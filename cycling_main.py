#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Central project module with 'main' function to check system compatibility, then
download, ingest, analyse, and visualise data.

@author:  tarney
@uid:     u7378856
@created: Sat Sep 18 16:24:21 2021
"""
import os
import sys
import time
from pathlib import Path
import tempfile
import csv
from cycling_check_dependencies import *


##############################################################################
#                               HELPER FUNCTIONS                             #
##############################################################################

def print_header(header_text, header_width=75, all_caps=True):
    """
    Prints text as a 3 line header of a given width, surrounded by hash
    symbols, with a blank line before and after.

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
    
    print()
    print('#' * header_width)
    print(header_line)
    print('#' * header_width)
    print()


##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':

    ##########################################################################
    #                            CHECK DEPENDENCIES                          #
    ##########################################################################
    print_header('Checking Dependencies')
    
    root_path = Path.cwd()
    local_module_prefix = 'cycling'
    sys_config = Dependencies(root_path, ignore_module_prefix=local_module_prefix,
                              include_subs=True, subs_to_ignore=['scratch'])

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
    from cycling_data_integration import *
    from cycling_helper_functions import *

    
    ##########################################################################
    #             UPDATE COMPATIBLE SYSTEMS / REQUIREMENTS DOC               #
    ##########################################################################
    print_header('Updating Compatible Systems')
       
    compatible_systems_csv = 'compatible_systems/compatible_systems.csv'
    requirements_doc_template = 'compatible_systems/REQUIREMENTS.template'
    requirements_doc = 'REQUIREMENTS.md'
    
    update_compatible_systems_csv(sys_config, compatible_systems_csv)
    update_requirements_doc(compatible_systems_csv, requirements_doc_template, requirements_doc)
    
    print()
    print('Please feel free to commit these files to the remote repository.')
    
    
    ##########################################################################
    #            CHECK IF DATA ALREADY PROCESSED AND STORED LOCALLY          #
    ##########################################################################
    print_header('Checking For Analysed Data')
    
    processed_data_tables = ['cyclists',
                             'crashes'] 
    data_paths = {data_table: Path(DATA_FOLDER) / (data_table + '.csv') 
                  for data_table in processed_data_tables}
    
    if all([file_exists(data_paths[table]) for table in data_paths]):
        ######################################################################
        #                        LOAD PROCESSED DATA                         #
        ######################################################################
        print('All local data sources found')
        
        integrated_data = {}
        
        for table, path in data_paths.items():
            integrated_data[table] = read_csv_to_df(path)
    else:
        print('Local data sources ... NOT FOUND')
        
        
        ######################################################################
        #         CHECK FOR LOCAL RAW DATA OTHERWISE DOWNLOAD DATA           #
        ######################################################################
        print_header('Checking Local Raw Data Sources')
        
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
        print_header('Loading Raw Data')
        
        data = load_data(data_index_path)
        print()
        print('All raw data sources loaded')
        
        
        ######################################################################
        #                           ANALYSE DATA                             #
        ######################################################################
        print_header('Analysing Raw Data')
        
        print('This may take a minute, please be patient ... ', end='')
        integrated_data = integration(data)
        print('complete')
        print()
        
        for table_name, df in integrated_data.items():
            output_path = Path(DATA_FOLDER) / (table_name + '.csv')
            print(f'  Writing {table_name} data to disk: {output_path}')
            write_df_to_csv(df, output_path)
            
        print()
        print('All data analysed and written to disk')
    
    
    ##########################################################################
    #                              VISUALISE DATA                            #
    ##########################################################################
    print_header('Visualising Data')

    print('Starting dashboard...')
    print()

    from cycling_app_index import *

    run_vis(reload=False)
    
    print()
    print('END :)')
    