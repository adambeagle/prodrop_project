"""
find_simple_sentence.py
Author: Adam Beagle

DESCRIPTION:
   Locates the simplest (i.e. fewest tree lines) pro-drop sentences in .parse
   files in a directory given by INPUT_PATH.
"""
from single_asterisk_lines import get_files_by_ext

INPUT_PATH = '../treebank_data/00/'
OUTFILE = 'simple.txt'

def itertrees(path):
    """
    Yield each tree of the .parse file given by 'path.'
    Trees are given as lists of strings.
    """
    start = '(TOP '
    end = '\n'
    current_tree = []
    
    with open(path) as f:
        for line in f:
            if line.startswith(start):
                current_tree = [line]
            elif not line.startswith(end):
                current_tree.append(line)
            else:
                if current_tree:
                    yield current_tree
                    current_tree = []

###############################################################################
if __name__ == '__main__':
    search_phrase = '(NP-SBJ (-NONE- *))'
    files = get_files_by_ext(INPUT_PATH, '.parse', prepend_dir=True)

    for path in files:
        for tree in itertrees(path):
            pass
                
