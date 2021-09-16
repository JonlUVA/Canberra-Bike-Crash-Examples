#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides tools to download online data sets and store them on the
local machine.  Details on each data source are read in from a CSV file given
in the following format:

        type  | description | format |  url
        ------------------------------------
        (str) |    (str)    |  (str) | (str)
        
Where values are:
    
        type : a classification of the data
        description : a descriptor to distinguish multiple sources of the 
                      same type
        format : the file extension of the intended data source to identify
                 the specific file if downloading a bundle
        url : the url of the data source.

The module can also generate a similar local data directory that includes a
'path' field with the path to the downloaded data stored on the local machine.

The module can also create or append a local '.gitignore' file to prevent
the downloaded data being tracked by the master git repository.

@author:  tarney
@uid:     u7378856
@created: Wed Sep 15 08:09:11 2021
"""

import csv
from pathlib import Path
import shutil
import requests
import zipfile
import io
import re


##############################################################################
#                               HELPER FUNCTIONS                             #
##############################################################################


def clean_folder_name(folder_name):
    """
    Normalised a folder name by removing any superfluous whitespace, converting
    spaces to underscores, and converting to lower case.

    Parameters
    ----------
    folder_name : str
        The folder name to be normalised.

    Returns
    -------
    folder_name : str
        The normalised folder name.

    """
    
    word_list = folder_name.split()
    word_list = [word.strip().lower() for word in word_list]
    folder_name = '_'.join(word_list)
    
    return folder_name


def parse_filename_from_headers(content_disposition):
    """
    Returns a file name, if found, in the header information from an HTTP 
    request.

    Parameters
    ----------
    cd : str
        The Content-Disposition header from an HTTP request.

    Returns
    -------
    str
        The file name if found, otherwise None.

    """
    
    if not content_disposition:
        return None
    
    fname = re.findall('filename=(.+)', content_disposition)
    
    if len(fname) == 0:
        return None
    
    return fname[0] # return the first file name


def parse_filename_from_url(url):
    """
    Returns the substring of a URL after the last forward slash.

    Parameters
    ----------
    url : str
        The URL.

    Returns
    -------
    file_name : str
        The URL substring.

    """
    
    file_name = ''
    
    if url.find('/'):
        file_name = url.rsplit('/', 1)[1]
        
    return file_name


##############################################################################
#                              UTILITY FUNCTIONS                             #
##############################################################################


def add_to_git_ignore(file_or_dir):
    """
    Adds a file or directory to the .gitignore file in the current working
    directory to prevent git tracking and uploading to the master repository.  
    
    If the file or directory doesn't exist then .gitignore is unchanged.  
    If the file or directory is already listed then .gitignore is unchanged.
    If .gitignore doesn't exist then it is created.

    Parameters
    ----------
    file_or_dir : str
        The file or directory path for git to ignore.

    Returns
    -------
    None.

    """
    path_to_ignore = Path(file_or_dir)
    
    if not path_to_ignore.exists(): # don't add non-existent file/dir
        return
    
    git_ignore_file = '.gitignore'
    git_ignore_path = Path(git_ignore_file)
    this_module_path = Path(__file__)
    
    comment = f'# Added by {this_module_path.name}\n'
    ignore = file_or_dir.strip() + '\n'
    already_ignoring = False
    
    if not git_ignore_path.exists():
        with open(git_ignore_path, 'w') as fout:
            fout.write(comment)
            fout.write(ignore)
    else:
        with open(git_ignore_path, 'r') as fin:
            for line in fin:
                if line.strip() == file_or_dir:
                    already_ignoring = True
                    break
                
        if not already_ignoring:
            with open(git_ignore_path, 'a') as fout:
                fout.write('\n')
                fout.write(comment)
                fout.write(ignore)
                
    if not already_ignoring:
        print()
        print(f"'{file_or_dir}' added to local '{git_ignore_file}' file")
                

def delete_previous_download(file_or_dir, force=False):
    """
    Deletes a file or directory from the local system along with any 
    sub-directories and files.

    Parameters
    ----------
    file_or_dir : str
        Path of file or directory to delete.
    force : bool, optional
        If True, delete without user prompted confirmation. The default is False.

    Returns
    -------
    None.

    """
    
    path_to_delete = Path(file_or_dir)
    response = 'n'
    
    if not path_to_delete.exists():
        return
    
    if not force:
        print(f"WARNING: '{path_to_delete}' already exists!", end='')
        response = input(f"Would you like to delete all contents of '{path_to_delete}' first? This action can not be undone (y/n): ").strip()
        
    if force or response.lower() == 'y':
        shutil.rmtree(path_to_delete, ignore_errors=True)
        print(f"'{path_to_delete}' deleted")


def read_data_source_csv(csv_file_name):
    """
    Reads a CSV file containing details of the data sources to download and 
    returns a list of elements, one per download source, where each element is a 
    dictionary keyed by column header.
    
    Expected CSV format is:
        
        type  | description | format |  url
        ------------------------------------
        (str) |    (str)    |  (str) | (str)
        
    Which is mapped to:
        
        {'type': (str), 'description': (str), 'format': (str), 'url': (str)}

    Parameters
    ----------
    csv_file_name : str
        Path of the CSV file to read.

    Returns
    -------
    list of dict
        As detailed above, with key-value pairs being:
            type : a classification of the data
            description : a descriptor to distinguish multiple sources of the 
                          same type
            format : the file extension of the intended data source to identify
                     the specific file if downloading a bundle
            url : the url of data to download.

    """
    
    data_source_path = Path(data_source_file)
    
    if not data_source_path.is_file():
        return []
    
    data_sources= []
    
    with open(data_source_path, encoding='utf-8-sig') as fin:
        csv_reader = csv.DictReader(fin)
        
        for row in csv_reader:
            data_sources.append(row)
        
    return data_sources


def write_data_source_csv(csv_file_name, data_sources):
    """
    Writes a CSV file containing details of the data sources downloaded and
    their location on the local system.
    
    Input dictionary format is:
        
        {'type': (str), 'description': (str), 'format': (str), 'url': (str), 'path': (str)}
    
    Output CSV format is:
        
        type  | description | format |  url  | path
        --------------------------------------------
        (str) |    (str)    |  (str) | (str) | (str)
        

    Parameters
    ----------
    csv_file_name : str
        Path of the CSV file to write.
    data_sources : list of dict
        A dicionary containing the information detailed above for each data source.

    Returns
    -------
    None.

    """
    if not data_sources:
        return
    
    data_source_path = Path(download_dir) / csv_file_name
    
    columns = list(data_sources[0].keys())
    
    with open(data_source_path, 'w') as fout:
        csv_writer = csv.DictWriter(fout, fieldnames=columns)
        csv_writer.writeheader()
        csv_writer.writerows(data_sources)
        
    print()
    print(f"Data directory written to: {data_source_path}")


def download_data(data_sources, download_dir):
    """
    Takes a list of data source dictionaries (as returned by read_data_source_csv),
    and a local directory path, and downloads each data source to the local directory.
    
    Each data source will be placed in a sub-directory as defined by the
    'type' and 'description' values found in its dictionary.
    
    If the data source is a zip file it will be automatically unzipped.
    
    An amended data source dictionary that includes the path to the local data 
    set is returned.

    Parameters
    ----------
    data_sources : list of dict
        A list of dicitonaries containing the information for each data source:
             {'type': (str), 'description': (str), 'format': (str), 'url': (str)}
    download_dir : str
        The local path to store the downloads.

    Returns
    -------
    data_sources : list of dict
        A list of dicitonaries containing the information for each data source:
             {'type': (str), 'description': (str), 'format': (str), 'url': (str), 'path': (str)}

    """
    download_root_dir = Path(download_dir)

    for data_source in data_sources:
        
        # get the path to the subdirectory where the data should be saved
        sub_dir = clean_folder_name(data_source['type'])
        sub_sub_dir = clean_folder_name(data_source['description'])
        download_path = download_root_dir / sub_dir / sub_sub_dir
        
        # create the download folder and any parent directories if it doesn't exist
        if not download_path.exists():
            download_path.mkdir(parents=True)
            
    
        # make the HTTP request with a custom header to coerce the remote
        # server that it isn't a bot
        url = data_source['url']
        h = {'User-Agent': 'XYZ/3.0'}
        r = requests.get(url, headers=h, allow_redirects=True)
        
        print()
        print(f"Downloading: {download_path}")
        print(f"{'URL:':>12} {url}")
        
        # try to determine the name of the file that will be downloaded
        file_name = parse_filename_from_headers(r.headers.get('content-disposition'))
        if file_name == None:
            file_name = parse_filename_from_url(url)
            
        file_path = ''
        
        # if the downloaded file is a zip file, then try to unzip it and determine
        # which bundled file is the relevant data source, otherwise just download
        # the file directly
        if r.headers['content-type'] == 'application/zip':
            try:
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(path=download_path)
                file_format = data_source['format'].strip().lower()
                glob_pattern = '**/*.' + file_format
                data_files_in_zip = list(download_path.glob(glob_pattern))
                
                if len(data_files_in_zip) == 0:
                    print(f"{'WARNING:':>12} no {file_format} files found in '{download_path}'")
                    file_path = ''
                elif len(data_files_in_zip) > 1:
                    print(f"{'WARNING:':>12} multiple {file_format} files found in '{download_path}', assuming first one")
                    file_path = download_path / data_files_in_zip[0]
                else:
                    file_path = download_path / data_files_in_zip[0]
            except zipfile.BadZipFile:
                print(f"{'WARNING:':>12} bad zip file found, skipping download")
        else:
            file_path = download_path / file_name
            with open(file_path, mode="wb") as outfile:
                outfile.write(r.content)
                
        # if the download was successful and a valid local file path is created
        # add it to the data source dictionary
        if file_path:
            data_source['path'] = file_path
            print(f"{'Local:':>12} {file_path}")
        
    return data_sources
  
  
##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':

    data_source_file = 'data_sources.csv'
    download_dir = 'data'
    local_data_file = 'local_data.csv'
    
    delete_previous_download(download_dir)
    data_sources = read_data_source_csv(data_source_file)
    data_sources = download_data(data_sources, download_dir)
    write_data_source_csv(local_data_file, data_sources)
    add_to_git_ignore(download_dir)
