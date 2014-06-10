"""
single_asterisk_lines.py
Author: Adam Beagle

PURPOSE:
    A fairly rudimentary starting point to begin examining the kinds of lines
    of the .parse files we'll be dealing with. It's likely essential that I
    understand the distinctions between lines such as (NP-SBJ (-NONE- *))
    and those such as (S (VP (NP-SBJ (-NONE- *-2)).

    A specific objective is to confirm that a line with a single asterisk
    always indicates a pro-drop sentence.

    Ideally, some of this code will be reusable as the project continues.

DESCRIPTION:
    Searches through all the .parse files in a directory (given by INPUT_PATH)
    for lines containing only a single asterisk. A distinct set of these lines
    (i.e. no repeats) is then written to the text file given by OUTFILE.

LIMITATIONS:
    1) Is there any case in which a line indicating a pro-drop can have
       multiple asterisks?

    2) Efficiency-wise this is okay, not great. Memory usage is good, as only a
       single file is loaded into memory at any time. Individual .parse
       files rarely exceed 100KB. Time-wise, the entire directory is searched
       in <2s, improvement will likely be needed as computation becomes more
       elaborate and to accomodate very large data sets.

    3) As of now, redundant closing parens are not accounted for when reporting
       distinct lines. This is not a big issue, it just clutters the results
       a little.

    4) Are lines such as (NP-OBJ (-NONE- *-2)) relevant or are we only
       concerned with NP-SBJ? Both types of lines are matched by this
       script.
       
INSTRUCTIONS:
    1) Set INPUT_PATH to the path to the directory in which the .parse files
       reside. This can be an absolute path (i.e. 'C:/treebank/00') or a
       relative path (i.e. '00' if this file is in the directory containing the
       '00' folder. If this file is in the same directory as the .parse files,
       use INPUT_PATH = ''

    2) If desired, change OUTFILE to a different name. This is the file to
       which the matching lines will be written.

    3) Invoke the script with python single_asterisk_lines.py at the command
       line.
"""
from os import listdir
from os.path import normpath, splitext
import re

from timer import Timer

INPUT_PATH = '../treebank_data/00/'
OUTFILE = 'out.txt'

def distinct_match_lines(path, pattern, group=0):
    """
    Return set of lines with a single asterisk, representing a pro-drop.
    Ignore leading and trailing whitespace in creating set.

    Assumes pattern designed for use with re.MULTILINE flag.
    """
    return set(file_matches(path, pattern, re.MULTILINE, group=group))

def distinct_match_lines_multi(paths, pattern, group=0):
    """
    Similar functionality to distinct_match_lines, but accepts iterable of
    multiple file paths.
    """
    matches = set()
    
    for path in paths:
        matches.update(distinct_match_lines(path, pattern, group=group))

    return matches
        
def file_matches(path, pattern, *flags, group=0):
    """
    Yield each match of regular expression 'pattern' as compared against
    each line of 'path.'

    Any flags present are passed to re.match.

    If 'group' is provided, that group of the match will be yielded
    (with re.match.group(group)). If not, the entire match string is returned.
    """
    with open(path, encoding='utf8') as f:
        for line in f:
            match = re.match(pattern, line, *flags)
            if match is not None:
                yield match.group(group)

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

###############################################################################
if __name__ == '__main__':
    pattern = r'^\s*([^\*]+\*[^\*]+)$'

    try:
        with Timer() as timer:
            with open(OUTFILE, 'w', encoding='utf8') as f:
                # Get list of files to search
                infiles = get_files_by_ext(INPUT_PATH, '.parse',
                    prepend_dir=True
                )

                # Search files and write matching lines
                for line in sorted(distinct_match_lines_multi(infiles, pattern,
                    group=1
                )):
                    f.write(line)

            print('Search complete.')
            print('Output written to \'{0}\''.format(OUTFILE))
            
    finally:
        print('Time:   {0:.3f}s'.format(timer.interval))
