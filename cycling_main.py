#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author:  tarney
@uid:     u7378856
@created: Sat Sep 18 16:24:21 2021
"""

import sys
from pathlib import Path

from cycling_check_dependencies import *

def suburb_demo(suburb, data):
    print()
    print('it stores all the geospatial data which allows a particular point,')
    print('given by a lat and long, to be located by suburb and district.')
    print('for example:')
    
    for station in data['rainfall']:
        name = data['rainfall'][station].get_station_name()
        print()
        print(f"Weather station '{name}' is located within:")
        
        lat = data['rainfall'][station].get_station_lat()
        long = data['rainfall'][station].get_station_long()
        located = suburb.locate(lat, long)
        
        for level, area in located.items():
            print(f"  {level.title()}: {area}")
        

def rainfall_demo(rainfall):
    print()
    print('it stores information such as:')
    station_id = rainfall.get_station_id()
    station_name = rainfall.get_station_name()
    station_lat = rainfall.get_station_lat()
    station_long = rainfall.get_station_long()
    station_height = rainfall.get_station_height()
    print(f'  station id: {station_id}')
    print(f'  station name: {station_name}')
    print(f'  station latitude: {station_lat}')
    print(f'  station longitude: {station_long}')
    print(f'  station height: {station_height}')
    
    print()
    print('it can also give you the distance to any lat and long')
    lat = -35.308056
    long = 149.124444
    print(f'for example, parliament house is at ({lat:.2f}, {long:.2f})')
    distance = rainfall.distance_from_station(lat, long)
    print(f'the distance from the station is: {distance:.2f}km')
    
    print()
    print('it also contains a pandas dataframe...')
    df = rainfall.get_data()
    
    dataframe_demo(df)

def dataframe_demo(df):
    print()
    
    rows, cols = df.shape
    print(f'the dataframe consists of {rows:,} rows and {cols} columns')
    
    columns = list(df.columns)
    print()
    print('its columns are:')
    for i, column in enumerate(columns):
        print(f'  {i+1}: {column}')
    
    if 'date_time' in df or 'lat' in df:
        print()
        print('of particular note:')
        if 'date_time' in df:
            print("  the column 'date_time' contains datetime objects")
            
        if 'lat' in df:
            print("  the columns 'lat' and 'long' contain floating point values")
            
    print()
    print("here's a sample of the data:")
    print()        
    print(df)

def data_demo(data):
    
    print()
    print('############################################################################')
    print('#                                DATA DEMO                                 #')
    print('############################################################################')
    
    import pandas as pd
    
    for key, value in data.items():
        print()
        
        if isinstance(value, pd.core.frame.DataFrame):
            line_length = len(key) + 8
            print(f"data['{key}']")
            print('-' * line_length)
            print("is a pandas dataframe")
            dataframe_demo(value)
            # tdf = value
            print()
        
        if isinstance(value, dict):
            for sub_key, sub_value in data[key].items():
                line_length = len(key) + len(sub_key) + 12
                print(f"data['{key}']['{sub_key}']")
                print('-' * line_length)
                print("is a Rainfall object")
                rainfall_demo(sub_value)
                print()
                
        if isinstance(value, Suburb):
            line_length = len(key) + 8
            print(f"data['{key}']")
            print('-' * line_length)
            print("is a Suburb object")
            suburb_demo(value, data)
            print()
    

##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':
    
    print()
    print('############################################################################')
    print('#                         CHECKING DEPENDENCIES                            #')
    print('############################################################################')
    print()  
    
    root_path = Path.cwd()
    local_module_prefix = 'cycling'
    sys_config = Dependencies(root_path, ignore_module_prefix=local_module_prefix)

    if sys_config.check():
        print(sys_config)
    else:
        print('Required modules missing, please install:')
        print()
        for i, module in enumerate(sys_config.get_missing_modules()):
            print(f'  {i + 1}: {module}')
        print()
        print('Once installed, please re-run the program.')
        sys.exit()
    
    
    ##########################################################################
    #    DEPENDENCIES MET, CAN NOW SAFELY IMPORT ALL ADDITIONAL MODULES      #
    ##########################################################################
    from cycling_globals import *
    from cycling_update_compatible_systems import *
    from cycling_download_data import *
    from cycling_load_data import *
    
    
    print()
    print('############################################################################')
    print('#                       UPDATING COMPATIBLE SYSTEMS                        #')
    print('############################################################################')
    print()  
       
    compatible_systems_csv = 'compatible_systems/compatible_systems.csv'
    requirements_doc_template = 'compatible_systems/REQUIREMENTS.template'
    requirements_doc = 'REQUIREMENTS.md'
    
    update_compatible_systems_csv(sys_config, compatible_systems_csv)
    update_requirements_doc(compatible_systems_csv, requirements_doc_template, requirements_doc)
    
    print()
    print('Please feel free to commit these files to the remote repository.')
    

    print()
    print('############################################################################')
    print('#                       CHECKING LOCAL DATA SOURCES                        #')
    print('############################################################################')
    print()  

    data_index_path = Path(DATA_FOLDER) / DATA_INDEX

    if not check_local_data(data_index_path):
        print()
        print('############################################################################')
        print('#                             DOWNLOADING DATA                             #')
        print('############################################################################')
        
        download_all_data(DATA_SOURCES, DATA_FOLDER, DATA_INDEX)
    else:
        print()
        print('All data sources found')

    
    print()
    print('############################################################################')
    print('#                               LOADING DATA                               #')
    print('############################################################################')
    print()  
    
    data = load_data(data_index_path)
    print()
    print('All data sources loaded')
    
    ##########################################################################
    #     CAN NOW PASS THE DATA TO THE ANALYSIS / VISUALISATION MODULES      #
    ##########################################################################
    
    data_demo(data)
    
    # print()
    # print('############################################################################')
    # print('#                                DATA DEMO                                 #')
    # print('############################################################################')
    
    # import pandas as pd
    
    # for key, value in data.items():
    #     print()
        
    #     if isinstance(value, pd.core.frame.DataFrame):
    #         line_length = len(key) + 8
    #         print(f"data['{key}']")
    #         print('-' * line_length)
    #         print("is a pandas dataframe")
    #         dataframe_demo(value)
    #         # tdf = value
    #         print()
        
    #     if isinstance(value, dict):
    #         for sub_key, sub_value in data[key].items():
    #             line_length = len(key) + len(sub_key) + 12
    #             print(f"data['{key}']['{sub_key}']")
    #             print('-' * line_length)
    #             print("is a Rainfall object")
    #             rainfall_demo(sub_value)
    #             print()
                
    #     if isinstance(value, Suburb):
    #         line_length = len(key) + 8
    #         print(f"data['{key}']")
    #         print('-' * line_length)
    #         print("is a Suburb object")
    #         suburb_demo(value, data)
    #         print()
    
    
    # for station in data['rainfall']:
    #     lat = data['rainfall'][station].get_station_lat()
    #     long = data['rainfall'][station].get_station_long()
        
    #     located = data['suburb'].locate(lat, long)
        
    #     name = data['rainfall'][station].get_station_name()
    #     print(f"Weather station '{name}' is located within:")
    #     for level, area in located.items():
    #         print(f"  {level.title()}: {area}")
    #     print()
            
    # distance = data['rainfall']['canberra airport'].distance_from_station(lat, long)
    
    # print(f'They are {distance:.2f} km apart')