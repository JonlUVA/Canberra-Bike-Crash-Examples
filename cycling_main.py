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


##############################################################################
#                               HELPER FUNCTIONS                             #
##############################################################################

def print_header(header_text, header_width=77, all_caps=True):
    if all_caps:
        header_text = header_text.upper()
        
    print('#' * header_width)
    
    header_line = f'#{header_text:^{header_width-2}}#'
    print(header_line)
    
    print('#' * header_width)
    

##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':
    
    
    ##########################################################################
    #                            CHECK DEPENDENCIES                          #
    ##########################################################################
    print()
    print_header('Checking Dependencies')
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
    
    
    ##########################################################################
    #             UPDATE COMPATIBLE SYSTEMS / REQUIREMENTS DOC               #
    ##########################################################################
    
    print()
    print_header('Updating Compatible Systems')
    print()  
       
    compatible_systems_csv = 'compatible_systems/compatible_systems.csv'
    requirements_doc_template = 'compatible_systems/REQUIREMENTS.template'
    requirements_doc = 'REQUIREMENTS.md'
    
    update_compatible_systems_csv(sys_config, compatible_systems_csv)
    update_requirements_doc(compatible_systems_csv, requirements_doc_template, requirements_doc)
    
    print()
    print('Please feel free to commit these files to the remote repository.')
    

    ##########################################################################
    #                CHECK LOCAL DATA OTHERWISE DOWNLOAD DATA                #
    ##########################################################################

    print()
    print_header('Checking Local Data Sources')
    print()  

    data_index_path = Path(DATA_FOLDER) / DATA_INDEX

    if not check_local_data(data_index_path):
        print()
        print_header('Downloading Data')
        
        download_all_data(DATA_SOURCES, DATA_FOLDER, DATA_INDEX)
    else:
        print()
        print('All data sources found')

    
    ##########################################################################
    #                                LOAD DATA                               #
    ##########################################################################
    print()
    print_header('Loading Data')
    print()  
    
    data = load_data(data_index_path)
    print()
    print('All data sources loaded')
    
    ##########################################################################
    #                         ANALYSE / VISUALISE DATA                       #
    ##########################################################################
    
    # Here's a little demo of the data that is available:
    from cycling_data_demo import *
    print()
    print_header('Data Demo')
    data_demo(data)