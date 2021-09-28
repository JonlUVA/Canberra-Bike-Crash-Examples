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
    

##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':
    
    ##########################################################################
    #                CHECK LOCAL DATA OTHERWISE DOWNLOAD DATA                #
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
    #                                LOAD DATA                               #
    ##########################################################################
    print()
    print('Loading Data')
    print()  
    
    data = load_data(data_index_path)
    print()
    print('All data sources loaded')
    
    ##########################################################################
    #                         ANALYSE / VISUALISE DATA                       #
    ##########################################################################
    
    # do what you will with 'data' from here