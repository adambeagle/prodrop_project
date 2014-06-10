"""
util.py
Author: Adam Beagle

DESCRIPTION:
    Utility module. Contains functions and classes that are useful and reusable
    throughout the project.
"""
from os import listdir
from os.path import normpath, splitext
import time

def get_files_by_ext(directory, ext, prepend_dir=False):
    """
    Return list of files in 'directory' whose extensions match 'ext.'
    Matching is case-insensitive.

    If prepend_dir is True, directory will be prepended to each filename in
    list. Otherwise, the filenames alone are returned.
    """
    files = []

    if not ext[0] == '.':
        ext = '.{0}'.format(ext.lower())
    else:
        ext = ext.lower()

    directory = normpath(directory)
    
    for f in listdir(directory):
        if splitext(f)[1].lower() == ext:
            if prepend_dir:
                files.append('{0}\\{1}'.format(directory, f))
            else:
                files.append(f)

    return files

def itertrees(path):
    """
    Yield each tree of the .parse file given by 'path.'
    Trees are given as lists of strings.
    """
    start = '(TOP '
    end = '\n'
    current_tree = []
    
    with open(path, encoding='utf8') as f:
        for line in f:
            if line.startswith(start):
                current_tree = [line]
            elif not line.startswith(end):
                current_tree.append(line)
            else:
                if current_tree:
                    yield current_tree
                    current_tree = []

################################################################################
class Timer():
    """
    Defines a timer that can be used as part of a 'with' statement
    to time any block of code.

    ATTRIBUTES:
      * interval (read-only)
    """
    def __init__(self):
        self._interval = 0

    def __enter__(self):
        self._startTime = time.clock()
        return self

    def __exit__(self, *args):
        self._endTime = time.clock()
        self._interval = self._endTime - self._startTime

    @property
    def interval(self):
        return self._interval
