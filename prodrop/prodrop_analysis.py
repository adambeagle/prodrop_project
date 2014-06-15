"""
prodrop_analysis.py
Author: Adam Beagle

PURPOSE:
    Handles the primary objective of the project, i.e. gathering and analyzing
    pro-drop sentences.
"""
from constants import TREEBANK_DATA_PATH
from parsetree import ParseTree
from util import itertrees, Timer

INPUT_PATH = '../treebank_data/testdata/simple_trees.txt'

def get_prodrops(tree):
    """
    Return list of pro-drop nodes in a single ParseTree.
    
    In treebank notation, these are (-NONE- *) nodes whose parent is a variant
    of NP-SBJ.
    """
    prodrops = []

    # Find nodes 
    for node in tree.search(tag='-NONE-', word='*', parent='NP-SBJ',
        parent_flag=tree.STARTSWITH
    ):
        for sibling in tree.get_siblings(node.parent):
            if sibling.tag.startswith('IV'):
                prodrops.append(node)

    return prodrops

def report_prodrops(tree):
    """
    """
    count = 0
    
    for node in tree.search(tag='-NONE-', word='*', parent='NP-SBJ',
        parent_flag=tree.STARTSWITH
    ):
        for sibling in tree.get_siblings(node.parent):
            if sibling.tag.startswith('IV'):
                count += 1
                print('Pro-drop found!')
                print('Verb tag: {0}'.format(sibling.tag))
                print('Verb: {0}\n'.format(sibling.word))

    return count

###############################################################################
if __name__ == '__main__':
    with Timer() as timer:
        count = 0
        prodrop_count = 0
        for tree in itertrees(INPUT_PATH, cache_end_nodes=1):
            prodrop_count += report_prodrops(tree)
            count +=1

        print('===================================')
        print('Total trees scanned: {0}'.format(count))
        print('Pro-drops found: {0}'.format(prodrop_count))
        print('Time: {0:.3f}s'.format(timer.elapsed_time))
