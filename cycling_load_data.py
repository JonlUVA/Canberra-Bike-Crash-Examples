#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides tools to examine a CSV index of local data sources, 
parse each into the appropriate data structure with additional data cleaning,
normalisation, and typing, and bundle them into a dictionary.

Relevant fields in the CSV index are:
    
    type | description | format | date_time_fields | lat_long_fields | path
    -----+-------------+--------+------------------+------------------------
    (str)|     (str)   |  (str) |      (str)       |       (str)     | (str)

Where values are:
    
    type  : a classification of the data, is the primary key in the resultant 
            dictionary
    description : a descriptor to distinguish multiple sources of the same type, 
                  if used provides the key of a nested dictionary
    format : the file extension of the data source to help determine how it 
             should be processed
    date_time_fields : a semi-colon separated list of columns names for any 
                      datetime fields in the data source
    lat_long_fields : a semi-colon separated list of columns names for any 
                      latitude and longitude fields in the data source
    path : the path to the data source

The index can be automatically generated by the 'cycling_download_data' module.

@author:  tarney
@uid:     u7378856
@created: Thu Sep 16 23:00:25 2021
"""

import csv
import pandas as pd
from pathlib import Path
from math import radians, cos, sin, asin, sqrt
import shapefile
from shapely.geometry import shape, Point
from collections import defaultdict
import json

from cycling_globals import *


##############################################################################
#                               HELPER FUNCTIONS                             #
##############################################################################

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


def read_data_index_csv(csv_file_name):
    """
    Reads a CSV file containing details of the local data sources and returns
    a list of elements, one per data source, where each element is a dictionary
    keyed by column header.
    
    Expected CSV format is:
        
    type | description | format | date_time_fields | lat_long_fields | path
    -----+-------------+--------+------------------+------------------------
    (str)|     (str)   |  (str) |      (str)       |       (str)     | (str)
        
    Which is mapped to:
        
        {'type': (str), 'description': (str), 'format': (str), 
         'date_time_fields': (str), 'lat_long_fields': (str), 'path': (str)}

    Parameters
    ----------
    csv_file_name : str
        Path of the CSV file to read.

    Returns
    -------
    list of dict
        As detailed above, with key-value pairs being:
        type  : a classification of the data, is the primary key in the resultant 
                dictionary
        description : a descriptor to distinguish multiple sources of the same type, 
                      if used provides the key of a nested dictionary
        format : the file extension of the data source to help determine how it 
                 should be processed
        date_time_fields : a semi-colon separated list of columns names for any 
                          datetime fields in the data source
        lat_long_fields : a semi-colon separated list of columns names for any 
                          latitude and longitude fields in the data source
        path : the path to the data source

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
    """
    Reads a CSV file into a pandas DataFrame paying particular attention
    that any datetime fields and lat/long fields are appropriately parsed
    to allow for data matching.
    
    If multiple datetime columns are provided they will be examined for
    appropriate merging before being typed into datetime objects with
    column name 'date_time'.
    
    If a single lat/long column is provided it will be examined for appropriate
    parsing into separate lat and long columns before being typed into float
    values with column names 'lat' and 'long'.
    
    Column names will be normalised into underscore separated lower case.

    Parameters
    ----------
    csv_file : str or Path
        File to read.
    date_time_cols : list of str, optional
        List of column names containing any datetime values. The default is None.
    lat_long_cols : list of str, optional
        List of column names containing any lat/long values. The default is None.

    Returns
    -------
    df : pandas.DataFrame
        The data table.

    """
    
    file_path = Path(csv_file)
    
    if date_time_cols:
        if isinstance(date_time_cols, str):
            date_time_cols = [date_time_cols]
            
        parse_dates_dict = {'date_time': date_time_cols}
        
        df = pd.read_csv(file_path, parse_dates=parse_dates_dict)
    else:
        df = pd.read_csv(file_path)
        
    if lat_long_cols:
        if isinstance(lat_long_cols, str):  # single column lat/long, need to parse
            df[['lat', 'long']] = df[lat_long_cols].str.strip('()') \
                                            .str.split(', ', expand=True) \
                                            .astype('float64') \
                                            .rename(columns={0:'lat', 1:'long'})
            df.drop(lat_long_cols, axis=1, inplace=True)
        else:  # already separate lat/long columns, just need to rename
            df.rename(columns={lat_long_cols[0]: 'lat', lat_long_cols[1]: 'long'}, inplace=True)
                                                       
    columns = [clean_column_name(column) for column in df.columns]
    df.columns = columns
    
    return df


