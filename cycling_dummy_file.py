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
from cycling_download_data import *
from cycling_load_data import *
from cycling_data_integration import *
from cycling_helper_functions import *

    

##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':
    
    crash_file = 'crash_data.xlsx'
    cyclists_file = 'cyclist_data.xlsx'
    
    crash_path = Path(DATA_FOLDER) / crash_file
    cyclists_path = Path(DATA_FOLDER) / cyclists_file
    
    print()
    
    ##########################################################################
    #        CHECK FOR LOCAL ANALYSED DATA OTHERWISE FULL SYSTEM CHECK       #
    ##########################################################################
    
    if file_exists(crash_path) and file_exists(cyclists_path):
        print('Loading Data Analysis')
        print()
        
        integrated_data = {}
        integrated_data['crash_data'] = read_excel_to_df(crash_path)
        integrated_data['estimated_cycle'] = read_excel_to_df(cyclists_path)
        
        print('All data loaded')
    else:
            
        ##########################################################################
        #             CHECK LOCAL RAW DATA OTHERWISE DOWNLOAD DATA               #
        ##########################################################################
    
        print()
        print('Checking Local Data Sources')
        print()  
    
        data_index_path = Path(DATA_FOLDER) / DATA_INDEX
    
        if not check_local_data(data_index_path):
            print()
            print('Downloading Data')
            
            download_all_data(DATA_SOURCES, DATA_FOLDER, DATA_INDEX)
        else:
            print()
            print('All data sources found')
    
        
        ##########################################################################
        #                              LOAD RAW DATA                             #
        ##########################################################################
        print()
        print('Loading Data')
        print()  
        
        data = load_data(data_index_path)
        print()
        print('All data sources loaded')
        
        ##########################################################################
        #                    ANALYSE RAW DATA AND WRITE TO DISK                  #
        ##########################################################################
        
        print()
        print('Analysing Data')
        print()
        
        integrated_data = integration(data)
        write_df_to_excel(integrated_data['crash_data'], crash_path)
        write_df_to_excel(integrated_data['estimated_cycle'], cyclists_path)
        
        print('All data analysed')

    
    ##########################################################################
    #                              VISUALISE DATA                            #
    ##########################################################################
    print()
    print('Visualising Data')
    # print()  
    
    pass
    print()
    print('...nothing to see here (yet)')
    
