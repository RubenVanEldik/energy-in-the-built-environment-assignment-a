# -*- coding: utf-8 -*-## importing libaries and filesimport pandas as pdimport datetime as dtimport pvlib as pvraw_data = pd.read_csv('../input/Irradiance_2015_UPOT.csv',                        sep= ';',                       index_col= 'timestamp',                       parse_dates= True)## preparing dataframeraw_data.index.names = ['Date and time']print ("hello world")