def read_json_into_df(json_file):
    """
    Reads the 'features' information from a GeoJSON file into a Pandas DataFrame.

    Parameters
    ----------
    json_file : str or Path
        File to read.

    Returns
    -------
    json_df : pandas.DataFrame
        A data table of the geographic features.

    """
    
    file_path = Path(json_file)
    
    if file_path.is_file():
        file_in = open(file_path, 'r')
        json_data = json.load(file_in)
        json_df = pd.DataFrame.from_dict(json_data['features'])
    else:
        json_df = pd.DataFrame()
        
    return json_df
        

def parse_field_params(field_params):
    """
    Checks an input string for semi-colons.  If found, returns a list of the 
    semi-colon separated values, otherwise returns the input string.

    Parameters
    ----------
    field_params : str
        Input string.

    Returns
    -------
    list of str or str
        List of any semi-colon separated values, otherise the input string.

    """
    
    if not field_params:
        return None
    elif field_params.find(';') >= 0:
        return field_params.split(';')
    else:
        return field_params
    

def check_local_data(data_index_csv):
    """
    Takes the path to a data index CSV and runs a full check that the index 
    itself can be found, then that each of the data sources in the index can
    be found.  Prints progress to standard out.

    Parameters
    ----------
    data_index_csv : str or Path
        The data index.

    Returns
    -------
    bool
        True if the data index and all data sources are found, otherwise False.

    """
    
    data_index = read_data_index_csv(data_index_csv)
    
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
        
    

##############################################################################
#                                RAINFALL CLASS                              #
##############################################################################

class Rainfall:
    """
    Class to represent a weather station and its rainfall measurements.
    Attributes of the weather station include:
        name, 
        id, 
        lat,
        long, 
        height.
    The primary data is a: 
        DataFrame containing daily rainfall measurements.
    Methods include:
        distance_from_station - the haversine distance from any point
                                by lat/long to the weather station.
    """
    
    def __init__(self, index_listing, data_frame):
        """
        Initialise the Rainfall object by attaching the measurement data
        and parsing the associated data notes for relevant station information.

        Parameters
        ----------
        index_listing : dict
            The data source entry in the data index list.
        data_frame : pandas.DataFrame
            The tabular measurement data loaded from file.

        Returns
        -------
        None.

        """
        
        self.df = data_frame
        self._read_rainfall_data_notes(index_listing)
    
    
    def _isfloat(value):
        """
        Safely test whether a string can be converted to a float.

        Parameters
        ----------
        value : str
            The string to test.

        Returns
        -------
        bool
            True if conversion to float wouldn't generate an exception.

        """
        
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    
    def _read_rainfall_data_notes(self, index_listing):
        """
        Parses the data notes file associated with the Rainfall data to
        extract details about the weather station.

        Parameters
        ----------
        index_listing : dict
            The data source entry in the data index list.

        Returns
        -------
        bool
            True if all target information found.

        """
        
        data_file = index_listing['path']
        notes_file = data_file.replace('Data.csv', 'Note.txt')
        
        notes_path = Path(notes_file)
        
        if not notes_path.is_file():
            print(f'File not found: {notes_path}')
            return False
        
        self.station = {}
        
        # map search strings to dictionary keys
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
                        
                        # convert to float if possible (eg, lat, long)
                        if Rainfall._isfloat(value):
                            value = float(value)
                            
                            # convert to int if possible (eg. station id)
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
        """
        Returns Rainfall measurements DataFrame.

        Returns
        -------
        pandas.DataFrame
            Rainfall measurements table.

        """
        
        if 'id' in self.station:
            return self.df
    
    
    def get_station_id(self):
        """
        Returns station ID.

        Returns
        -------
        int
            Station ID.

        """
        
        if 'id' in self.station:
            return self.station['id']
   
    
    def get_station_name(self):
        """
        Returns station name.

        Returns
        -------
        str
            Station name.

        """
        
        if 'name' in self.station:
            return self.station['name']
    
    
    def get_station_lat(self):
        """
        Returns station latitude.

        Returns
        -------
        float
            Station latitude.

        """
        
        if 'lat' in self.station:
            return self.station['lat']
    
    
    def get_station_long(self):
        """
        Returns station longitude.

        Returns
        -------
        float
            Station longitude.

        """
        
        if 'long' in self.station:
            return self.station['long']
    
    
    def get_station_lat_long(self):
        """
        Returns tuple of station (latitude, longitude)

        Returns
        -------
        float
            Station latitude.
        float
            Station longitude.

        """
        
        if 'lat' in self.station and 'long' in self.station:
            return (self.station['lat'], self.station['long'])
    
    
    def get_station_long_lat(self):
        """
        Returns tuple of station (longitude, latitude)

        Returns
        -------
        
        float
            Station longitude.
        float
            Station latitude.

        """
        
        if 'lat' in self.station and 'long' in self.station:
            return (self.station['long'], self.station['lat'])
     
        
    def get_station_height(self):
        """
        Returns station height.

        Returns
        -------
        int
            Station height in metres.

        """
        
        if 'height' in self.station:
            return self.station['height']
    
    
    def distance_from_station(self, lat2, lon2):
        """
        Returns distance from station to a given latitude and longitude.

        Parameters
        ----------
        lat2 : float
            Latitude of point of interest.
        lon2 : float
            Longitude of point of interest.

        Returns
        -------
        distance : float
            Distance in km from station to point of interest.

        """
        
        if not 'lat' in self.station or not 'long' in self.station:
            return
    
        R = 6371 # radius of the Earth in km
        
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
        

