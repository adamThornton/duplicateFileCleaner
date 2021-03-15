# Duplicate File Cleaner
Scans a provide folder and subfolders to find duplicate files.

## Approach: 

    1. Makes a dictionary of file sizes with a list of files for each file size.  This identifies duplicates by file size.
    2. Iterates through the dictionary and generates hashes on the file size based list of duplicates and removes items with a hash that only appears once.  This removes files from the dictionary that were a file size match but, indeed, are not an actual duplicate.
    3. The remain list is the list of duplicates and is then interated again to move the files to a staging location prior to the user deleting. A CLI will allow the user to choice which of the duplicates to keep.  The other will be moved.

## Usage:
    1. Set **search_root** to the path to start searching from.
    2. Set **target_location** to the path to where files will be moved to.
    3. Set **is_test** to test the behavior of the algorithm without moving the files.
    4. ***Optional*** Set **auto_move** if you don't want to choose the file to keep from the duplicates and instead automatically keep the first one and move the rest.
    5. ***Optional*** Set **log_enabled** to print more verbose messages in the terminal during execution.