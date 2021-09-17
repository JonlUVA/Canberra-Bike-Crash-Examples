#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides tools to download online data sets and store them on the
local machine.  Details on each data source are read in from a CSV file given
in the following format:

        type  | description | format |  url  |  backup_url
        --------------------------------------------------
        (str) |    (str)    |  (str) | (str) |    (str)
        
Where values are:
    
        type : a classification of the data
        description : a descriptor to distinguish multiple sources of the 
                      same type
        format : the file extension of the intended data source to identify
                 the specific file if downloading a bundle
        url : the url of the data source
        backup url : a mirror link should the initial download fail.

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
import os


##############################################################################
#                               HELPER FUNCTIONS                             #
##############################################################################


def clean_folder_name(folder_name):
    """
    Normalises a folder name by removing any superfluous whitespace, converting
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


def http_request(url):
    """
    Send an HTTP request to the given URL and returns the request response
    if valid.

    Parameters
    ----------
    url : str
        The URL to query.

    Returns
    -------
    requests.Response
        The HTTP request Response object if successful, otherwise returns False.

    """
    try:
        request_headers = {'User-Agent': 'XYZ/3.0'}
        request_response = requests.get(url, headers=request_headers, allow_redirects=True)
        
        if request_response.status_code == requests.codes.ok:
            return request_response
        else:
            return False
    except:
        return False


def get_remote_file_name(request_response, url):
    """
    Attempts to discern the file name at the other end of an HTTP request,
    first by examining the contents of the request response headers, then
    by examining the URL itself.

    Parameters
    ----------
    request_response : requests.Response
        An HTTP request Response object, as returned by http_request.
    url : str
        The URL.

    Returns
    -------
    file_name : str
        The file name if determined, otherwise an empty string.

    """
    
    file_name = ''
    
    # Look in the content disposition header.  If the content is intended
    # as an attachment, to be downloaded and saved locally, will typically
    # reference a 'filename'
    content_disposition = request_response.headers.get('content-disposition')
    
    if content_disposition:
        file_names = re.findall('filename=(.+)', content_disposition)
        
        if len(file_names) == 0:
            return None
        
        file_name = file_names[0]
        
        if file_name.find(';'):
            file_name = file_name.split(';', 1)[0]
            
        file_name = file_name.replace('"','')
    
    # If the content disposition doesn't reveal a filename, look for any
    # characters after the final forward slash in the URL
    if file_name == '':
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
    
    comment_line = f'# Added by {this_module_path.name}\n'
    ignore_line = file_or_dir.strip() + '\n'
    already_ignoring = False
    
    if not git_ignore_path.exists():
        with open(git_ignore_path, 'w') as fout:
            fout.write(comment_line)
            fout.write(ignore_line)
    else:
        with open(git_ignore_path, 'r') as fin:
            for line in fin:
                if line.strip() == file_or_dir:
                    already_ignoring = True
                    break
                
        if not already_ignoring:
            with open(git_ignore_path, 'a') as fout:
                fout.write('\n')
                fout.write(comment_line)
                fout.write(ignore_line)
                
    if not already_ignoring:
        print()
        print(f"'{file_or_dir}' added to local '{git_ignore_file}' file")
                

def remove_from_git_ignore(file_or_dir):
    """
    Removes a file or directory from the .gitignore file in the current working
    directory.  If there's a comment on the preceding line it is also removed.

    Parameters
    ----------
    file_or_dir : str
        File or directory to remove.

    Returns
    -------
    None.

    """
    
    git_ignore_file = '.gitignore'
    git_ignore_path = Path(git_ignore_file)
    
    if not git_ignore_path.exists():
        return
    
    this_module_path = Path(__file__)
    
    comment_line = f'# Added by {this_module_path.name}\n'
    ignore_line = file_or_dir.strip() + '\n'
    
    line_found = False
    line_counter = 0
    
    # find the line and retain its line index
    with open(git_ignore_path) as fin:
        for line in fin:
            if line == ignore_line:
                line_found = True
                line_number = line_counter
                break
            line_counter += 1
    
    
    if not line_found:
        return
    
    temp_file_path = git_ignore_path.with_suffix('.bak')
    line_counter = 0
    
    # duplicate the file contents to a temp file, skipping the relevant line
    # as well as the line prior if it matches the relevant comment line
    with open(git_ignore_path) as fin, open(temp_file_path, 'w') as fout:
        for line in fin:
            if (line_counter == line_number - 1 and line == comment_line) or \
                line_counter == line_number:
                pass
            else:
                fout.write(line)
                
            line_counter += 1
    
    # delete the original file and copy the temp file over
    git_ignore_path.unlink()
    temp_file_path.rename(git_ignore_path)
    
    print()
    print(f"'{file_or_dir}' removed from local '{git_ignore_file}' file")
    

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
    bool
        True if successfully deleted, False otherwise.

    """
    
    path_to_delete = Path(file_or_dir)
    response = 'n'
    
    if not path_to_delete.exists():
        return False
    
    if not force:
        print(f"WARNING: '{path_to_delete}' already exists!")
        print(f"Would you like to delete all contents of '{path_to_delete}' first?", end='')
        response = input("This action can not be undone (y/n): ").strip()
        
    if force or response.lower() == 'y':
        shutil.rmtree(path_to_delete, ignore_errors=True)
        print(f"'{path_to_delete}' deleted")
        return True

    return False


