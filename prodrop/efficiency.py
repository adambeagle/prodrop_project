"""
efficiency.py
Author: Adam Beagle

PURPOSE:
    Any experiments to test efficiency of any module should be placed here.
    The module name avoids the test_* format so it will not be run in the
    normal test suite. The thought behind that is some tests here may
    be quite lengthy if they involve lots of runs to get a good average,
    and these tests do not necessarily involve assertions.
"""
from parsetree import ParseTree
from util import itertreelines, Timer

def test_end_node_caching():
    """
    Report execution time to build and search a tree with end-node caching
    off, then on.

    Total number of runs and searches, as well as which file the test
    tree is taken from can be varied.
    """
    def do_test(caching):
        with timer:
            for r in range(runs):
                tree = ParseTree(lines, caching)
                for s in range(searches):
                    tree.search(tag='PUNC', word='.')

        caching_word = 'WITH' if caching else 'NO'
        print('\n{0} CACHING'.format(caching_word)) 
        print('Time for {0} runs, {1} searches per run:\n {2:.3f}s'.format(
            runs, searches, timer.total_time)
        )
        print(' {0:.5f}ms / run'.format(1000*timer.total_time / runs))
        if searches:
            print(' {0:.5f}ms / search'.format(
                (1000*timer.total_time / runs) / searches))
        
    timer = Timer()
    runs = 100
    searches = 50
    filepath = '../treebank_data/sample_tree_large.parse'
    lines = None

    # Get one tree (generators not indexable, so break after 1)
    for t in itertreelines(filepath):
        lines = t[:]
        break

    print('==================================\nBegin end node caching test...')
    do_test(0)
    do_test(1)

###############################################################################
if __name__ == '__main__':
    test_end_node_caching()
