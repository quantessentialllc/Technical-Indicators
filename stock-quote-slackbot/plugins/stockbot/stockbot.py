import random
import time
import re
import yaml
from slackclient import SlackClient
import datetime
import pandas as pd
import requests
import numpy as np
import math
import matplotlib
import psycopg2
matplotlib.use('Agg')
#matplotlib.rcParams['backend'] = "Qt4Agg"
import matplotlib.pyplot as plt
from matplotlib.dates import date2num    
from matplotlib.finance import candlestick_ohlc
from boto.s3.connection import S3Connection
import boto
from boto.s3.key import Key
import uuid

LIST_OF_TECHNICAL_INDICATORS=['bollinger']

crontable = []
outputs = []

config = yaml.load(open('rtmbot.conf', 'r'))
trig_word = config["TRIGGER_WORD"].lower()
AWS_KEY = config["AWS_KEY"]
AWS_SECRET = config["AWS_SECRET"]

def process_message(data):
    """Process a message entered by a user
    If the message has either the trigger word or "range", 
    evaluate it and respond accordingly with the stock info 
    or average price over the range

    data -- the message's data
    """
    message = data["text"].lower()
    first_word = message.split()[0].lower()
    
    print(data);
    # Look for trigger word, remove it, and look up each word
    if trig_word == first_word:
        print(message)
        #Second word will be the technical indicator 
        #Right now only bollinger
        second_word = message.split(" ")[1].lower()
        #Third word is the candlestick width
        #Right now only hourly or daily
        third_word = message.split(" ")[2].lower()
        #Fourth word is the # of Periods as an Integer. i.e. 10
        try:
            fourth_word = int(message.split(" ")[3])
        except:
            outputs.append([data['channel'], 'Please enter an integer for # of Periods'])
        if third_word not in ['hourly', 'daily']:
            outputs.append([data['channel'], 'Please specify Candlestick Period as Hourly or Daily'])
        else:
            stock_df = create_dataframe(third_word)
            if second_word not in LIST_OF_TECHNICAL_INDICATORS:
                outputs.append([data['channel'], 'Please select one of following: ' + ",".join(LIST_OF_TECHNICAL_INDICATORS)])
            else:
                stock_df.plot_candlestick()
                stock_df.plot_bollinger_bands(fourth_word)
                url = stock_df.upload_to_aws()
                print(url)
                outputs.append([data['channel'], url])


def create_connection():
    """Initiates connection to underlying table in database"""
    conn_string = "host='quantessential.cfpe5fdxx2fr.us-west-2.redshift.amazonaws.com' dbname='quantessential' user='stacsy483' password='ADD20mg!'"
    connection = psycopg2.connect(conn_string)
    return connection

def summarize_dataframe(pulled_dataframe, how='hourly'):
    """Re-aggregates OHLC (Open, High, Low, Close) minutely data

    how - currently can be aggregated to Hourly or Daily"""
    raw_datetimes = list(pulled_dataframe['datetime'])
    if how == 'hourly':
        grouped_datetimes = [x.strftime('%Y-%m-%d %H:00') for x in raw_datetimes]
    elif how =='daily':
        grouped_datetimes = [x.strftime('%Y-%m-%d') for x in raw_datetimes]
    new_dataframe = pulled_dataframe
    new_dataframe['datetime'] = grouped_datetimes
    aggregated = new_dataframe.groupby('datetime').agg({
        'open_price': 'first',
        'low_price' : min,
        'high_price': max,
        'close_price': 'last'
        })
    datetimes = list(aggregated.index)
    aggregated['datetime'] = datetimes
    column_order = ['datetime', 'open_price', 'high_price', 'low_price', 'close_price']
    aggregated = aggregated[column_order]
    aggregated.columns = ['datetime','Open', 'High', 'Low', 'Close']
    return aggregated

class Stock_DataFrame(object):
    """Object to plot various Technical Indicators
        Base figure is candlestick charts
        Uploads to S3 and returns the url
    """
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.SHAPE = self.dataframe.shape[0] - 1
        self.STEP_SIZE = self.SHAPE/6
        self.minimum = min(self.dataframe['Low'])
        self.maximum =  max(self.dataframe['High'])
    
    def plot_candlestick(self):
        marks = np.arange(0, self.SHAPE + self.STEP_SIZE, step=self.STEP_SIZE)
        marks = [int(math.floor(x)) for x in marks]
        marks = marks[:6+1]
        date_marks = []
        for i in marks:
            datetime = list(self.dataframe['datetime'])[i]
            date_marks.append(datetime)
        self.dataframe['datetime'] = np.arange(0, self.SHAPE + 1)
        tupled = [tuple(x) for x in self.dataframe.values]
        fig, ax = plt.subplots()    
        candlestick_ohlc(ax, tupled, width= .4, colorup='g', alpha=.4)
        ax.set_ylim([self.minimum - 10, self.maximum + 10])
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
    def upload_to_aws(self):
        plt.savefig('testing.png')
        plt.close()
        conn = S3Connection(AWS_KEY, AWS_SECRET)
        bucket = conn.get_bucket('quantessential-underlying')
        upload_file = open('testing.png')
        bucket_key = Key(bucket)
        bucket_key.key=str(uuid.uuid4()) + '.png'
        print('uploading to S3...')
        bucket_key.set_contents_from_filename('testing.png')
        bucket_key.make_public()    
        url = bucket_key.generate_url(expires_in=0, query_auth=False)
        return url                

def create_dataframe(how='hourly'):
    """Returns stock dataframe object to be manipulated"""
    connection = create_connection()
    pull = pd.read_sql_query("SELECT * from underlying", connection)
    aggregated = summarize_dataframe(pull, how)
    stock_df = Stock_DataFrame(aggregated)
    return stock_df


