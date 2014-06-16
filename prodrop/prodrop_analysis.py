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

# TODO refactor
def prodrop_verb_association(treesfunc):
    """
    Analyze every tree in INPUT_PATH for pro-drop nodes and find an
    associated verb for each.

    Counts of distinct associated verbs are gathered and printed.

    A report is written to OUTPUT_PATH with results from the analysis.
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

            # Store sibling tags for reporting if no associated verb
            # found matching allowed tags. 
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

def _print_and_write(outfile, description, value, nl=False):
    """
    Designed with _write_report specifically in mind; Not for general use.
    """
    s = '{0}{1:>5} - {2}'.format('\n' if nl else '', value, description)
    print(s)
    outfile.write(s)
    outfile.write('\n')

def _write_report(verbs, tree_count, prodrop_count, prodrop_with_verb_count,
                  ignored_tags, failure_trees, tree_with_prodrop_count,
                  allowed_verb_tags):
    """
    Write report of results from prodrop_verb_association to
    OUTPUT_PATH/report (timestamp).txt
    """
    path = normpath(join(OUTPUT_PATH,
        'report {0}.txt'.format(timestamp_now())
    ))
    
    with open(path, 'w', encoding='utf8') as outfile:
        print('')
        _print_and_write(outfile, 'Trees searched', tree_count)
        _print_and_write(outfile, 'Trees with at least 1 pro-drop',
                         tree_with_prodrop_count)
        _print_and_write(outfile, 'Trees with failed sibling lookup',
                         len(failure_trees))
        _print_and_write(outfile, 'Total pro-drops found', prodrop_count, nl=1)
        _print_and_write(outfile, 'Pro-drops with associated verb found',
                         prodrop_with_verb_count)
        _print_and_write(outfile, 'Distinct associated verbs found',
                         len(verbs), nl=1)
        _print_and_write(outfile, 'Distinct excluded sibling tags',
                         len(ignored_tags))

        _write_container(outfile, 'Allowed verb tag bases', allowed_verb_tags)
        _write_container(outfile,
            'Sibling tags of pro-drops with no associated verb found',
            ignored_tags)
        _write_container(outfile, 'Verb occurrences', verbs)
        

    print('\nReport written to', path)

def _write_container(outfile, heading, c):
    """
    Pretty-print a sequence or a dict.
    Designed with _write_report specifically in mind; Not for general use.
    """
    outfile.write('\n{0}\n{1}\n'.format(heading, '='*len(heading)))

    if isinstance(c, dict):
        for key in sorted(c, key=lambda x: c[x], reverse=True):
            outfile.write('{0:>5}'.format(c[key]))
            outfile.write('  :  {0}\n'.format(key))
    else:
        for x in c:
            outfile.write('  {0}\n'.format(x))
###############################################################################
if __name__ == '__main__':
    try:
        with Timer() as timer:
            prodrop_verb_association(itertrees_dir)
    finally:
        print('Time: {0:.3f}s'.format(timer.total_time))

