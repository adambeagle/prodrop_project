"""
prodrop_analysis.py
Author: Adam Beagle

PURPOSE:
    Handles the primary objective of the project, i.e. gathering and analyzing
    pro-drop sentences.
"""
from constants import TREEBANK_DATA_PATH
from parsetree import ParseTree
from util import itertrees_dir, Timer

# TODO add more constraints?
# Could check if particular sibling nodes exist.
def get_prodrops(tree):
    """
    Return list of pro-drop nodes in a single ParseTree.
    
    In treebank notation, these are (-NONE- *) nodes whose parent is a variant
    of NP-SBJ.
    """
    prodrops = []
    for node in tree.search(tag='-NONE-', word='*'):
        if node.parent.tag.startswith('NP-SBJ'):
            prodrops.append(node)

    return prodrops

###############################################################################
if __name__ == '__main__':
    with Timer() as timer:
        count = 0
        prodrop_count = 0
        for tree in itertrees_dir(TREEBANK_DATA_PATH, cache_end_nodes=0):
            prodrop_count += len(get_prodrops(tree))
            count +=1

        print(count)
        print(prodrop_count)
        print('Time: {0}s'.format(timer.elapsed_time))
