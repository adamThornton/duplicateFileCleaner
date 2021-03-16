from datetime import datetime
import os
import re
import sys
import hashlib
import ntpath
import shutil

log_enabled = False

def log(message: str):
    if log_enabled:
        print(message)


class DuplicateFileCleaner:

    def __init__(self, is_test, total_files):
        self.is_test = is_test
        self.total_files = total_files
        self.errors = []
        self.current_file_number: int = 0
        self.hashes = {}
        self.files_by_size = {}
        self.duplicates = {}

    def update_progress(self):
        self.current_file_number = self.current_file_number + 1
        percent = str(round((self.current_file_number/self.total_files)*100, 3))
        if ('100' in percent):
            print('##### ' + 'Done'.center(10) + ' #####')
        else:
            print('##### ' + f'{percent}%'.center(10) + ' #####', end='\r')

    def hashfile(self, path, blocksize = 65536):
        afile = open(path, 'rb')
        hasher = hashlib.md5()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        return hasher.hexdigest()

    def buildFileListBySize(self, directory):
        for dirpath,_,filenames in os.walk(directory):
            log((f'##### Checking in {dirpath}'))
            for f in filenames:
                full_path = os.path.abspath(os.path.join(dirpath, f))
                size = os.path.getsize(full_path)
                if size in self.files_by_size:
                    if full_path not in self.files_by_size[size]:
                        self.files_by_size[size].append(full_path)
                else:
                    self.files_by_size[size] = [full_path]
                self.update_progress()
    
    def reduceDuplicatesBySize(self):
        self.duplicates = dict(filter(lambda s: len(s[1]) > 1, self.files_by_size.items()))
        print(f'Found {len(self.duplicates)} duplicates by file size.')
        return self.duplicates
    
    def reduceDuplicatesByHash(self):
        current_dup_number = 1
        non_dups = []
        for dup in self.duplicates.items():
            hashes = list()
            to_remove = []
            i = 0
            for filename in dup[1]:
                hashes.append(self.hashfile(filename))
                i = i + 1
            for i, h in enumerate(hashes):
                if hashes.count(h) == 1:
                    to_remove = dup[1][i]
            if to_remove:
                temp = [dup[0], list(filter(lambda s: s not in to_remove, dup[1]))]
                if len(temp[1]) > 1:
                    dup = tuple(temp)
                    self.duplicates[dup[0]] = dup[1]
                else:
                    non_dups.append(dup[0])
            percent = str(round((current_dup_number/len(self.duplicates))*100, 3))
            print('##### ' + f'{percent}%'.center(10) + ' #####', end='\r')
            current_dup_number = current_dup_number + 1
        
        # Remove the single file items from the duplicates dictionary.
        [self.duplicates.pop(key) for key in non_dups]
        print('##### ' + 'Done'.center(10) + ' #####')
        print(f'Found {len(self.duplicates)} by hash.')
        return self.duplicates

    def clean(self, target_location, auto_move: bool = False):
        for dup in self.duplicates.items():
            to_delete = []
            print('Enter the number for the file to keep.  All others will be moved.')
            print('\n'.join('{}: {}'.format(*k) for k in enumerate(dup[1])))
            value = '0'
            if not auto_move:
                value = input('Choice: ')
                if value == '':
                    value = '0'
            dup[1].pop(int(value))
            to_delete = to_delete + dup[1]

            for filepath in to_delete:
                print(f"Moving: {filepath}")
                if not is_test:
                    if os.path.exists(filepath):
                        filename = ntpath.basename(filepath)
                        shutil.move(filepath, f'{target_location}\\{filename}')
                    else:
                        print(f"The file does not exist: {filepath}")

if __name__ == '__main__':
    search_root = ".\\test"
    target_location = "C:\\ToDelete\\"
    auto_move = False
    if not os.path.isdir(search_root):
        print(f'Path not found: {search_root}')
        exit()
    is_test = False

    start = datetime.now()
    file_count = 0
    dir_count = 0
    for root, dirs, file_names in os.walk(search_root):
        for dirpath,_,filenames in os.walk(root):
            log(f"{root}")
            dir_count = dir_count + 1
            for f in filenames:
                file_count = file_count + 1
    print(f'Total dirs: {dir_count}')
    print(f'Total files: {file_count}')

    fixer = DuplicateFileCleaner(is_test, file_count)
    for root, dirs, file_names in os.walk(search_root):
        fixer.buildFileListBySize(root)
        
    print('Finding duplicates by file size.')
    dups = fixer.reduceDuplicatesBySize()
    print('Reducing file size matches with hash comparison.')
    dups = fixer.reduceDuplicatesByHash()
    print(f'### Errors: \n{fixer.errors}')
    print(f'Elapsed time: {datetime.now() - start}')
    fixer.clean(target_location, auto_move)
