import datetime
import pandas as pd
import requests
import numpy as np
import math
import psycopg2

SYMBOL = 'SPX'
INTERVAL_SECONDS=3601
def get_intraday_data(symbol, interval_seconds=61, num_days=15):
    """Hits Google Finance Website and creates a dataframe of historical prices"""
    import datetime
    print('pulling data from Google...')
    # Specify URL string based on function inputs.
    url_string = 'http://www.google.com/finance/getprices?q={0}'.format(symbol.upper())
    url_string += "&i={0}&p={1}d&f=d,o,h,l,c,v".format(interval_seconds,num_days)
    # Request the text, and split by each line
    r = requests.get(url_string).text.split()
    # Split each line by a comma, starting at the 8th line
    r = [line.split(',') for line in r[7:]]
    # Save data in Pandas DataFrame
    df = pd.DataFrame(r, columns=['Datetime','Close','High','Low','Open','Volume'])
    # Convert UNIX to Datetime format
    datetimed = [datetime.datetime.fromtimestamp(int(x[1:])) for x in list(df['Datetime'])]
    df['Datetime'] = datetimed
    #df['Datetime'] = df['Datetime'].apply(lambda x: datetime.datetime.fromtimestamp(int(x[1:])))
    cols = ['Datetime', 'Open', 'High', 'Low', 'Close']
    df = df[cols]
    for column_name in ['Open', 'High', 'Low', 'Close']:
    #converts above columns 
        df[column_name] = pd.to_numeric(df[column_name])
    return df

def create_connection():
	conn_string = "host='quantessential.cfpe5fdxx2fr.us-west-2.redshift.amazonaws.com' dbname='quantessential' user='stacsy483' password='ADD20mg!'"
	connection = psycopg2.connect(conn_string)
	return connection

def pull_last_date(connection):
	""""Pulls the last time recorded time in the underlying table"""
	query = 'SELECT MAX(datetime) from underlying2'
	pull = pd.read_sql_query(query, connection)['max'][0]
	print('last date in db: ' + pull)
	return pull 

def parse_intraday_data(intraday_dataframe, last_time_in_db):	    
	"""Takes intraday dataframe and delete any entries that already exist in the underlying table"""
	sliced_dataframe = intraday_dataframe[intraday_dataframe['Datetime'] > last_time_in_db]
	sliced_dataframe = 	sliced_dataframe.reset_index()
	try:
		del sliced_dataframe['index']
	except:
		pass
	print(str(sliced_dataframe.shape[0]) + ' new datapoints detected.')
	return sliced_dataframe


def update_db(connection, intraday_dataframe):
	cursor = connection.cursor()
	dict_records = intraday_dataframe.to_dict('records')
	count = 0
	for row in dict_records:
		datetime = row['Datetime']
		close = row['Close']
		high = row['High']
		low = row['Low']
		opened = row['Open']
		query = "INSERT INTO underlying2 (datetime, close_price, high_price, low_price, open_price) VALUES (%s, %s, %s, %s, %s);"
		data = (datetime, close, high, low, opened)
		cursor.execute(query, data)
		count +=1
	connection.commit()	
	print(str(count) + ' Rows Added.')

def main():
	intraday_raw = get_intraday_data(SYMBOL)
	connection = create_connection()
	last_date = pull_last_date(connection)
	parsed_intraday = parse_intraday_data(intraday_raw, last_date)
	update_db(connection, parsed_intraday)

if __name__=='__main__':
    main()
