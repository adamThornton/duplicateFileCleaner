from datetime import datetime
import os
import re
import sys
import hashlib

log_enabled = False
dir_count: int = 0
file_count: int = 0

def log(message: str):
    if log_enabled:
        print(message)


class DuplicateFileCleaner:

    def __init__(self, is_test):
        self.is_test = is_test
        self.current_file_number: int = 0
        self.hashes = {}

    def update_progress(self):
        self.current_file_number = self.current_file_number + 1
        print(f'##### {(self.current_file_number/file_count)*100}% #####', end='\r')

    def hashfile(self, path, blocksize = 65536):
        afile = open(path, 'rb')
        hasher = hashlib.md5()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        return hasher.hexdigest()

    def findDup(self, parentFolder):
        # Dups in format {hash:[names]}
        dups = {}
        for dirName, subdirs, fileList in os.walk(parentFolder):
            print('Scanning %s...' % dirName)
            for filename in fileList:
                # Get the path to the file
                path = os.path.join(dirName, filename)
                # Calculate hash
                file_hash = self.hashfile(path)
                # Add or append the file path
                if file_hash in dups:
                    dups[file_hash].append(path)
                else:
                    dups[file_hash] = [path]
        return dups

    def duplicateFileCleaner(self, directory):
        errors = []
        for dirpath,_,filenames in os.walk(directory):
            log((f'##### Checking in {dirpath}'))
            for f in filenames:
                fullPath = os.path.abspath(os.path.join(dirpath, f))
                self.update_progress()
        print(errors)


if __name__ == '__main__':
    dir = "\\\\SYNOLOGYNAS\photo\sylvia"
    if not os.path.isdir(dir):
        print(f'Path not found: {dir}')
        exit()
    is_test = True

    start = datetime.now()
    for root, dirs, file_names in os.walk(dir):
        log(f"{root}")
        dir_count = dir_count + 1
        for f in file_names:
            file_count = file_count + 1
    print(f'Total dirs: {dir_count}')
    print(f'Total files: {file_count}')

    fixer = DuplicateFileCleaner(is_test)
    for root, dirs, file_names in os.walk(dir):
        fixer.duplicateFileCleaner(root)
    print(f'Elapsed time: {datetime.now() - start}')
