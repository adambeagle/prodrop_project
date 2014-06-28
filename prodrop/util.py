"""
util.py
Author: Adam Beagle

DESCRIPTION:
    Utility module. Contains functions and classes that are useful and reusable
    throughout the project.
"""
from datetime import datetime
from os import listdir
from os.path import join, normpath, splitext
import time

from parsetree import ParseTree

def get_files_by_ext(directory, ext, prepend_dir=False):
    """
    Return list of files in 'directory' whose extensions match 'ext.'
    Matching is case-insensitive.

    If prepend_dir is True, directory will be prepended to each filename in
    list. Otherwise, the filenames alone are returned.
    """
    files = []

    # Force ext to have leading period and be lowercase
    ext = '{0}{1}'.format(
        '.' if not ext[0] == '.' else '',
        ext.lower()
    )

    # For each file in 'directory' check if the file's extension matches
    # 'ext' and append filename to 'files' if so.
    for f in listdir(directory):
        if splitext(f)[1].lower() == ext:
            if prepend_dir:
                files.append(normpath(join(directory, f)))
            else:
                files.append(f)

    return files

def itertreelines(filepath):
    """
    Yield each set of lines from .parse file given by filepath that
    represent a single parse tree. Yielded values are lists of strings,
    each a line as found in the file given by filepath. Line-end characters
    are retained.
    """
    tree_start = '(TOP '
    tree_end = '\n'
    current_tree_lines = []
    
    with open(filepath, encoding='utf8') as f:
        current_tree_lines = []
        
        for line in f:

            # Starting line; Begin new list
            if line.startswith(tree_start):
                current_tree_lines = [line]

            # Normal (non start or end) line; Append to list
            elif not line.startswith(tree_end):
                current_tree_lines.append(line)

            # End; Yield list if not empty
            else:
                if current_tree_lines:
                    yield current_tree_lines
                    current_tree_lines = []

def itertrees(filepath, cache_end_nodes=1):
    """
    Yield each tree of the .parse file given by 'path' as a
    parsetree.ParseTree object.
    """
    for treelines in itertreelines(filepath):
        yield ParseTree(treelines, cache_end_nodes)

def itertrees_dir(path, **kwargs):
    """
    Yield every parse tree of every .parse file found in the directory
    given by path. Trees are yielded as parsetree.ParseTree objects.

    .parse files in nested directories of path are not searched.
    """
    for filepath in get_files_by_ext(path, '.parse', prepend_dir=True):
        for tree in itertrees(filepath, **kwargs):
            yield tree

def timestamp_now():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H.%M.%S")

def update_distinct_counts(d, key, n=1):
    """
    Set d[key] = n if key does not already exist in d, otherwise
    increments value of d[key] by n. Useful when storing counts of
    distinct items.
    """
    if key in d:
        d[key] += n
    else:
        d[key] = n

################################################################################
class TimerError(Exception):
    pass

class Timer():
    """
    Defines a timer that can be used as part of a 'with' statement
    to time any block of code.

    ATTRIBUTES:
      * elapsed_time (read-only)
      * total_time (read-only)
    """
    def __init__(self):
        self._startTime = None
        self._endTime = None
        self._interval = None

    def __enter__(self):
        self._startTime = time.clock()
        return self

    def __exit__(self, *args):
        self._endTime = time.clock()
        self._interval = self._endTime - self._startTime

    @property
    def elapsed_time(self):
        """Return time elapsed (in sec) since the timer was entered."""
        try:
            return time.clock() - self._startTime
        except TypeError:
            raise TimerError(
                'Timer must be started before elapsed_time can have a value.'
            )

    @property
    def total_time(self):
        """Return total time from enter to exit of timer, in seconds."""
        return self._interval
