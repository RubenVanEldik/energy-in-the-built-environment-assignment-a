#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 14:06:46 2021

@author: rajesh, ruben, erik, kevan, marita
"""
#Preparing KNMI data for station:
# STN         LON(east)   LAT(north)  ALT(m)      NAME
# 270         5.752       53.224      1.20        Leeuwarden 

import pandas as pd

to_skip_lines = range(0, 10)


data = pd.read_csv('../input/KNMI_2019_hourly.txt', skiprows=to_skip_lines)
del data['# STN'] #delere station column
data.columns = ['date', 'HH', 'wind', 'temp', 'GHI']
#print(data)

#fix date-time index
data.date = data.date.astype(str)
data.HH = data.HH.apply( lambda x : str(x).zfill(2) )
data.HH = data.HH.replace('24', '00')
data['datetime'] = data.date + data.HH + '00'
data['datetime'] = pd.to_datetime(data.datetime, format= '%Y%m%d%H%M')

data.index = data.datetime
data = data[['wind', 'temp', 'GHI']]

#fix GHI units from GHI (j/cm2 to kw/m2) , temperature & wind (0.1 to 1)
data.GHI = data.GHI * 2.77778
data.wind = data.wind/10
data.temp = data.temp/10

#fix timezone UTC
data.index = data.index.tz_localize('UTC')

#export to new csv

data.to_csv('../input/csvdata_KNMI_2019_hourly.csv', sep = ";")
#newdata = pd.read_csv('../input/csvdata_KNMI_2019_hourly.csv', sep = ";")