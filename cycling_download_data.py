#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


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
    word_list = folder_name.split()
    word_list = [word.strip().lower() for word in word_list]
    folder_name = '_'.join(word_list)
    return folder_name


def parse_filename_from_headers(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]
    # # content_disposition = headers.get('content-disposition')
    # file_name = re.findall('filename=(.+)', content_disposition)
    # return file_name[0]


def parse_filename_from_url(url):
    file_name = ''
    if url.find('/'):
        file_name = url.rsplit('/', 1)[1]
    return file_name


##############################################################################
#                              UTILITY FUNCTIONS                             #
##############################################################################


def add_to_git_ignore(file_or_dir):
    path_to_ignore = Path(file_or_dir)
    
    if not path_to_ignore.exists():
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
    path_to_delete = Path(file_or_dir)
    response = 'n'
    
    if not path_to_delete.exists():
        return
    
    if not force:
        response = input(f"Deleting all contents of '{path_to_delete}', this action can not be undone, would you like to continue (y/n): ").strip()
        
    if force or response.lower() == 'y':
        shutil.rmtree(path_to_delete, ignore_errors=True)
        print(f"'{path_to_delete}' deleted")



def read_data_source_csv(csv_file_name):
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
    download_root_dir = Path(download_dir)

    for data_source in data_sources:
        
        sub_dir = clean_folder_name(data_source['type'])
        sub_sub_dir = clean_folder_name(data_source['description'])
        download_path = download_root_dir / sub_dir / sub_sub_dir
        
        if not download_path.exists():
            download_path.mkdir(parents=True)
            # print(f'created: {download_path}')
            
    
        url = data_source['url']
        h = {'User-Agent': 'XYZ/3.0'}
        r = requests.get(url, headers=h, allow_redirects=True)
        
        print()
        print(f"Downloading: {download_path}")
        print(f"{'URL:':>12} {url}")
        # print(r.headers['content-type'])
        
        file_name = parse_filename_from_headers(r.headers.get('content-disposition'))
        if file_name == None:
            file_name = parse_filename_from_url(url)
            
        # print(f'file name: {file_name}')
        
        file_path = ''
        
        if r.headers['content-type'] == 'application/zip':
            try:
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(path=download_path)
                file_format = data_source['format'].strip().lower()
                glob_pattern = '**/*.' + file_format
                data_files_in_zip = list(download_path.glob(glob_pattern))
                
                if len(data_files_in_zip) == 0:
                    print(f"Warning: no {file_format} files found in '{download_path}'")
                    file_path = ''
                elif len(data_files_in_zip) > 1:
                    print(f"Warning: multiple {file_format} files found in '{download_path}', assuming first one")
                    file_path = download_path / data_files_in_zip[0]
                else:
                    file_path = download_path / data_files_in_zip[0]
            except BadZipFile:
                print(f"Warning: bad zip file '{file_name}', download skipped")
        else:
            file_path = download_path / file_name
            with open(file_path, mode="wb") as outfile:
                outfile.write(r.content)
                
        data_source['path'] = file_path
        
        if file_path:
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
