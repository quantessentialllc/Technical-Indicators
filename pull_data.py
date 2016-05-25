import datetime
import pandas as pd
import pandas_datareader.data as web
import requests
import numpy as np
import math
import matplotlib
matplotlib.rcParams['backend'] = "Qt4Agg"
import matplotlib.pyplot as plt
from matplotlib.dates import date2num    


SYMBOL = 'SPX'
def get_intraday_data(symbol, interval_seconds=3601, num_days=15):
	import datetime
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
        df[column_name] = pd.to_numeric(df[column_name])
    return df


class Stock_DataFrame(object):
	def __init__(self, dataframe):
		self.dataframe = dataframe
		self.SHAPE = 104
		self.STEP_SIZE = 104/5
	#    #
	def plot_candlestick(self):
		#change datetime objects to date2num for candlestick
		marks = np.arange(0, self.SHAPE + self.STEP_SIZE, step=self.STEP_SIZE)
		marks = [math.floor(x) for x in marks]
		date_marks = []
		for i in marks:
			datetime = list(test['Datetime'])[i]
			date_marks.append(datetime.strftime('%m/%d %H:00'))
		self.dataframe['Datetime'] = np.arange(0, self.SHAPE + 1)
		tupled = [tuple(x) for x in self.dataframe.values]
		fig, ax = plt.subplots()
		candlestick_ohlc(ax, tupled, width= .4, colorup='g', alpha=.4)
		ax.set_xlim([0,self.SHAPE +1])
		ax.set_xticklabels(date_marks, rotation = 45)
		print ('Plotting Candlestick')
	def plot_bollinger_bands(self, n):
		MA = pd.Series(pd.rolling_mean(df['Close'], n))  
		MSD = pd.Series(pd.rolling_std(df['Close'], n))  
		b1 = MA + 2 * MSD
		b2 = MA - 2 * MSD
		fake_x = np.arange(0, self.SHAPE + 1)
		plt.plot(fake_x, b1, color='k', label='Bollinger Band with Period {}'.format(str(n)) )
		plt.plot(fake_x, b2, color='k')
		print('Plotting Bollinger Bands with Period {}'.format(str(n)))
	def show_plot(self):
		plt.show()













