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
    
    from cycling_data_demo import *
    data_demo(data)