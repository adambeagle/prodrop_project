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

def write_combined_csv(outfile, prodrop_analysis, nonprodrop_analysis):
    column_widths = (20, 20, 15)
    pdcounts = prodrop_analysis.verb_counts
    npa = nonprodrop_analysis
    npdcounts = {}

    for verb, count in npa.verb_counts.items():
        npdcounts[verb] = [count, False]
        
    outfile.write('VERB,PRO-DROP-COUNT,NON-PRO-DROP-COUNT\n')
    for verb in prodrop_analysis.verb_counts:
        outfile.write('{0},{1},'.format(
            verb,
            pa.verb_counts[verb],
        ))

        npdcount = 0
        if verb in npdcounts:
            npdcounts[verb][1] = True
            npdcount = npdcounts[verb][0]
            
        outfile.write('{0}\n'.format(npdcount))

    for verb, count in ((k, v[0]) for k, v in npdcounts.items() if not v[1]):
        outfile.write('{0},{1},{2}\n'.format(
            verb, 0, count
        ))


###############################################################################
class SubjectVerbAnalyzer():
    """
    ATTRIBUTES:
    ===========
    * allowed_verb_tags
    * input_path
    * subject_descriptor

    Populated by do_verb_analysis:
    ------------------------------
      * failure_trees
      * ignored_tag_counts
      * subject_count
      * subject_w_verb_count
      * tree_count
      * tree_w_subject_count
      * verb_counts

    METHODS:
    ========
      * do_verb_analysis
      * itersubjects
      * print_report_basic
      * print_report_full
      * write_report_basic
      * write_report_full
    """
    def __init__(self, input_path, subject_descriptor):
        """input_path may be to directory or existing .parse file."""

        if isfile(input_path):
            self.itertrees = itertrees
        elif isdir(input_path):
            self.itertrees = itertrees_dir
        else:
            raise ImportPathError(
                "input_path is not a valid path to a directory or " +
                "existing file.\ninput_path: {0}".format(input_path)
            )

        self.subject_descriptor = subject_descriptor
        self.input_path = input_path
        self.allowed_verb_tags = (
            'IV', 'PV', 'VERB', 'PSEUDO_VERB',
        )

        # Instantiate all counters/dictionaries populated by do_verb_analysis
        self._reset()

    def do_verb_analysis(self):
        self._reset()
        
        print('Starting {0} search... '.format(
            self.subject_descriptor), end=''
        )
        for tree in self.itertrees(self.input_path):
            self.tree_count += 1
            has_subject = False
            
            for node in self.itersubjects(tree):
                has_subject = True
                self.subject_count += 1
                sibtags = []

                result = self._check_siblings_for_verb(
                    node, self.allowed_verb_tags
                )

                # Success. Verb found
                if hasattr(result, 'tag'):
                    self.subject_w_verb_count += 1
                    update_distinct_counts(self.verb_counts, result.word)

                # Failure.
                # Store sibling tags for reporting if no associated verb
                # found matching allowed tags.
                else:
                    sibtags += result
                    for t in sibtags:
                        update_distinct_counts(self.ignored_tag_counts, t)
                    self.failure_trees.add(tree)

            self.tree_w_subject_count += 1 if has_subject else 0
                
        print('Complete.\n')

    def itersubjects(self):
        raise NotImplementedError(
            "Inheriting classes must override and implement this method."
        )

    def print_report_basic(self):
        self.write_report_basic(stdout)

    def print_report_full(self):
        self.write_report_full(stdout)

    def write_report_basic(self, out, rw=None):
        """ """
        sd = self.subject_descriptor
        
        if not rw:
            rw = ReportWriter(out)

        rw.write_int_stat('Trees searched', self.tree_count)
        rw.write_int_stat('Trees with at least 1 {0}'.format(sd),
                          self.tree_w_subject_count)
        rw.write_int_stat('Trees with failed sibling lookup',
                          len(self.failure_trees))
        
        rw.write_int_stat('Total {0}s found'.format(sd), self.subject_count,
                          skipline=True)
        rw.write_int_stat(
            '{0}s with associated verb found'.format(sd.capitalize()),
            self.subject_w_verb_count
        )

        if self.subject_count > 0:
            perc = 100*self.subject_w_verb_count / self.subject_count
        else:
            perc = 0
            
        rw.write_float_stat('Percent {0}s with associated verb'.format(sd),
                            perc, decprec=1, ntrail='%')
        rw.write_int_stat('Distinct associated verbs found',
                          len(self.verb_counts), skipline=True)
        rw.write_int_stat('Distinct excluded sibling tags',
                          len(self.ignored_tag_counts))

    def write_report_full(self, out):
        """ """
        rw = ReportWriter(out)
        sd = self.subject_descriptor
        
        rw.write_heading_toplevel(
            '{0} VERB ASSOCIATION ANALYSIS REPORT'.format(sd.upper())
        )
        
        self.write_report_basic(out, rw)
        
        rw.write_sequence('Allowed verb tag bases', self.allowed_verb_tags)
        rw.write_dict(
            'Sibling tags of {0}s with no associated verb found'.format(sd),
            self.ignored_tag_counts,
            sortonval=True,
            reverse=True
        )

        rw.write_dict('Verb occurrences', self.verb_counts,
            sortonval=True, reverse=True
        )

    def _check_siblings_for_verb(self, node, allowed_verb_tags):
        """
        Check node's siblings for a verb node whose tag starts with a
        value in allowed_verb_tags.

        If valid verb found, return the sibling node which contains the verb.
        If no match found, return a list of tags of visited siblings.
        """
        sibling_tags = []
        
        # Only check siblings above parent, as subject always follows
        # verb as per the guidelines.
        for sib in self._get_previous_siblings(node):
            sibling_tags.append(sib.tag)

            for tag in allowed_verb_tags:
                if sib.tag.startswith(tag):
                    return sib

        return sibling_tags

    def _get_previous_siblings(self, node):
        """
        Yield the prior siblings of a tree as found in a depth-first traversal.
        """
        for child in node.parent.children:
            if child == node:
                return

            yield child

    def _reset(self):
        """
        Reset all class attributes to initial state.
        Called automatically before each analysis, and by constructor.
        """
        self.tree_count = 0
        self.tree_w_subject_count = 0
        self.subject_count = 0
        self.subject_w_verb_count = 0
        self.verb_counts = {}
        self.ignored_tag_counts = {}
        self.failure_trees = set()

