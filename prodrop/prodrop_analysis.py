"""
prodrop_analysis.py
Author: Adam Beagle

PURPOSE:
    Handles the primary objective of the project, i.e. gathering and analyzing
    pro-drop sentences.
"""
from os.path import isfile, isdir, join, normpath

from constants import TREEBANK_DATA_PATH
from exceptions import InputPathError
from parsetree import ParseTree
from sys import stdout
from util import (itertrees, itertrees_dir, Timer, timestamp_now,
    update_distinct_counts)

INPUT_PATH = TREEBANK_DATA_PATH
OUTPUT_PATH = '../reports/' # Must be directory; Filename auto-generated
PRODROP_WORD_PATTERN = '^\*(?:-\d+)?$'

###############################################################################
class ProdropAnalyzer():
    """ """
    def __init__(self, input_path):
        """input_path may be to directory or existing .parse file."""
        self._reset()
        self.allowed_verb_tags = ('IV', 'CV', 'PV', 'VERB', 'PSEUDO_VERB',
            'ADJ.VN', 'NOUN.VN', 'DET+ADJ.VN',
        )

        if isfile(input_path):
            self.itertrees = itertrees
        elif isdir(input_path):
            self.itertrees = itertrees_dir
        else:
            raise ImportPathError(
                "input_path is not a valid path to a directory or " +
                "existing file.\ninput_path: {0}".format(input_path)
            )

        self.input_path = input_path

    def prodrop_verb_association_analysis(self):
        """
        Analyze every tree in INPUT_PATH for pro-drop nodes and find an
        associated verb for each.

        Sets the following class-level attributes for use in reporting or
        further analysis:
            tree_count, tree_w_prodrop_count, prodrop_count, verb_counts,
            ignored_tag_counts, failure_trees
        """
        self._reset()
        
        print('Starting pro-drop search... ', end='')
        for tree in self.itertrees(self.input_path):
            self.tree_count += 1
            has_prodrop = False
            
            for pdnode in iterprodrops(tree):
                has_prodrop = True
                self.prodrop_count += 1
                sibtags = []

                result = self._check_siblings_for_verb(pdnode)
                if not result == True:
                    # Store sibling tags for reporting if no associated verb
                    # found matching allowed tags.
                    sibtags += result
                    for t in sibtags:
                        update_distinct_counts(self.ignored_tag_counts, t)
                    self.failure_trees.add(tree)

            self.tree_w_prodrop_count += 1 if has_prodrop else 0
                
        print('Complete.\n')

    def print_report_basic(self):
        self.write_report_basic(stdout)

    def print_report_full(self):
        self.write_report_full(stdout)

    def write_report_basic(self, out, rw=None):
        """ """
        if not rw:
            rw = ReportWriter(out)

        rw.write_int_stat('Trees searched', self.tree_count)
        rw.write_int_stat('Trees with at least 1 pro-drop',
                          self.tree_w_prodrop_count)
        rw.write_int_stat('Trees with failed sibling lookup',
                          len(self.failure_trees))
        
        rw.write_int_stat('Total pro-drops found', self.prodrop_count,
                          skipline=True)
        rw.write_int_stat('Pro-drops with associated verb found',
                          self.prodrop_w_verb_count)

        if self.prodrop_count > 0:
            perc = 100*self.prodrop_w_verb_count / self.prodrop_count
        else:
            perc = 0
            
        rw.write_float_stat('Percent pro-drops with associated verb',
                            perc, decprec=1, ntrail='%')
        rw.write_int_stat('Distinct associated verbs found',
                          len(self.verb_counts), skipline=True)
        rw.write_int_stat('Distinct excluded sibling tags',
                          len(self.ignored_tag_counts))

    def write_report_full(self, out):
        """ """
        rw = ReportWriter(out)
        rw.write_heading_toplevel('PRO-DROP VERB ASSOCIATION ANALYSIS REPORT')
        
        self.write_report_basic(out, rw)
        
        rw.write_sequence('Allowed verb tag bases', self.allowed_verb_tags)
        rw.write_dict(
            'Sibling tags of pro-drops with no associated verb found',
            self.ignored_tag_counts,
            sortonval=True,
            reverse=True
        )

        rw.write_dict('Verb occurrences', self.verb_counts,
            sortonval=True, reverse=True
        )

    def _check_siblings_for_verb(self, pdnode):
        """
        Check pro-drop node's NP-SBJ parent's siblings for a verb
        node whose tag starts with a value in self.allowed_verb_tags.

        If valid verb found, update self.verb_counts and
        self.prodrop_w_verb_count accordingly.

        If valid verb found, return True, otherwise list of tags
        of all visited siblings.
        """
        sibtags = []
        
        # Only check siblings above parent, as subject always follows
        # verb as per the guidelines.
        for sib in get_previous_siblings(pdnode.parent):
            sibtags.append(sib.tag)

            for tag in self.allowed_verb_tags:
                if sib.tag.startswith(tag):
                    self.prodrop_w_verb_count += 1
                    update_distinct_counts(self.verb_counts, sib.word)
                    
                    return True

        return sibtags
        
    def _reset(self):
        """ """
        self.tree_count = 0
        self.tree_w_prodrop_count = 0
        self.prodrop_count = 0
        self.prodrop_w_verb_count = 0
        self.verb_counts = {}
        self.ignored_tag_counts = {}
        self.failure_trees = set()

