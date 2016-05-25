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




















#Bollinger Bands  
def BBANDS(df, n):  
    MA = pd.Series(pd.rolling_mean(df['Close'], n))  
    MSD = pd.Series(pd.rolling_std(df['Close'], n))  
    b1 = MA + 2 * MSD
    B1 = pd.Series(b1, name = 'BollingerB_' + str(n))  
    df = df.join(B1)  
    b2 = MA - 2 * MSD
    B2 = pd.Series(b2, name = 'Bollinger%b_' + str(n))  
    df = df.join(B2)  
    return df

import plotly.plotly as py
from plotly.tools import FigureFactory as FF
from datetime import datetime

import pandas.io.data as web
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import plotly.graph_objs as go


def plot_candlestick(dataframe):


#subset is a pandas dataframe
tuples = [tuple(x) for x in subset.values]


def plot_candlestick(dataframe):


#!/usr/bin/env python
import matplotlib.pyplot as plt
plt.style.use('ggplot')
matplotlib.use('TkAgg')
from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc

# (Year, month, day) tuples suffice as args for quotes_historical_yahoo
date1 = (2004, 2, 1)
date2 = (2004, 4, 12)


mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays = DayLocator()              # minor ticks on the days
weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
dayFormatter = DateFormatter('%d')      # e.g., 12

quotes = quotes_historical_yahoo_ohlc('INTC', date1, date2)
if len(quotes) == 0:
    raise SystemExit

trace = 


fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_minor_locator(alldays)
ax.xaxis.set_major_formatter(weekFormatter)
#ax.xaxis.set_minor_formatter(dayFormatter)

#plot_day_summary(ax, quotes, ticksize=3)
candlestick_ohlc(ax, quotes, width=0.6, colorup='g', alpha=.4)

ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

plt.show()

# Create Line of open values
add_line = Scatter(
    x=df.index,
    y=df.Open,
    name= 'Open Vals',
    line=Line(color='black')
    )

fig['data'].extend([add_line])
py.iplot(fig, filename='candlestick_and_trace', validate=False)



# data in a text file, 5 columns: time, opening, close, high, low
# note that I'm using the time you formated into an ordinal float

# determine number of days and create a list of those days
ndays = np.unique(np.trunc(data[:,0]), return_index=True)
xdays =  []
for n in np.arange(len(ndays[0])):
    xdays.append(datetime.date.isoformat(num2date(data[ndays[1],0][n])))

# creation of new data by replacing the time array with equally spaced values.
# this will allow to remove the gap between the days, when plotting the data
data2 = np.hstack([np.arange(data[:,0].size)[:, np.newaxis], data[:,1:]])

# plot the data
fig = plt.figure(figsize=(10, 5))
ax = fig.add_axes([0.1, 0.2, 0.85, 0.7])
    # customization of the axis
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.tick_params(axis='both', direction='out', width=2, length=8,
               labelsize=12, pad=8)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)
    # set the ticks of the x axis only when starting a new day
ax.set_xticks(data2[ndays[1],0])
ax.set_xticklabels(xdays, rotation=45, horizontalalignment='right')

ax.set_ylabel('Quote ($)', size=20)
ax.set_ylim([177, 196])

candlestick(ax, data2, width=0.5, colorup='g', colordown='r')

plt.show()



start = dt.datetime(2015, 7, 1)
data = pd.io.data.DataReader('AAPL', 'yahoo', start)
data = data.reset_index()
data['Date2'] = data['Date'].apply(lambda d: mdates.date2num(d.to_pydatetime()))
tuples = [tuple(x) for x in data[['Date2','Open','High','Low','Close']].values]

fig, ax = plt.subplots()
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel("Price")
plt.title("AAPL")
candlestick_ohlc(ax, tuples, width=.6, colorup='g', alpha =.4);