##############################################################################
#                                 SUBURB CLASS                               #
##############################################################################

class Suburb:
    """
    Class to contain GIS polygon/record data and provide methods to position
    any lat/long point by its suburb and/or district.
    """
    
    # dict to map terminology in shapefile records to preferred term
    level_map = {'Gazetted Locality': 'suburb',
                 'District': 'district'}
    
    def __init__(self, data_path):
        """
        Takes the path to the '.shp' shapefile and initialises the Suburb object.

        Parameters
        ----------
        data_path : str or Path
            Path to the '.shp' shapefile.

        Returns
        -------
        None.

        """
        
        # read in the shapefile shapes and records
        sf = shapefile.Reader(data_path)
        self.shapes = sf.shapes()
        self.records = sf.records()
        
        # preprocess data for improved efficiency when interrogated
        self.__calculate_record_ranges()
        self.__build_district_lookup()
        
        
    def __calculate_record_ranges(self):
        """
        Examines shapefile records to determine the indexes that relate to 
        'suburb' and the indexexes that relate to 'district' data.  Allows for
        more focussed and faster searching.

        Returns
        -------
        None.

        """
        num_records = len(self.records)
        first_suburb = num_records - 1
        first_district = num_records - 1
        last_suburb = 0
        last_district = 0
        
        for i in range(num_records):
            level = self.records[i][4]
            
            if level == 'Gazetted Locality':
                if i < first_suburb:
                    first_suburb = i
                elif i > last_suburb:
                    last_suburb = i
            elif level == 'District':
                if i < first_district:
                    first_district = i
                elif i > last_district:
                    last_district = i
        
        self.suburb_range = range(first_suburb, last_suburb + 1)
        self.district_range = range(first_district, last_district + 1)
        
        
    def __build_district_lookup(self):
        """
        Builds an index of each suburb that can be uniquely mapped to a 
        particular district.  This speeds up searching as once a point is located
        in a suburb if the district can be mapped there's no need to additionally
        search the district boundaries to find the correct placement.

        Returns
        -------
        None.

        """
        
        lookup = defaultdict(list)
        
        for i in self.suburb_range:
            suburb = self.records[i][3]
            suburb_boundary = shape(self.shapes[i])
        
            for j in self.district_range:
                district = self.records[j][3]
                district_boundary = shape(self.shapes[j])
        
                if suburb_boundary.intersects(district_boundary):
                    lookup[suburb].append(district)
        
        # only include suburbs that map to a single district
        self.district_lookup = {k: v[0] for k, v in lookup.items() if len(v) == 1}
        
    
    def __locate(self, lat, long):
        """
        Takes a latitude and longitude and returns a dictionary containing
        the suburb and district the point is located in.

        Parameters
        ----------
        lat : float
            Latitude.
        long : float
            Longitude.

        Returns
        -------
        location : dict
            Dictionary of location keyed by 'suburb' and 'district'.

        """
        
        point = Point(long, lat)
        location = {'suburb': '', 'district': ''}
        suburb = ''
        
        # first find suburb
        for i in self.suburb_range:
            suburb_boundary = shape(self.shapes[i])
        
            if point.within(suburb_boundary):
                suburb = self.records[i][3]
                location['suburb'] = suburb
                break
           
        # then check if it's in the district lookup
        if suburb in self.district_lookup:
            location['district'] = self.district_lookup[suburb]
            return location
        
        # otherwise find the district
        for i in self.district_range:
            district_boundary = shape(self.shapes[i])
        
            if point.within(district_boundary):
                location['district'] = self.records[i][3]
                return location
                
        return location
    
    
    def __locate_df(self, df):
        """
        Takes a pandas DataFrame that includes 'lat' and 'long' columns and
        determines the suburb and district for each and returns a copy of
        the DataFrame with 'suburb' and 'district' columns added.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing 'lat' and 'long' columns.

        Returns
        -------
        pandas.DataFrame
            Copy of input DataFrame with 'suburb' and 'district' columns added.

        """
        
        res = [self.__locate(lat, long) for lat, long in zip(df['lat'], df['long'])]  
        res_df = pd.DataFrame(res)
        res_df.fillna('', inplace=True)
        return df.join(res_df, how='left')
    
    
    def locate(self, *args):
        """
        Takes a particular point given by its latitude and longitude, or a
        pandas DataFrame that includes 'lat' and 'long', and determines the
        suburb and district of each point.
        
        If the input is a point, a dictionary with 'suburb' and 'district' keys
        is returned.
        
        If the input is a DataFrame, a copy of the DataFrame with 'suburb' and
        'district' columns added is returned

        Parameters
        ----------
        *args : float, float or pandas.DataFrame
            A point lat, long or a DataFrame that includes 'lat' and 'long' 
            colummns.

        Returns
        -------
        dict or pandas.DataFrame
            A dictionary with 'suburb' and 'district' keys for a single point 
            input.
            A pandas.DataFrame with 'suburb' and 'district' columns added for a 
            DataFrame input.

        """
        
        if len(args) == 2:
            lat, long = args
            
            if isinstance(lat, float) and isinstance(long, float):
                return self.__locate(lat, long)
                
        elif isinstance(args[0], pd.DataFrame):
            df = args[0]
            
            return self.__locate_df(df)
        