###############################################################################
class ReportWriter():
    """
    Facilitates writing formatted report lines for simple types and structures.

    ATTRIBUTES:
      * stream - What is written to. Can be reassigned at any time.
                 Expected to be standard stream (out, err) or open file.

    METHODS:
      * write_dict
      * write_float_stat
      * write_heading
      * write_heading_toplevel
      * write_int_stat
      * write_sequence
    """
    def __init__(self, stream=None):
        """stream expected to be standard stream or open file"""
        self.stream = stream if stream is not None else stdout

    def write_dict(self, heading, d, sortonval=False, reverse=False, width=5):
        """
        Write dict to self.stream with format:

        heading
        =======
        d[k0]  :  k0
        d[k1]  :  k1
        ...
        d[kn]  :  kn

        Where k# represent keys of d.
        List will be sorted by values if sortonval set, and reversed if
        reverse set. Width is format string left-padded width for values.
        """
        def write_pair(key, val):
            self.stream.write('{0:>{1}}'.format(val, width))
            self.stream.write('  :  {0}\n'.format(key))

        self.write_heading(heading)
            
        if sortonval:
            for key in sorted(d, key=lambda x: d[x], reverse=reverse):
                write_pair(key, d[key])
        else:
            for key in d:
                write_pair(key, d[key])
        
    def write_float_stat(self, description, n, width=5, decprec=3,
                         skipline=0, ntrail=''):
        """
        Write line to self.stream with format:
        (assuming description='float', n=1.234, width=5, ntrail='%',
        decprec=1, skipline=0)

         1.2% - float

        If skipline set, a single newline will be written before the line.
        """
        if skipline:
            self.stream.write('\n')
            
        self.stream.write('{0:>{1}.{2}f}{3} - {4}\n'.format(
            n, width - len(ntrail), decprec, ntrail, description)
        )

    def write_heading(self, heading, skipline=True):
        """
        Write to self.stream with format:

        heading
        =======

        If skipline is set, a newline is written before the heading.
        """
        if skipline:
            self.stream.write('\n')
            
        self.stream.write('{0}\n{1}\n'.format(heading, '='*len(heading)))

    def write_heading_toplevel(self, heading, skipline=False):
        """
        Write to self.stream with format:

        =======
        heading
        =======

        If skipline is set, a newline is written before the heading.
        A blank line is always written after the heading.
        """
        self.stream.write('{0}\n'.format('='*len(heading)))
        self.write_heading(heading, skipline=False)
        self.stream.write('\n')
        
    def write_int_stat(self, description, n, width=5, skipline=0):
        """
        Write line to self.stream with format:
            n - description

        Width passed to format string as left-padded width for n.
        If skipline set, a single newline will be written before the line.
        """
        if skipline:
            self.stream.write('\n')
            
        self.stream.write('{0:>{1}} - {2}\n'.format(n, width, description))

    def write_sequence(self, heading, seq):
        """
        Write to self.stream with format:

        heading
        =======
        seq[0]
        seq[1]
        ...
        seq[-1]
        """
        self.write_heading(heading)
        
        for x in seq:
            self.stream.write('  {0}\n'.format(x))

###############################################################################
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

###############################################################################
if __name__ == '__main__':
    timer = Timer()
    outpath = normpath(join(
        OUTPUT_PATH, 'report {0}.txt'.format(timestamp_now())
    ))
    with timer:
        pa = ProdropAnalyzer(INPUT_PATH)
        pa.prodrop_verb_association_analysis()
        pa.print_report_basic()

        with open(outpath, 'w', encoding='utf8') as outfile:
            pa.write_report_full(outfile)
                      
    print('\nTime: {0:.3f}s'.format(timer.total_time))

