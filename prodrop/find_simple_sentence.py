"""
find_simple_sentence.py
Author: Adam Beagle

DESCRIPTION:
   Locates the simplest (i.e. fewest tree lines) pro-drop sentences in .parse
   files in a directory given by INPUT_PATH.
"""
from os.path import basename

from exceptions import MissingParseFilesError, NoTreesFoundError
from util import get_files_by_ext, itertrees

INPUT_PATH = '../treebank_data/00/'

def phrase_in_tree(tree, phrase):
    """
    Return True if 'phrase' found in any position of any line of 'tree.'
    """
    for line in tree:
        if phrase in line:
            return True

    return False

###############################################################################
if __name__ == '__main__':
    search_phrase = '(NP-SBJ (-NONE- *))'
    files = get_files_by_ext(INPUT_PATH, '.parse', prepend_dir=True)
    shortest = None
    shortest_len = 9999
    shortest_file = None

    if not files:
        raise MissingParseFilesError(
            'No .parse files found in {0}'.format(INPUT_PATH)
        )

    print('Starting search...', end='')
    for path in files:
        for tree in itertrees(path):
            if phrase_in_tree(tree, search_phrase):
                tree_len = len(tree)
                if tree_len < shortest_len:
                    shortest = tree[:]
                    shortest_len = tree_len
                    shortest_file = basename(path)

    if shortest == None:
        raise NoTreesFoundError(
            'No parse trees found in {0}'.format(INPUT_PATH)
        )

    print(' Search complete.')
    print('\nSHORTEST TREE:')
    for line in shortest:
        print(line, end='')

    print('\nTree found in file {0}'.format(shortest_file))

                
                
                
