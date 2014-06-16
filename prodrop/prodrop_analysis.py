"""
prodrop_analysis.py
Author: Adam Beagle

PURPOSE:
    Handles the primary objective of the project, i.e. gathering and analyzing
    pro-drop sentences.
"""
from os.path import join, normpath

from constants import TREEBANK_DATA_PATH
from parsetree import ParseTree
from util import itertrees, itertrees_dir, Timer, timestamp_now, update_distinct_counts

INPUT_PATH = TREEBANK_DATA_PATH #'../treebank_data/testdata/simple_trees.txt'
OUTPUT_PATH = '../reports/'
PRODROP_WORD_PATTERN = '^\*(?:-\d+)?$'

def get_previous_sibling(node):
    """
    Return the prior sibling of a tree as found in a depth-first traversal.
    """
    previous_sibling = None
    
    for child in node.parent.children:
        if child == node:
            return previous_sibling
        
        previous_sibling = child

    return None

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
    ignored_tags = {}
    found_associated_verb = False

    print('Starting pro-drop search... ', end='')
    for tree in treesfunc(INPUT_PATH):
        tree_count += 1
        
        for pdnode in iterprodrops(tree):
            found_associated_verb = False
            sibling_tags = {}
            prodrop_count += 1

            # Search for primary verb tag in each sibling of a pro-drop.
            for sibling in tree.get_siblings(pdnode.parent):
                if sibling.is_end:
                    update_distinct_counts(sibling_tags, sibling.tag)
                
                if sibling.tag.startswith('IV'):
                    prodrop_with_verb_count += 1
                    found_associated_verb = True
                    update_distinct_counts(verbs, sibling.word)
                    break

            # If no associated verb found, store all the sibling tags of the
            # pro-drop for the report.
            if not found_associated_verb:
                for tag in sibling_tags:
                    update_distinct_counts(
                        ignored_tags, tag, sibling_tags[tag]
                    )
  
    print('Complete.')
    _write_report(verbs, tree_count, prodrop_count,
        prodrop_with_verb_count, ignored_tags
    )
    
def _write_report(verbs, tree_count, prodrop_count,
                  prodrop_with_verb_count, ignored_tags):
    """ """
    path = normpath(join(OUTPUT_PATH,
        'report {0}.txt'.format(timestamp_now())
    ))
    
    def print_and_write(s):
        print(s)
        outfile.write(s)
        outfile.write('\n')

    with open(path, 'w', encoding='utf8') as outfile:
        print('')
        print_and_write('Trees searched: {0}'.format(tree_count))
        print_and_write('Pro-drops found: {0}'.format(prodrop_count))
        print_and_write('Pro-drops with associated verb found: {0}'.format(
            prodrop_with_verb_count
        ))
        print_and_write('Distinct associated verbs found: {0}'.format(len(verbs)))
        print_and_write(
            'Distinct excluded sibling tags: {0}'.format(len(ignored_tags))
        )
        
        outfile.write('\nVERB OCCURENCES\n===============\n')
        for v in sorted(verbs, key=lambda x: verbs[x], reverse=True):
            outfile.write('{0:>2}'.format(verbs[v]))
            outfile.write('  :  {0}\n'.format(v))

        outfile.write('\nEXCLUDED PRO-DROP SIBLING TAGS\n')
        outfile.write('====================================\n')
        for tag in sorted(
            ignored_tags, key=lambda x: ignored_tags[x], reverse=True
        ):
            outfile.write('{0:>4}'.format(ignored_tags[tag]))
            outfile.write('  :  {0}\n'.format(tag))

    print('\nReport written to', path)

###############################################################################
if __name__ == '__main__':
    try:
        with Timer() as timer:
            prodrop_verb_association(itertrees_dir)
    finally:
        print('Time: {0:.3f}s'.format(timer.total_time))

