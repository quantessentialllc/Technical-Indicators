import datetime
import pandas as pd
import requests
import numpy as np
import math
import matplotlib
import psycopg2
matplotlib.use('Agg')
matplotlib.rcParams['backend'] = "Qt4Agg"
import matplotlib.pyplot as plt
from matplotlib.dates import date2num    
from matplotlib.finance import candlestick_ohlc
from boto.s3.connection import S3Connection
import boto
from boto.s3.key import Key

SLACK_TOKEN='xoxb-51362182401-RB3eWRs4u3xdXEyGBubNBc83'
AWS_KEY='AKIAJ45LIVBDUEVII33A'
AWS_SECRET='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'


def create_connection():
	conn_string = "host='quantessential.cfpe5fdxx2fr.us-west-2.redshift.amazonaws.com' dbname='quantessential' user='stacsy483' password='ADD20mg!'"
	connection = psycopg2.connect(conn_string)
	return connection

def summarize_dataframe(pulled_dataframe, how='Hourly'):
	raw_datetimes = list(pulled_dataframe['datetime'])
	if how == 'Hourly':
		grouped_datetimes = [x.strftime('%Y-%m-%d %H:00') for x in raw_datetimes]
	elif how =='Daily':
		grouped_datetimes = [x.strftime('%Y-%m-%d') for x in raw_datetimes]
	new_dataframe = pulled_dataframe
	new_dataframe['datetime'] = grouped_datetimes
	aggregated = new_dataframe.groupby('datetime').agg({
		'open_price': 'first',
		'low_price' : min,
		'high_price': max,
		'close_price': 'last'
		})
	column_order =  ['open_price', 'high_price', 'low_price', 'close_price']
	aggregated = aggregated[column_order]
	aggregated.columns = ['Open', 'High', 'Low', 'Close']
	aggregated = aggregated.reset_index()
	return aggregated


class Stock_DataFrame(object):
	def __init__(self, dataframe):
		self.dataframe = dataframe
		self.SHAPE = self.dataframe.shape[0] - 1
		self.STEP_SIZE = self.SHAPE/6
		self.minimum = min(self.dataframe['Low'])
		self.maximum =  max(self.dataframe['High'])
	#    #
	def plot_candlestick(self):
		#change datetime objects to date2num for candlestick
		marks = np.arange(0, self.SHAPE + self.STEP_SIZE, step=self.STEP_SIZE)
		marks = [int(math.floor(x)) for x in marks]
		marks = marks[:5+1]
		date_marks = []
		for i in marks:
			datetime = list(self.dataframe['datetime'])[i]
			date_marks.append(datetime)
		self.dataframe['datetime'] = np.arange(0, self.SHAPE + 1)
		tupled = [tuple(x) for x in self.dataframe.values]
		ax = plt.subplot(211)	
		candlestick_ohlc(ax, tupled, width= .4, colorup='g', alpha=.4)
		ax.set_ylim([self.minimum - 10, self.maximum + 10])
		ax.set_xlim([0,self.SHAPE +1])
		ax.set_xticklabels(date_marks, rotation = 45)
		plt.subplot(212)
		rsis = self.rsi(self.dataframe)
		x_values = np.arange(0, self.SHAPE + 1)
		plt.plot(x_values, rsis)
		plt.show()
		print ('Plotting Candlestick')
	def plot_bollinger_bands(self, n):
		MA = pd.Series(pd.rolling_mean(self.dataframe['Close'], n))  
		MSD = pd.Series(pd.rolling_std(self.dataframe['Close'], n))  
		b1 = MA + 2 * MSD
		b2 = MA - 2 * MSD
		fake_x = np.arange(0, self.SHAPE + 1)
		plt.plot(fake_x, b1, color='k', label='Bollinger Band with Period {}'.format(str(n)) )
		plt.plot(fake_x, b2, color='k')
		print('Plotting Bollinger Bands with Period {}'.format(str(n)))
	def rsi(self, dataframe, period=14):
		i = 0
		UpI = [0]
		DoI = [0]
		while i + 1 <= dataframe.shape[0] - 1:
			UpMove = dataframe.get_value(i + 1, 'High') - dataframe.get_value(i, 'High')
			DoMove = dataframe.get_value(i, 'Low') - dataframe.get_value(i + 1, 'Low')
			if UpMove > DoMove and UpMove > 0:
				UpD = UpMove
			else:
				UpD = 0
			UpI.append(UpD)
			if DoMove > UpMove and DoMove > 0:
				DoD = DoMove
			else:
				DoD = 0
			DoI.append(DoD)
			i +=1 
		UpI = pd.Series(UpI)
		DoI = pd.Series(DoI)
		PosDI = pd.Series(pd.ewma(UpI, span = period, min_periods = period - 1))
		NegDI = pd.Series(pd.ewma(DoI, span = period, min_periods = period -1))
		RSI = pd.Series(PosDI / (PosDI + NegDI), name = 'RSI_' + str(period))
		return RSI
	def upload_to_aws(self):
		plt.savefig('testing.png')
		conn = S3Connection(AWS_KEY, AWS_SECRET)
		bucket = conn.get_bucket('quantessential-underlying')
		upload_file = open('testing.png')
		bucket_key = Key(bucket)
		bucket_key.key='testing2.png'
		print('uploading to S3...')
		bucket_key.set_contents_from_filename('testing.png')	
		url = bucket_key.generate_url(expires_in=0, query_auth=False)
		print(url)
		return url

def create_dataframe():
	connection = create_connection()
	pull = pd.read_sql_query("SELECT * from underlying", connection)
	aggregated = summarize_dataframe(pull, 'Hourly')
	stock_df = Stock_DataFrame(aggregated)
	return stock_df

def main():
	stock_df = create_dataframe()
	stock_df.plot_candlestick()
	stock_df.plot_bollinger_bands(10)
	stock_df.upload_to_aws()


if __name__=="__main__":
	main()	