###############################################################################
class ProdropAnalyzer(SubjectVerbAnalyzer):
    """ """
    def __init__(self, input_path):
        """input_path may be to directory or existing .parse file."""
        super().__init__(input_path, 'pro-drop')

    def itersubjects(self, tree):
        """
        Yield NP-SBJ parent nodes of pro-drop nodes.
        """
        return (node.parent for node in iterprodrops(tree))

###############################################################################
class NonProdropAnalyzer(SubjectVerbAnalyzer):
    """ """
    def __init__(self, input_path):
        super().__init__(input_path, 'non-pro-drop')

    # TODO Currently excluding ANY node whose child has a -NONE- tag,
    # including traces, etc. Need to verify that this assumption is correct.
    #
    # TODO Assuming a -NONE- tag always a direct child of NP-SBJ and not
    # further nested.
    def itersubjects(self, tree):
        """
        Yield NP-SBJ nodes that do not represent pro-drops, i.e. a node
        whose tag is a variant of NP-SBJ, that does not have a child with a
        -NONE- tag.
        """
        return (node.parent for node in tree.search(
            parent_tag='NP-SBJ',
            parent_flag=tree.STARTSWITH,
            word=PRODROP_WORD_PATTERN,
            word_flag=tree.NOT_REMATCH,
        ))

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

    def write_heading(self, heading, ulchar='=', skipline=True):
        """
        Write to self.stream with format:

        heading
        =======

        If skipline is set, a newline is written before the heading.
        The character used to underline can be changed with named attribute 'ulchar.'
        """
        if skipline:
            self.stream.write('\n')
            
        self.stream.write('{0}\n{1}\n'.format(heading, ulchar*len(heading)))

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
if __name__ == '__main__':
    timer = Timer()
    outpath = normpath(join(
        OUTPUT_PATH, 'verbs {0}.csv'.format(timestamp_now())
    ))
    with timer:
        pa = ProdropAnalyzer(INPUT_PATH)
        npa = NonProdropAnalyzer(INPUT_PATH)
        
        pa.do_verb_analysis()
        npa.do_verb_analysis()

        with open(outpath, 'w', encoding='utf8') as outfile:
            write_combined_csv(outfile, pa, npa)
                      
    print('\nTime: {0:.3f}s'.format(timer.total_time))

