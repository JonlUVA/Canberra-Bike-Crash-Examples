#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General helper functions, not module specific

@author:  tarney
@uid:     u7378856
@created: Thu Sep 30 18:29:00 2021
"""


from pathlib import Path
import pandas as pd


##############################################################################
#                               HELPER FUNCTIONS                             #
##############################################################################


def file_exists(file):
    """
    Checks a file exists.

    Parameters
    ----------
    file : str or path
        Path/name of file to check.

    Returns
    -------
    bool
        True if exists, False otherwise.

    """
    
    file_path = Path(file)
    
    return file_path.is_file()


def read_csv_to_df(file):
    file_path = Path(file)
    return pd.read_csv(file, header=0, index_col=0)
    
    
    
def write_df_to_csv(df, file):
    file_path = Path(file)
    df.to_csv(file_path, header=True, index=True)
    

def read_excel_to_df(file):
    """
    Loads an Excel sheet into a pandas DataFrame.

    Parameters
    ----------
    file : str or path
        Path/name of file to load.

    Returns
    -------
    pandas.DataFrame
        The loaded data.

    """
    
    file_path = Path(file)
    return pd.read_excel(file, header=0, index_col=0)
    
    
def write_df_to_excel(df, file):
    """
    Writes a pandas DataFrame to an Excel file.

    Parameters
    ----------
    df : pandas.DataFrame
        Data to write.
    file : str or path
        Output file.

    Returns
    -------
    None.

    """
    
    file_path = Path(file)
    df.to_excel(file_path, header=True, index=True)
  
   
  
##############################################################################
#                                    MAIN                                    #
##############################################################################
    
if __name__ == '__main__':
    
    ##########################################################################
    #                CONDITIONALLY READING/WRITING DATAFRAME DEMO            #
    ##########################################################################    
    
    from cycling_globals import *
    
    # let's give the file a name
    data_file = 'test_file.xlsx'
    
    # but let's bang it in the DATA_FOLDER for safe keeping
    data_path = Path(DATA_FOLDER) / data_file
    
    print()
    
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
    
    print()
    print(df)