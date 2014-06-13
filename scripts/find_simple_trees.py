"""
find_simple_trees.py
Author: Adam Beagle

PURPOSE:
    Find short, simple trees that include a pro-drop. These trees will be
    useful for learning/testing purposes.

DESCRIPTION:
   Locates trees with a pro-drop in .parse files in a directory given by
   INPUT_PATH that are fewer than MAX_LINES in length, then writes these
   trees to OUTFILE. A maxiumum of MAX_TREES will be written.
"""
from os.path import basename

from constants import TREEBANK_DATA_PATH
from exceptions import MissingParseFilesError
from util import get_files_by_ext, itertrees

INPUT_PATH = TREEBANK_DATA_PATH
OUTFILE = 'simple_trees.txt'
MAX_LINES = 6
MAX_TREES = 999

def phrase_in_tree(tree, phrase):
    """
    Return True if 'phrase' found in any position of any line of 'tree.'
    """
    for line in tree:
        if phrase in line:
            return True

    return False

def report_short_trees(path, search_phrase, trees_found):
    for tree in itertrees(path):
        if phrase_in_tree(tree, search_phrase):
            
            # If tree meets criteria, write it to outfile
            if len(tree) <= MAX_LINES and trees_found < MAX_TREES:
                outfile.write('{0}\n'.format(''.join(tree)))
                trees_found += 1

    return trees_found

###############################################################################
if __name__ == '__main__':
    search_phrase = '(NP-SBJ (-NONE- *))'
    files = get_files_by_ext(INPUT_PATH, '.parse', prepend_dir=True)
    trees_found = 0
    
    if not files:
        raise MissingParseFilesError(
            'No .parse files found in {0}'.format(INPUT_PATH)
        )

    print('Starting search...', end='')
    with open(OUTFILE, 'w', encoding='utf8') as outfile:
        for path in files:
            trees_found = report_short_trees(
                path, search_phrase, trees_found
            )

            if trees_found >= MAX_TREES:
                break
                
    print(' Search complete. {0} trees found.'.format(trees_found))
    
    if not trees_found:
        print('\nNo pro-drop trees found with length <= {0}'.format(
            MAX_LINES)
        )
    else:
        print('\nOutput written to {0}'.format(OUTFILE))
