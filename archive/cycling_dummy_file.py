#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author:  tarney
@uid:     u7378856
@created: Tue Sep 28 14:38:09 2021
"""


import sys
from pathlib import Path

from cycling_globals import *
from cycling_update_compatible_systems import *
from cycling_download_data import *
from cycling_load_data import *
from cycling_data_integration import *
from cycling_helper_functions import *


##############################################################################
#                               HELPER FUNCTIONS                             #
##############################################################################

def print_header(header_text, header_width=75, all_caps=True):
    """
    Prints text as a 3 line header of a given width, surrounded by hash
    symbols.

    Parameters
    ----------
    header_text : str
        Text to display.
    header_width : int, optional
        Number of characters on each line. The default is 75.
    all_caps : bool, optional
        Convert text to uppercase. The default is True.

    Returns
    -------
    None.

    """
    
    if all_caps:
        header_text = header_text.upper()
    
    if len(header_text) > header_width - 4:
        header_text = header_text[:header_width-7] + '...'
        
    header_line = f'#{header_text:^{header_width-2}}#'    
    
    print('#' * header_width)
    print(header_line)
    print('#' * header_width)
    

##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':
    
    ##########################################################################
    #            CHECK IF DATA ALREADY PROCESSED AND STORED LOCALLY          #
    ##########################################################################
    
    print()
    print_header('Checking Local Processed Data Sources')
    print()  
    
    processed_data_tables = ['cyclists',
                             'crashes'] 
    data_paths = {data_table: Path(DATA_FOLDER) / (data_table + '.xlsx') 
                  for data_table in processed_data_tables}
    
    if all([file_exists(data_paths[table]) for table in data_paths]):      
        ######################################################################
        #                        LOAD PROCESSED DATA                         #
        ######################################################################
        
        print('All processed data sources found')
        
        integrated_data = {}
        
        for table, path in data_paths.items():
            integrated_data[table] = read_excel_to_df(path)
    else:
        print('Processed data sources not found')
        
        
        ######################################################################
        #         CHECK FOR LOCAL RAW DATA OTHERWISE DOWNLOAD DATA           #
        ######################################################################
    
        print()
        print_header('Checking Local Raw Data Sources')
        print()  
    
        data_index_path = Path(DATA_FOLDER) / DATA_INDEX
    
        if not check_local_data(data_index_path):
            print()
            print_header('Downloading Raw Data')
            
            download_all_data(DATA_SOURCES, DATA_FOLDER, DATA_INDEX)
        else:
            print()
            print('All raw data sources found')
    
        
        ######################################################################
        #                           LOAD RAW DATA                            #
        ######################################################################
        print()
        print_header('Loading Raw Data')
        print()  
        
        data = load_data(data_index_path)
        print()
        print('All raw data sources loaded')
        
        
        ######################################################################
        #                           ANALYSE DATA                             #
        ######################################################################
        print()
        print_header('Analysing Raw Data')
        print()  
        
        print('This may take a minute, please be patient ... ', end='')
        integrated_data = integration(data)
        print('complete')
        print()
        
        for table_name, df in integrated_data.items():
            output_path = Path(DATA_FOLDER) / (table_name + '.xlsx')
            print(f'  Writing {table_name} data to disk: {output_path}')
            write_df_to_excel(df, output_path)
            
        print()
        print('All data analysed and written to disk')
    
    
    ##########################################################################
    #                              VISUALISE DATA                            #
    ##########################################################################
    print()
    print_header('Visualising Data')
    print()  
    
    pass
    print()
    print('...nothing to see here (yet)...')
    
