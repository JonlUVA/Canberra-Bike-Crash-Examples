#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author:  tarney
@uid:     u7378856
@created: Thu Sep 16 23:00:25 2021
"""

import csv
import pandas as pd
from pathlib import Path
from math import radians, cos, sin, asin, sqrt
import shapefile

from shapely.geometry import shape, Point #, Polygon
# from datetime import datetime

from cycling_globals import *

def clean_column_name(column_name):
    """
    Normalises a colummn name by removing any superfluous whitespace, converting
    spaces to underscores, and converting to lower case.

    Parameters
    ----------
    column_name : str
        The column name to be normalised.

    Returns
    -------
    column_name : str
        The normalised column name.

    """
    
    word_list = column_name.split()
    word_list = [word.strip().lower() for word in word_list]
    column_name = '_'.join(word_list)
    
    return column_name


def read_data_directory_csv(csv_file_name):
    """
    Reads a CSV file containing details of the local data sources and returns
    a list of elements, one per data source, where each element is a dictionary
    keyed by column header.
    
    Expected CSV format is:
        
        type  | description | format |  url  |  backup_url | path
        ----------------------------------------------------------
        (str) |    (str)    |  (str) | (str) |    (str)    | (str)
        
    Which is mapped to:
        
        {'type': (str), 'description': (str), 'format': (str), 
         'url': (str), 'backup_url': (str), 'path': (str)}

    Parameters
    ----------
    csv_file_name : str
        Path of the CSV file to read.

    Returns
    -------
    list of dict
        As detailed above, with key-value pairs being:
            type : a classification of the data
            description : a descriptor to distinguish multiple sources of the 
                          same type
            format : the file extension of data source to identify
            url : the source url of the data
            backup url : a mirror link should the initial download fail
            path : the local path to the data file, relative to the project root.

    """
    
    data_source_path = Path(csv_file_name)
    
    if not data_source_path.is_file():
        return []
    
    data_sources= []
    
    with open(data_source_path, encoding='utf-8-sig') as fin:
        csv_reader = csv.DictReader(fin)
        
        for row in csv_reader:
            data_sources.append(row)
        
    return data_sources


def read_csv_into_df(csv_file, date_time_cols=None, lat_long_cols=None):
    file_path = Path(csv_file)
    
    # 11/23/2017 1:00:00 AM
    # mydateparser = lambda x: datetime.strptime(x, "%m/%d/%Y %I:%M:%S %p")
    
    if date_time_cols:
        if isinstance(date_time_cols, str):
            date_time_cols = [date_time_cols]
            
        parse_dates_dict = {'date_time': date_time_cols}
        
        df = pd.read_csv(file_path, parse_dates=parse_dates_dict)
        # df = pd.read_csv(file_path, parse_dates=[date_time_cols])
        
        # if isinstance(date_time_cols, list):
            
        
        # df = pd.read_csv(file_path, parse_dates=[date_time_cols], date_parser=mydateparser)
    else:
        # df = pd.read_csv(file_path, date_parser=mydateparser)
        df = pd.read_csv(file_path)
        
    if lat_long_cols:
        if isinstance(lat_long_cols, str):
            df[['lat', 'long']] = df[lat_long_cols].str.strip('()') \
                                            .str.split(', ', expand=True) \
                                            .astype('float64') \
                                            .rename(columns={0:'lat', 1:'long'})
            df.drop(lat_long_cols, axis=1, inplace=True)
        else:
            df.rename(columns={lat_long_cols[0]: 'lat', lat_long_cols[1]: 'long'}, inplace=True)
                                                       
    columns = [clean_column_name(column) for column in df.columns]
    df.columns = columns
    
    return df


def parse_field_params(field_params):
    if not field_params:
        return None
    elif field_params.find(';') >= 0:
        return field_params.split(';')
    else:
        return field_params
    

def check_local_data(data_index_csv):
    data_index = read_data_directory_csv(data_index_csv)
    
    print(f'Checking data index: {data_index_csv} ...', end=' ')
    if not data_index:
        print('NOT FOUND')
        return False
    else:
        print('found')
        
    max_width = 0
    for data_source in data_index:
        if len(data_source['path']) > max_width:
            max_width = len(data_source['path'])
    
    all_found = True
    
    print('')
    print('Checking data sources:')
    for data_source in data_index:
        path = Path(data_source['path'])
        padding = '.' * (max_width - len(data_source['path']) + 3)
        
        print(f'  {path} {padding}', end=' ')
        
        if path.is_file():
            print('found')
        else:
            print('NOT FOUND')
            all_found = False
            
    return all_found
        
    
    

# data_directory_file = 'data/local_data.csv'



# crash_path = Path(data_dir[0]['path'])

# df = pd.read_csv(crash_path, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])

# columns = [clean_column_name(column) for column in df.columns]

# df.columns = columns

# df['crash_date'] = pd.to_datetime(df['crash_date'])

# df.drop('location_1', axis=1, inplace=True)

# data_types = {'crash_date_crash_time': 'datetime64[ns]',
#               'crash_id': 'int64',
#               'severity': 'str',
#               'crash_type': 'str',
#               'cyclists': 'int64',
#               'cyclist_casualties': 'int64',
#               'reported_location': 'str',
#               'latitude': 'float64',
#               'longitude': 'float64',
#               'location_1': 'str'}

class Rainfall:
    def __init__(self, index_listing, data_frame):
        self.df = data_frame
        self._read_rainfall_data_notes(index_listing)
    
    def _isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _read_rainfall_data_notes(self, index_listing):
        data_file = index_listing['path']
        notes_file = data_file.replace('Data.csv', 'Note.txt')
        
        notes_path = Path(notes_file)
        
        if not notes_path.is_file():
            print(f'File not found: {notes_path}')
            return False
        
        self.station = {}
        
        search_strings = {'Bureau of Meteorology station number': 'id',
                          'Station name': 'name',
                          'Latitude': 'lat',
                          'Longitude': 'long',
                          'Height': 'height'}
        
        all_attributes_found = False
        
        with open(notes_path) as fin:
            for line in fin:
                for search_string, attribute in search_strings.items():
                    if line.strip().lower().startswith(search_string.lower()):
                        words = line.split(':')
                        value = words[-1].strip()
                        
                        if Rainfall._isfloat(value):
                            value = float(value)
                            
                            if int(value) == value:
                                value = int(value)
                                
                        self.station[attribute] = value
                        
                        if len(self.station) == len(search_strings):
                            all_attributes_found = True
                            break
                        
                if all_attributes_found:
                    break
    
        return all_attributes_found
    
    def get_data(self):
        if 'id' in self.station:
            return self.df
    
    def get_station_id(self):
        if 'id' in self.station:
            return self.station['id']
   
    def get_station_name(self):
        if 'name' in self.station:
            return self.station['name']
    
    def get_station_lat(self):
        if 'lat' in self.station:
            return self.station['lat']
    
    def get_station_long(self):
        if 'long' in self.station:
            return self.station['long']
    
    def get_station_lat_long(self):
        if 'lat' in self.station and 'long' in self.station:
            return (self.station['lat'], self.station['long'])
    
    def get_station_long_lat(self):
        if 'lat' in self.station and 'long' in self.station:
            return (self.station['long'], self.station['lat'])
        
    def get_station_height(self):
        if 'height' in self.station:
            return self.station['height']
    
    def distance_from_station(self, lat2, lon2):
        if not 'lat' in self.station or not 'long' in self.station:
            return
    
        R = 6371 # km
        
        lat1 = self.station['lat']
        lon1 = self.station['long']
        
        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        lat1 = radians(lat1)
        lat2 = radians(lat2)
  
        a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
        c = 2*asin(sqrt(a))
  
        distance = R * c
        
        return distance
        

class Suburb:
    level_map = {'Gazetted Locality': 'suburb',
                 'District': 'district'}
    
    def __init__(self, data_path):
        sf = shapefile.Reader(data_path)
        self.shapes = sf.shapes()
        self.records = sf.records()
        
    def locate(self, lat, long):
        point = Point(long, lat)
        res = {}
        
        for i, this_shape in enumerate(self.shapes):
            boundary = shape(this_shape)
        
            if point.within(boundary):
                name = self.records[i][3]
                level = self.records[i][4]
                res[Suburb.level_map[level]] = name
                
        return res
                
     
def load_data(data_index_path):
    data_index = read_data_directory_csv(data_index_path)
    data = {}
    
    max_width = 0
    for data_source in data_index:
        if len(data_source['path']) > max_width:
            max_width = len(data_source['path'])
    print('Reading data:')
    
    for data_source in data_index:
        data_path = data_source['path']
        data_type = data_source['type']
        data_description = data_source['description']
        data_format = data_source['format']
        
        date_time = parse_field_params(data_source['date_time_fields'])
        lat_long = parse_field_params(data_source['lat_long_fields'])
        
        padding = '.' * (max_width - len(data_source['path']) + 3)
        print(f'  {data_path} {padding}', end=' ')
        
        if data_format.lower() == 'csv':
            data_content = read_csv_into_df(data_path, date_time_cols=date_time, lat_long_cols=lat_long)
        elif data_format.lower() == 'shp':
            data_content = Suburb(data_path)     
        else:
            continue    
            
        if data_type.lower() == 'rainfall':
            data_content = Rainfall(data_source, data_content)
        
        if data_description:
            if data_type in data:
                data[data_type][data_description] = data_content
            else:
                data[data_type] = {data_description: data_content}
        else:
            data[data_type] = data_content
            
        print('loaded')
        
    return data
     
if __name__ == '__main__':             
        
    data_directory_path = Path(DATA_FOLDER) / DATA_INDEX
    data_index = read_data_directory_csv(data_directory_path)
    data = {}
    
    for data_source in data_index:
        data_path = data_source['path']
        data_type = data_source['type']
        data_description = data_source['description']
        data_format = data_source['format']
        
        date_time = parse_field_params(data_source['date_time_fields'])
        lat_long = parse_field_params(data_source['lat_long_fields'])
        
        if data_format.lower() == 'csv':
            data_content = read_csv_into_df(data_path, date_time_cols=date_time, lat_long_cols=lat_long)
        elif data_format.lower() == 'shp':
            data_content = Suburb(data_path)     
        else:
            continue    
            
        if data_type.lower() == 'rainfall':
            data_content = Rainfall(data_source, data_content)
        
        if data_description:
            if data_type in data:
                data[data_type][data_description] = data_content
            else:
                data[data_type] = {data_description: data_content}
        else:
            data[data_type] = data_content
        
    
    ## SHAPE DEMO
    
    # all_shapes = data['suburb boundary'].shapes()
    # all_records = data['suburb boundary'].records()   
     
    # for station in data['rainfall']:
    #     station_location = Point(data['rainfall'][station].get_station_long_lat())
    #     station_name = data['rainfall'][station].get_station_name()
        
    #     for i, this_shape in enumerate(all_shapes):
    #         boundary = shape(this_shape)
            
    #         if station_location.within(boundary):
    #             locality_name = all_records[i][3]
    #             locality_level = all_records[i][4]
    #             print(f"Rainfall station '{station_name}' is located within the {locality_level} {locality_name}")
    
    print()
    
    for station in data['rainfall']:
        lat = data['rainfall'][station].get_station_lat()
        long = data['rainfall'][station].get_station_long()
        
        located = data['suburb'].locate(lat, long)
        
        name = data['rainfall'][station].get_station_name()
        print(f"Weather station '{name}' is located within:")
        for level, area in located.items():
            print(f"  {level.title()}: {area}")
        print()
            
    distance = data['rainfall']['canberra airport'].distance_from_station(lat, long)
    
    print(f'They are {distance:.2f} km apart')