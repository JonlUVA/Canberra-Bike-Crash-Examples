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


def data_demo(data):
    pass


if __name__ == '__main__':
    
    print()
    print('###########################################################')
    print('#                   DEPENDENCY CHECK                      #')
    print('###########################################################')
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
    
    # import everything else
    from cycling_globals import *
    from cycling_update_compatible_systems import *
    
    # if dependencies met update compatible systems (or move to end?)
    
    # if no local data, download data
    
    # load data
    
    # analyse data
    
    # visualise data