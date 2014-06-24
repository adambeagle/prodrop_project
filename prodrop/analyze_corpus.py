"""
analyze_corpus.py
Author: Adam Beagle
"""
from os.path import join, normpath

from constants import TREEBANK_DATA_PATH
from subjectverbanalysis import CombinedAnalyzer
from util import Timer, timestamp_now

INPUT_PATH = TREEBANK_DATA_PATH
OUTPUT_PATH = '../reports/' # Must be directory; Filename auto-generated

###############################################################################
if __name__ == '__main__':
    timer = Timer()
    
    csvpath = normpath(join(
        OUTPUT_PATH,
        'verbs {0}.csv'.format(timestamp_now())
    ))

    with timer:
        ca = CombinedAnalyzer(INPUT_PATH)
        ca.do_analysis()
        ca.print_report_basic()

        with open(csvpath, 'w', encoding='utf8') as outfile:
            ca.write_csv(outfile)

    print('\nTime: {0:.3f}s'.format(timer.total_time))
