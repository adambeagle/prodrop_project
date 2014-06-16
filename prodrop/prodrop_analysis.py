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

def get_previous_siblings(node):
    """
    Yield the prior siblings of a tree as found in a depth-first traversal.
    """
    for child in node.parent.children:
        if child == node:
            return

        yield child

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
    tree_with_prodrop_count = 0 # At least 1 pro-drop
    verbs = {}
    ignored_tags = {}
    failure_trees = set()
    allowed_verb_tags = ('IV', 'PV', 'CV', 'ADJ.VN',
        'NOUN.VN', 'PSEUDO_VERB', 'VERB', 'DET+ADJ.VN'
    )
    assoc_verb_found = False

    print('Starting pro-drop search... ', end='')
    for tree in treesfunc(INPUT_PATH):
        tree_count += 1
        has_prodrop = False
        
        for pdnode in iterprodrops(tree):
            assoc_verb_found = False
            has_prodrop = True
            prodrop_count += 1
            sibtags = []

            # Only check siblings above parent, as subject always follows
            # verb as per the guidelines.
            for sib in get_previous_siblings(pdnode.parent):
                sibtags.append(sib.tag)

                for tag in allowed_verb_tags:
                    if sib.tag.startswith(tag):
                        assoc_verb_found = True
                        prodrop_with_verb_count += 1
                        update_distinct_counts(verbs, sib.word)
                        break

            if not assoc_verb_found:
                for t in sibtags:
                    update_distinct_counts(ignored_tags, t)
                failure_trees.add(tree)

        tree_with_prodrop_count += 1 if has_prodrop else 0
  
    print('Complete.')
    _write_report(verbs, tree_count, prodrop_count,
        prodrop_with_verb_count, ignored_tags, failure_trees,
        tree_with_prodrop_count, allowed_verb_tags
    )
    
def _write_report(verbs, tree_count, prodrop_count, prodrop_with_verb_count,
                  ignored_tags, failure_trees, tree_with_prodrop_count,
                  allowed_verb_tags):
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
        print_and_write(
            'Trees with at least 1 pro-drop: {0}'.format(tree_with_prodrop_count)
        )
        print_and_write(
            'Trees with failed sibling lookup: {0}\n'.format(len(failure_trees))
        )
        print_and_write('Pro-drops found: {0}'.format(prodrop_count))
        print_and_write('Pro-drops with associated verb found: {0}'.format(
            prodrop_with_verb_count
        ))
        print_and_write('Distinct associated verbs found: {0}'.format(len(verbs)))
        print_and_write(
            'Distinct excluded sibling tags: {0}'.format(len(ignored_tags))
        )

        outfile.write('\nALLOWED VERB TAG BASES\n=======================\n')
        for tag in allowed_verb_tags:
            outfile.write('  {0}\n'.format(tag))
        
        outfile.write('\nVERB OCCURENCES\n===============\n')
        for v in sorted(verbs, key=lambda x: verbs[x], reverse=True):
            outfile.write('{0:>5}'.format(verbs[v]))
            outfile.write('  :  {0}\n'.format(v))

        outfile.write('\nEXCLUDED PRO-DROP SIBLING TAGS\n')
        outfile.write('====================================\n')
        for tag in sorted(
            ignored_tags, key=lambda x: ignored_tags[x], reverse=True
        ):
            outfile.write('{0:>5}'.format(ignored_tags[tag]))
            outfile.write('  :  {0}\n'.format(tag))

##        outfile.write('\nTREES WITH PRO-DROPS WITH NO ASSOC. VERB FOUND:\n')
##        outfile.write('==================================================\n')
##        for tree in failure_trees:
##            outfile.write(tree.treebank_notation)
##            outfile.write('\n')
                

    print('\nReport written to', path)

###############################################################################
if __name__ == '__main__':
    try:
        with Timer() as timer:
            prodrop_verb_association(itertrees_dir)
    finally:
        print('Time: {0:.3f}s'.format(timer.total_time))

