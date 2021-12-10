import numpy as np
import matplotlib.pyplot as plt
import requests
import urllib
import json
import datetime
from dateutil.relativedelta import relativedelta

class crypto:
    def __init__(self, id, slug, symbol, currentValue):
        self.id = id
        self.slug = slug
        self.symbol = symbol
        self.currentValue = currentValue

def makeCryptoList():
    url = "https://data.messari.io/api/v1/assets?fields=id,slug,symbol,metrics/market_data/price_usd"
    data = urllib.request.urlopen(url).read()
    cryptoList = json.loads(data.decode('utf-8'))['data']
    finalList = []
    for element in cryptoList:
        finalList.append(crypto(element['id'], element['slug'], element['symbol'], element['metrics']['market_data']['price_usd']))
        
    return finalList

def makeTimeSeriesString(slug, startYear, startMonth, startDay, endYear, endMonth, endDay):
    startDate = datetime.datetime(startYear, startMonth, startDay)
    endDate = datetime.datetime(endYear, endMonth, endDay)
    
    startStr = startDate.strftime('%Y/%m/%d')
    endStr = endDate.strftime('%Y/%m/%d')
    return "https://data.messari.io/api/v1/assets/" + slug +  "/metrics/price/time-series?start=" + startStr + "&end=" + endStr \
    + "&interval=1d"

def makeGraph(slug, numOfMonths, indexOfSetting):
    #note: for indexOfSetting 1: open, 2: high, 3:low, 4:close, 5:volume
    startDate = datetime.datetime.now() - relativedelta(months=numOfMonths)
    url = makeTimeSeriesString(slug, startDate.year, startDate.month, startDate.day, datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    
    dataStr = urllib.request.urlopen(url).read()
    time_series = json.loads(dataStr.decode('utf-8'))
    raw_timeseries = time_series['data']['values']
    if raw_timeseries == None:
        return None, None
    
    x = []
    y = []
    
    for record in raw_timeseries:
        timestampInSec = int(record[0])/1000 #converts from milliseconds to seconds
        curr_date = datetime.datetime.utcfromtimestamp(timestampInSec)
        price = record[indexOfSetting]
        
        x.append(curr_date)
        y.append(price)
    
    return x,y