##############################################################################
#                              UTILITY FUNCTIONS                             #
##############################################################################            
     
def load_data(data_index_path):
    """
    Reads a CSV file containing information on local data sources, parse each 
    into the appropriate data structure, and bundles them into a dictionary.
    
    Relevant fields in the CSV index are:
        
        type | description | format | date_time_fields | lat_long_fields | path
        -----+-------------+--------+------------------+------------------------
        (str)|     (str)   |  (str) |      (str)       |       (str)     | (str)
    
    Where values are:
        
        type  : a classification of the data, is the primary key in the resultant 
                dictionary
        description : a descriptor to distinguish multiple sources of the same type, 
                      if used provides the key of a nested dictionary
        format : the file extension of the data source to help determine how it 
                 should be processed
        date_time_fields : a semi-colon separated list of columns names for any 
                          datetime fields in the data source
        lat_long_fields : a semi-colon separated list of columns names for any 
                          latitude and longitude fields in the data source
        path : the path to the data source
    
    The index can be automatically generated by the 'cycling_download_data' module.    

    Parameters
    ----------
    data_index_path : str or Path
        Path to the data index CSV file.

    Returns
    -------
    data : dict
        A dictionary containing the data.  Keys are given by the 'type'
        and 'description' fields of each source.  Values are source 'type'
        dependant and may include pandas DataFrames, Rainfall objects, and
        Suburb objects.

    """
    
    # load the data index
    data_index = read_data_index_csv(data_index_path)
    data = {}
    
    # calculate the maximum line length for the progress display
    max_width = 0
    for data_source in data_index:
        if len(data_source['path']) > max_width:
            max_width = len(data_source['path'])
    print('Reading data:')
    
    for data_source in data_index:
        # extract the relevant fields from the index
        data_path = data_source['path']
        data_type = data_source['type']
        data_description = data_source['description']
        data_format = data_source['format']
        
        # parse the semi-colon separated fields
        date_time = parse_field_params(data_source['date_time_fields'])
        lat_long = parse_field_params(data_source['lat_long_fields'])
        
        padding = '.' * (max_width - len(data_source['path']) + 3)
        print(f'  {data_path} {padding}', end=' ')
        
        # if the data source is CSV file then load to DataFrame
        if data_format.lower() == 'csv':
            data_content = read_csv_into_df(data_path, date_time_cols=date_time, lat_long_cols=lat_long)
        
        elif data_format.lower() == 'json':
            data_content = read_json_into_df(data_path)
        # if the data source is a Shapefile then load a Suburb object
        elif data_format.lower() == 'shp':
            data_content = Suburb(data_path)     
        else:
            continue    
         
        # if the source data is rainfall data, then need create Rainfall object
        # with weather station info as well as the DataFrame
        if data_type.lower() == 'rainfall':
            data_content = Rainfall(data_source, data_content)
        
        # if there are multiple sources with the same data type then need to
        # create a nested dictionary
        if data_description:
            if data_type in data:
                data[data_type][data_description] = data_content
            else:
                data[data_type] = {data_description: data_content}
        else:
            data[data_type] = data_content
            
        print('loaded')
        
    return data 


##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':             
    
    print()
    print('###########################################################')
    print('#                       LOAD DATA                         #')
    print('###########################################################')
    print()
    
    data = load_data(Path(DATA_FOLDER) / DATA_INDEX)
        
    
    
    print()
    print('###########################################################')
    print('#                        DEMO DATA                        #')
    print('###########################################################')
    print()

    from cycling_data_demo import *
    suburb_type = type(data['suburb'])
    data_demo(data, suburb_type)
    