def read_data_source_csv(csv_file_name):
    """
    Reads a CSV file containing details of the data sources to download and 
    returns a list of elements, one per download source, where each element is a 
    dictionary keyed by column header.
    
    Expected CSV format is:
        
        type  | description | format |  url  |  backup_url
        --------------------------------------------------
        (str) |    (str)    |  (str) | (str) |    (str)
        
    Which is mapped to:
        
        {'type': (str), 'description': (str), 'format': (str), 
         'url': (str), 'backup_url': (str)}

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
            url : the url of data to download
            backup url : a mirror link should the initial download fail.

    """
    
    data_source_path = Path(csv_file_name)
    
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
        
        {'type': (str), 'description': (str), 'format': (str), 
         'url': (str), 'backup_url': (str), 'path': (str)}
    
    Output CSV format is:
        
        type  | description | format |  url  |  backup_url | path
        ----------------------------------------------------------
        (str) |    (str)    |  (str) | (str) |    (str)    | (str)
        

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
             {'type': (str), 'description': (str), 'format': (str), 
              'url': (str), 'backup_url': (str)}
    download_dir : str
        The local path to store the downloads.

    Returns
    -------
    data_sources : list of dict
        A list of dicitonaries containing the information for each data source:
            {'type': (str), 'description': (str), 'format': (str), 
             'url': (str), 'backup_url': (str), 'path': (str)}

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
        
        downloaded = False 
        tried_backup = False
        url = data_source['url']
        
        while not downloaded and not tried_backup:
            response = http_request(url)
            
            # invalid response, try backup URL if supplied and not yet tried
            if not response:
                if url == data_source['backup_url'] or data_source['backup_url'] == '':
                    tried_backup = True
                else:
                    url = data_source['backup_url']
                continue
            
            print()
            print(f"Downloading: {download_path}")
            print(f"{'URL:':>12} {url}")
            
            file_name = get_remote_file_name(response, url)
            
            # invalid file name, try backup URL if supplied and not yet tried
            if not file_name:
                if url == data_source['backup_url'] or data_source['backup_url'] == '':
                    tried_backup = True
                else:
                    url = data_source['backup_url']
                continue
            
            file_ext = os.path.splitext(file_name)[1].lower()
            file_path = ''
            
            # check if file to be downloaded is zip, in which case decompress
            # and try to identify relevant source file within contents,
            # otherwise just download file directly
            if response.headers['content-type'] == 'application/zip' or file_ext == '.zip':
                try:
                    z = zipfile.ZipFile(io.BytesIO(response.content))
                    z.extractall(path=download_path)
                    
                    # look for file in contents that matches data source format
                    file_format = data_source['format'].strip().lower()
                    glob_pattern = '**/*.' + file_format
                    data_files_in_zip = list(download_path.glob(glob_pattern))
                    
                    if len(data_files_in_zip) == 0:
                        print(f"{'WARNING:':>12} no {file_format} files found in '{download_path}'")
                        file_path = ''
                    elif len(data_files_in_zip) > 1:
                        print(f"{'WARNING:':>12} multiple {file_format} files found in '{download_path}', assuming first one")
                        file_path = data_files_in_zip[0]
                    else:
                        file_path = data_files_in_zip[0]
                        
                    downloaded = True
                except zipfile.BadZipFile:
                    # invalid zip file, try backup URL if supplied and not yet tried
                    if url == data_source['backup_url'] or data_source['backup_url'] == '':
                        print(f"{'WARNING:':>12} bad zip file found, skipping download")
                        tried_backup = True
                    else:
                        print(f"{'WARNING:':>12} bad zip file found, trying backup source")
                        url = data_source['backup_url']
                    continue
            else:
                file_path = download_path / file_name
                with open(file_path, mode="wb") as outfile:
                    outfile.write(response.content)
                downloaded = True
                
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
    
    print('###########################################################')
    print('#                   DOWNLOADING DATA                      #')
    print('###########################################################')
    print()

    data_source_file = 'data_sources.csv'
    download_dir = 'data'
    local_data_file = 'local_data.csv'
    
    if delete_previous_download(download_dir):
        remove_from_git_ignore(download_dir)
        
    data_sources = read_data_source_csv(data_source_file)
    data_sources = download_data(data_sources, download_dir)
    write_data_source_csv(local_data_file, data_sources)
    add_to_git_ignore(download_dir)
