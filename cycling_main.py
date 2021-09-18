#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author:  tarney
@uid:     u7378856
@created: Sat Sep 18 16:24:21 2021
"""

import sys

from cycling_globals import *
from cycling_check_dependencies import *

if __name__ == '__main__':
    
    print()
    print('###########################################################')
    print('#                   DEPENDENCY CHECK                      #')
    print('###########################################################')
    print()
    
    root_path = Path.cwd()
    local_module_prefix = 'cycling'
    dependencies = Dependencies(root_path, ignore_module_prefix=local_module_prefix)

    if dependencies.check():
        # print('System appears compatible:')
        # print()
        print(dependencies)
    else:
        print('Required modules missing, please install:')
        print()
        for i, module in enumerate(dependencies.get_missing_modules()):
            print(f'{i + 1}: {module}')
        sys.exit()

    # if dependencies met update compatible systems (or move to end?)
    
    # import everything else
    
    # if no local data, download data
    
    # load data
    
    # analyse data
    
    # visualise data