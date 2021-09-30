#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author:  tarney
@uid:     u7378856
@created: Thu Sep 30 18:29:00 2021
"""

from pathlib import Path
import pandas as pd

from cycling_globals import *


def file_exists(file):
    file_path = Path(file)
    
    return file_path.is_file()


def read_excel_to_df(file):
    file_path = Path(file)
    return pd.read_excel(file, header=0, index_col=0)
    
    
def write_df_to_excel(df, file):
    file_path = Path(file)
    df.to_excel(file_path, header=True, index=True)
    
    
if __name__ == '__main__':
    
    # let's give the file a name
    data_file = 'test_file.xlsx'
    
    # but let's bang it in the DATA_FOLDER for safe keeping
    data_path = Path(DATA_FOLDER) / data_file
    
    
    if file_exists(data_path):
        # great, data on file, let's load that
        
        print(f'Reading: {data_path}')
        df = read_excel_to_df(data_path)
    else:
        # bugger, no data on file, let's calculate it
        df = pd.DataFrame([['a', 'b'], ['c', 'd']],
                   index=['row 1', 'row 2'],
                   columns=['col 1', 'col 2'])
        
        # then write to disk to save time in the future
        print(f'Writing: {data_path}')
        write_df_to_excel(df, data_path)
    
    