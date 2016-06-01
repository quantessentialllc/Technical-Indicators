from django.shortcuts import render
# Create your views here.
import logging
import requests
import geocoder
import pandas as pd 
import datetime
from datetime import datetime
from django.http import HttpResponse
from slack_commands import settings
import numpy as np
import math
import matplotlib
matplotlib.rcParams['backend'] = "Qt4Agg"
import matplotlib.pyplot as plt
from matplotlib.dates import date2num    
from matplotlib.finance import candlestick_ohlc
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError

SYMBOL='SPX'
INTERVAL_SECONDS=3601 #1 hour
BOLLINGER_PERIOD=10 #10 interval_seconds periods (10 hours)
NUM_DAYS=15 #number of lookback days. Google Finance currently only supports 15 days



logger = logging.getLogger(__name__)

def validate_buy_params(request):
    #validate parameters here
    try: 
        parameter1 = request.data['parameter1']
    return parameter1, parameter2, etc

def get_intraday_data(symbol, interval_seconds=3601, num_days=15):
    import datetime #this is necessary i dont know why
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
        self.SHAPE = self.dataframe.shape[0] - 1
        self.STEP_SIZE = self.SHAPE/5
    #    #
    def plot_candlestick(self):
        #change datetime objects to date2num for candlestick
        marks = np.arange(0, self.SHAPE + self.STEP_SIZE, step=self.STEP_SIZE)
        marks = [math.floor(x) for x in marks]
        marks = marks[:5+1]
        date_marks = []
        for i in marks:
            datetime = list(self.dataframe['Datetime'])[i]
            date_marks.append(datetime.strftime('%m/%d %H:00'))
        self.dataframe['Datetime'] = np.arange(0, self.SHAPE + 1)
        tupled = [tuple(x) for x in self.dataframe.values]
        fig, ax = plt.subplots()
        candlestick_ohlc(ax, tupled, width= .4, colorup='g', alpha=.4)
        ax.set_xlim([0,self.SHAPE +1])
        ax.set_xticklabels(date_marks, rotation = 45)
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
    def post_plot(self):
        #code to save image and upload image URL to imgur
        #return image URL

@api_view(['POST'])
def post_image_url(request):
    try:
        parameter1, parameter2, parameter3= validate_buy_params(request)
    except ValidationError as error:
        return HttpResponse(error.message_dict, status=400)
    pulled_dataframe = get_intraday_data(SYMBOL, INTERVAL_SECONDS, NUM_DAYS)
    spx_dataframe = Stock_DataFrame(pulled_dataframe)
    spx_dataframe.plot_candlestick()
    spx_dataframe.plot_bollinger_bands(BOLLINGER_PERIOD)
    image_url = spx_dataframe.post_plot()
    return HttpResponse(image_url)







