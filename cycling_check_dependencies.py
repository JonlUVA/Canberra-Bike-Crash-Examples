#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auxiliary module to scan project folder for Python source files, scan the code
in those files for module dependencies, and check if host system has those 
modules installed.

@author:  tarney
@uid:     u7378856
@created: Sat Sep 18 08:56:07 2021
"""

# Dependency check has its own dependencies, best to import those with some
# added protection...
try:
    import sys
    import importlib
    import platform
    import socket
    from pathlib import Path
except ModuleNotFoundError as me:
    print(f"Dependency check requires missing module '{me.name}' "
          f"(how embarassing!), please install first.")
    sys.exit() 


class Dependencies:
    """
    Class to determine module requiremenets of Python coding project and 
    assess host system.
    """
    
    def __init__(self, root_path, ignore_module_prefix='', include_subs=False,
                 self_ignore=True, subs_to_ignore=None):
        """
        Creates a Dependencies object by scanning a project directory for code
        files, checking any module dependencies, and check if system has
        each module installed.

        Parameters
        ----------
        root_path : str or Path
            Root directory of the source files.
        ignore_module_prefix : str, optional
            Prefix of any local project modules to be ignored. The default is ''.
        include_subs : bool, optional
            Examine source code in subdirectories. The default is False.
        self_ignore : bool, optional
            Include modules required by dependency check. The default is True.

        Returns
        -------
        None.

        """
        
        self._path = root_path
        
        # convert project folder string to Path object
        if isinstance(self._path, str):
            self._path = Path(self._path)
        
        # make sure project folder exists before continuing
        if not self._path.is_dir():
            return
        
        self._ignore_prefix = ignore_module_prefix
        self._include_subs = include_subs
        self._self_ignore = self_ignore
        
        # turn list of subdirectories to ignore into Path objects
        if subs_to_ignore is None:
            self._subs_to_ignore = subs_to_ignore
        else:
            self._subs_to_ignore = [Path.cwd() / sub for sub in subs_to_ignore]
        
        # compile list of source code files
        self._list_python_files()
        
        # make sure source files are found before continuing
        if not self._file_list:
            return
        
        self._build_module_list()
        self._get_module_versions()
        self._hostname = socket.gethostname()
        
       
    def __str__(self):
        """
        Builds printable string of dependency check results.

        Returns
        -------
        text : str
            Dependency check results to pass to print statement.

        """
        
        text = f'Host: {self._hostname}\n'
        
        # build table of installed modules
        if len(self._modules_found) > 0:
            max_module_len = 0
            max_version_len = 0
            
            # figure out table width
            for module, version in self._modules_found.items():
                if len(module) > max_module_len:
                    max_module_len = len(module) + 1
            
                if len(version) > max_version_len:
                    max_version_len = len(version) + 1
            
            # add table header
            text += '\n'
            text += 'Installed Modules:\n'
            text += '\n'
            text += f"{'Module':{max_module_len}} | Version\n"
            text += '-' * (max_module_len + 1) + '+' + '-' * max_version_len + '\n'
            
            # add each row
            for module, version in self._modules_found.items():
                text += f'{module:{max_module_len}} | {version}\n'
            
        # build table of missing modules
        if len(self._modules_missing) > 0:
            max_module_len = 0
            
            # figure out table width
            for module in self._modules_missing:
                if len(module) > max_module_len:
                    max_module_len = len(module)
            
            # add table header
            text += '\n'
            text += 'Missing Modules:\n'
            text += '\n'
            text += 'Module\n'
            text += '-' * max_module_len + '\n'
            
            # add each row
            for module in self._modules_missing:
                text += f'{module}\n'
        else:
            text += '\n'
            text += 'No required modules missing.'
            
        return text
    
    
    def _list_python_files(self):
        """
        Builds a list of all '.py' files found in the project directory.

        Returns
        -------
        None.

        """
        
        if self._include_subs:
            file_list = list(self._path.glob('**/*.py'))
        else:
            file_list = list(self._path.glob('*.py'))
            
        self_path = Path(__file__)
        
        if self._self_ignore and self_path in file_list:
            file_list.remove(self_path)
            
        temp_file_list = file_list.copy()
        
        for file in temp_file_list:
            for sub in self._subs_to_ignore:
                # skip directory if doesn't actually exist
                if not sub.is_dir():
                    continue
                
                # PosixPath will throw exception if paths aren't relative
                try:
                    file.relative_to(sub)
                    file_list.remove(file)
                    break
                except ValueError:
                    pass
                
        self._file_list = file_list
    
    
    def _build_module_list(self):
        """
        Builds a list of all modules used in the project.

        Returns
        -------
        None.

        """
        
        modules = set()
        modules.add('python')   # also want to check python version
        
        for file_path in self._file_list:
            with open(file_path) as file:
                for line in file:
                    # break each line into words
                    words = line.split()
                    
                    # empty line, skip to next
                    if not len(words):
                        continue
                    
                    # check if 'import' appears on an uncommented line
                    if 'import' in words and words[0] != '#':
                        # relevant 'import' should appear as word 0 or 2
                        if words.index('import') > 2:
                            continue
                        
                        # skip the line if it includes the prefix to ignore
                        if line.find(self._ignore_prefix) >= 0:
                            continue
                        
                        # figure out if the module name should come after an 
                        # 'import' or 'from'
                        if 'from' in words:
                            module_index = words.index('from') + 1
                            
                            # double check it isn't a local module nested in
                            # a subdirectory
                            if words[module_index + 2].startswith(self._ignore_prefix):
                                continue
                        else:
                            module_index = words.index('import') + 1
                        
                        # no more words on the line, skip to next
                        if module_index < len(words):
                            module = words[module_index]
                        else:
                            continue
                        
                        # check if import is a module subpackage and extract 
                        # parent module
                        if module.find('.') > 0:
                            module = module[:module.find('.')]
                        
                        # check the module isn't internal to project and should
                        # be ignored
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
        Checks whether each module is installed and gathers version information.

        Returns
        -------
        None.
        """
        
        D = {}
        missing = set()
        
        for module in self._required_modules:
            # python requires special version check
            if module.lower() == 'python':
                D['python'] = self._get_python_version()
                continue
            
            # try import module, if successful then check for version info,
            # otherwise catch the exception
            try: 
                loaded_module = importlib.import_module(module)
                
                if hasattr(loaded_module,'__version__'):
                    D[module] = loaded_module.__version__
                else:
                    D[module] = 'unknown'
            except ModuleNotFoundError:
                missing.add(module)
                
        self._modules_found = D
        self._modules_missing = missing
      
        
    def _get_python_version(self):
        """
        Checks the Python interpreter version running on the host system.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        
        return platform.python_version()  
    
    
    def get_hostname(self):
        """
        Returns the name of the host system.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        
        return self._hostname    
    
    
    def check(self):
        """
        Checks if dependencies are met.

        Returns
        -------
        bool
            True if no modules are missing, False otherwise.

        """
        
        return len(self._modules_missing) == 0
    
    
    def get_missing_modules(self):
        """
        Returns list of missing modules.

        Returns
        -------
        list of str
            Missing modules.

        """
        
        return list(self._modules_missing)
    
    
    def get_system_config(self):
        """
        Returns dictionary keyed by installed modules with version as value. 

        Returns
        -------
        dict
            {module as str : version as str}.

        """
        
        return self._modules_found

    
    def get_file_list(self):
        """
        Returns a list of all '.py' source files found.

        Returns
        -------
        list of str
            List of '.py' files.

        """
        
        return self._file_list

    
    def get_module_list(self):
        """
        Returns a list of modules required by the project.

        Returns
        -------
        list of str
            Required modules.

        """
        
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
    dependencies = Dependencies(root_path, ignore_module_prefix=local_module_prefix, include_subs=True, subs_to_ignore=['scratch'])
    
    print('Source code files examined')
    print('--------------------------')
    for file in dependencies.get_file_list():
        print(file)
    print()
    print()
    
    print('Modules referenced')
    print('------------------')
    for module in dependencies.get_module_list():
        print(module)
    print()
    print()
    
     
    print('System compatibility')  
    print('--------------------')
    print(dependencies)
    print()