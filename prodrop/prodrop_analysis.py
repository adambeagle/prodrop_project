"""
prodrop_analysis.py
Author: Adam Beagle

PURPOSE:
    Handles the primary objective of the project, i.e. gathering and analyzing
    pro-drop sentences.
"""
from constants import TREEBANK_DATA_PATH
from parsetree import ParseTree
from util import itertrees, itertrees_dir, Timer

INPUT_PATH = TREEBANK_DATA_PATH #'../treebank_data/testdata/simple_trees.txt'
OUTPUT_PATH = 'report.txt'
PRODROP_WORD_PATTERN = '^\*(?:-\d+)?$'

def iterprodrops(tree):
    """
    Yield pro-drop nodes, i.e. (-NONE- *) nodes whose parent is a variant
    of NP-SBJ.
    """
    return (node for node in tree.search(
        tag='-NONE-',
        word=PRODROP_WORD_PATTERN,
        word_flag=tree.REMATCH,
        parent_tag='NP-SBJ',
        parent_flag=tree.STARTSWITH)
    )

def prodrop_verb_association(treesfunc):
    """
    """
    prodrop_count = 0
    prodrop_with_verb_count = 0
    tree_count = 0
    verbs = {}

    print('Starting pro-drop search... ', end='')
    for tree in treesfunc(INPUT_PATH):
        tree_count += 1
        for pdnode in iterprodrops(tree):
            prodrop_count += 1
            for sibling in tree.get_siblings(pdnode.parent):
                if sibling.tag.startswith('IV'):
                    prodrop_with_verb_count += 1
                    _update_verbs(verbs, sibling.word)

    print('Complete.')
    _write_report(verbs, tree_count, prodrop_count, prodrop_with_verb_count)
    
def _write_report(verbs, tree_count, prodrop_count, prodrop_with_verb_count):
    """ """
    outfile = open(OUTPUT_PATH, 'w', encoding='utf8')
    
    def print_and_write(s):
        print(s)
        outfile.write(s)
        outfile.write('\n')

    print('')
    print_and_write('Trees searched: {0}'.format(tree_count))
    print_and_write('Pro-drops found: {0}'.format(prodrop_count))
    print_and_write('Pro-drops with associated verb found: {0}'.format(
        prodrop_with_verb_count
    ))
    print_and_write('Distinct verbs found: {0}'.format(len(verbs)))
    
    outfile.write('\nVERB OCCURENCES\n===============\n')
    for v in sorted(verbs, key=lambda x: verbs[x], reverse=True):
        outfile.write('{0:>2}'.format(verbs[v]))
        outfile.write('  :  {0:<2}\n'.format(v))

    
    outfile.close()

    print('\nReport written to {0}'.format(OUTPUT_PATH))

def _update_verbs(verbs, newverb):
    if newverb in verbs:
        verbs[newverb] += 1
    else:
        verbs[newverb] = 1

###############################################################################
if __name__ == '__main__':
    try:
        with Timer() as timer:
            prodrop_verb_association(itertrees_dir)
    finally:
        print('Time: {0:.3f}s'.format(timer.total_time))

