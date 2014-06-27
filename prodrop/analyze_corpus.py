"""
analyze_corpus.py
Author: Adam Beagle
"""
from os import mkdir
from os.path import join, normpath

from constants import TREEBANK_DATA_PATH
from subjectverbanalysis import CombinedAnalyzer
from util import Timer, timestamp_now

INPUT_PATH =  TREEBANK_DATA_PATH #'../treebank_data/00/ann_0001.parse'#
OUTPUT_PATH = '../reports/' # Must be directory; Filename auto-generated

###############################################################################
if __name__ == '__main__':
    timer = Timer()
    nowstamp = timestamp_now()

    mkdir(normpath(join(OUTPUT_PATH, nowstamp)))
    
    csvpath = normpath(join(
        OUTPUT_PATH,
        nowstamp,
        'verbs.csv'.format(nowstamp)
    ))

    pd_report_path = normpath(join(
        OUTPUT_PATH,
        nowstamp,
        'pro-drop-report.txt'.format(nowstamp)
    ))
    
    npd_report_path = normpath(join(
        OUTPUT_PATH,
        nowstamp,
        'non-pro-drop report.txt'.format(nowstamp)
    ))

    with timer:
        ca = CombinedAnalyzer(INPUT_PATH)
        ca.do_analysis()
        ca.print_report_basic()

        with open(pd_report_path, 'w', encoding='utf8') as pdout:
            with open(npd_report_path, 'w', encoding='utf8') as npdout:
                ca.write_report_full(pdout, npdout)

        with open(csvpath, 'w', encoding='utf8') as outfile:
            ca.write_csv(outfile)

    print('\nTime: {0:.3f}s'.format(timer.total_time))
