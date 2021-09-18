#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author:  tarney
@uid:     u7378856
@created: Sat Sep 18 08:56:07 2021
"""

try:
    import sys
    import importlib
    import platform
    import socket
    from pathlib import Path
except ModuleNotFoundError as me:
    print(f"Dependency check requires missing module '{me.name}' (how embarassing!), please install first.")
    sys.exit() 


class Dependencies:
    def __init__(self, root_path, ignore_module_prefix='', include_subs=False, self_ignore=True):
        self._path = root_path
        
        if isinstance(self._path, str):
            self._path = Path(self._path)
            
        if not self._path.is_dir():
            return
        
        self._ignore_prefix = ignore_module_prefix
        self._include_subs = include_subs
        self._self_ignore = self_ignore
        
        self._list_python_files()
        
        if not self._file_list:
            return
        
        self._build_module_list()
        self._get_module_versions()
        self._hostname = socket.gethostname()
        
        # if not self._modules:
        #     return
        
       
    def __str__(self):
        text = f'Host: {self._hostname}\n'
        
        if len(self._modules_found) > 0:
            max_module_len = 0
            max_version_len = 0
            
            for module, version in self._modules_found.items():
                if len(module) > max_module_len:
                    max_module_len = len(module) + 1
            
                if len(version) > max_version_len:
                    max_version_len = len(version) + 1
            
            text += '\n'
            text += 'Installed Modules:\n'
            text += '\n'
            text += f"{'Module':{max_module_len}} | Version\n"
            text += '-' * (max_module_len + 1) + '+' + '-' * max_version_len + '\n'
            
            for module, version in self._modules_found.items():
                text += f'{module:{max_module_len}} | {version}\n'
            
        if len(self._modules_missing) > 0:
            max_module_len = 0
            
            for module in self._modules_missing:
                if len(module) > max_module_len:
                    max_module_len = len(module)
            
            text += '\n'
            text += 'Missing Modules:\n'
            text += '\n'
            text += 'Module\n'
            text += '-' * max_module_len + '\n'
            
            for module in self._modules_missing:
                text += f'{module}\n'
        else:
            text += '\n'
            text += 'No required modules missing.'
            
        return text
    
    def _list_python_files(self):
        if self._include_subs:
            file_list = list(self._path.glob('**/*.py'))
        else:
            file_list = list(self._path.glob('*.py'))
            
        self_path = Path(__file__)
        
        if self._self_ignore and self_path in file_list:
            file_list.remove(self_path)
            
        self._file_list = file_list
    
    
    def _build_module_list(self):
        modules = set()
        modules.add('python')
        
        for file_path in self._file_list:
            with open(file_path) as file:
                # print(file_path)
                for line in file:
                    words = line.split()
                    
                    if not len(words):
                        continue
                    
                    if 'import' in words and words[0] != '#':
                        if words.index('import') > 2:
                            continue
                        
                        if 'from' in words:
                            module_index = words.index('from') + 1
                        else:
                            module_index = words.index('import') + 1
                            
                        if module_index < len(words):
                            module = words[module_index]
                        else:
                            continue
                        
                        if module.find('.') > 0:
                            module = module[:module.find('.')]
                        
                        if not self._ignore_prefix:
                            modules.add(module)
                        elif not module.startswith(self._ignore_prefix):
                            modules.add(module)
                            
                        if module == 'statements':
                            print(f'{file_path}: {line}')
                            
        modules = list(modules)
        modules.sort()
        
        self._required_modules = modules
        
    def _get_module_versions(self):
        """
        Builds a dictionary of modules and the current version running on the 
        host system.
    
        Parameters
        ----------
        module_list : list of str
            A list of module names.
    
        Returns
        -------
        D : dict
            A dictionary of {'module name': 'module version'} pairs.
    
        """
        D = {}
        missing = set()
        
        for module in self._required_modules:
            if module.lower() == 'python':
                D['python'] = self._get_python_version()
                continue
            
            try: 
                loaded_module = importlib.import_module(module)
                
                if hasattr(loaded_module,'__version__'):
                    D[module] = loaded_module.__version__
                else:
                    D[module] = 'unknown'
            except ModuleNotFoundError:
                # print(f"Warning: module '{module}' not found")
                missing.add(module)
                
        self._modules_found = D
        self._modules_missing = missing
      
    def _get_python_version(self):
        """
        Returns the Python interpreter version running on the host system.
    
        Returns
        -------
        str
            Python interpreter version.
    
        """
        return platform.python_version()  
    
    def get_hostname(self):
        """
        Returns the name of the current host system.
    
        Returns
        -------
        str
            Name of the host system.
    
        """
        return self._hostname    
    
    def check(self):
        return len(self._modules_missing) == 0
    
    def get_missing_modules(self):
        return list(self._modules_missing)
        
    def get_system_config(self):
        return self._modules_found
    
    def get_file_list(self):
        return self._file_list
    
    def get_module_list(self):
        return self._required_modules


##############################################################################
#                                    MAIN                                    #
##############################################################################

if __name__ == '__main__':

    print()
    print('###########################################################')
    print('#                   DEPENDENCY CHECK                      #')
    print('###########################################################')
    print()
    
    root_path = Path.cwd()
    local_module_prefix = 'cycling'
    dependencies = Dependencies(root_path, ignore_module_prefix=local_module_prefix)
    
    print('Source code files examined')
    print('--------------------------')
    print()
    for file in dependencies.get_file_list():
        print(file)
    print()
    print()
    
    print('Modules referenced')
    print('------------------')
    print()
    for module in dependencies.get_module_list():
        print(module)
    print()
    print()
    
     
    print('System compatibility')  
    print('--------------------')     
    print()
    print(dependencies)
    print()