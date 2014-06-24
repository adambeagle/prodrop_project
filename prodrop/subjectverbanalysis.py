"""
subjectverbanalysis.py
Author: Adam Beagle

=======
PURPOSE
=======
    Handles the primary objective of the project, i.e. gathering and analyzing
    subjects and their associated verbs.

=====
USAGE
=====
    The classes useful to an end-user are as follows:

    ProdropAnalyzer
    ---------------
      Gathers statistics on pro-drop subjects and their associated verbs for an
      entire corpus.

    NonProdropAnalyzer
    ------------------
      Gathers statistics on non-pro-drop subjects and their associated verbs
      for an entire corpus.

    CombinedAnalyzer
    ----------------
      Facilitates running analysis of instances of both of the above classes in
      an efficient manner.

    Each of the above classes has, at minimum, the following methods:
      do_analysis
      print_report_basic
      print_report_full
      write_report_basic
      write_report_full

    The CombinedAnalyzer class also has a write_csv method to write a table
    of pro-drop association and non-pro-drop association counts for each verb.

    See each class' individual documentation, as well as that of the
    SubjectVerbAnalyzer base class, for more details.

=============
USAGE EXAMPLE
=============
    A typical use-case (running the pro-drop analyzer, printing the basic
    report, and writing the full report) is accomplished as follows:

    # Create instance of analyzer, providing path to directory
    # containing .parse files from which to examine parse trees.
    pdanalyzer = ProdropAnalyzer('path/to/parsefiles/')

    # Accumulate data by analyzing each tree in each file
    # in the path provided. This step may take some time;
    # 12,000 trees in 600 files takes ~18 seconds on my machine.
    pdanalyzer.do_analysis()

    # Print basic information to console
    pdanalyzer.print_report_basic()

    # Open a file in write mode and pass it to the write_report_full
    # method to write complete report to a file.
    with open('report.txt', 'w', encoding='utf8') as outfile:
        pdanalyzer.write_report_full(outfile)
"""
from abc import ABCMeta, abstractmethod
import csv
from os.path import isfile, isdir
from sys import stdout

from exceptions import InputPathError
from util import itertrees, itertrees_dir, update_distinct_counts

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

###############################################################################
class BaseAnalyzer(metaclass=ABCMeta):
    """
    Abstract base class to the *Analyzer classes.

    Makes the itertrees method an alias to the proper function from util,
    which differs based on whether input_path is a directory or a file.

    METHODS:
      * do_analysis (abstract)
      * itertrees
      * print_report_basic (abstract)
      * print_report_full (abstract)
      * write_report_basic (abstract)
      * write_report_full (abstract)
    """
    def __init__(self, input_path):
        """
        input_path can be directory or file.

        InputPathError is raised if input_path is not a valid path to
        an existing directory or file.
        """
        if isfile(input_path):
            self._itertreesfunc = itertrees
        elif isdir(input_path):
            self._itertreesfunc = itertrees_dir
        else:
            raise InputPathError(
                "input_path is not a valid path to a directory or " +
                "existing file.\ninput_path: {0}".format(input_path)
            )

        self._input_path = input_path

    @abstractmethod
    def do_analysis(self):
        raise NotImplementedError(self.notimplementedmsg)
    
    def itertrees(self):
        return self._itertreesfunc(self._input_path)

    @abstractmethod
    def print_report_basic(self, *args, **kwargs):
        raise NotImplementedError(
            "Inheriting classes must override and implement this method."
        )

    @abstractmethod
    def print_report_full(self, *args, **kwargs):
        raise NotImplementedError(
            "Inheriting classes must override and implement this method."
        )

    @abstractmethod
    def write_report_basic(self, *args, **kwargs):
        raise NotImplementedError(
            "Inheriting classes must override and implement this method."
        )

    @abstractmethod
    def write_report_basic(self, *args, **kwargs):
        raise NotImplementedError(
            "Inheriting classes must override and implement this method."
        )

###############################################################################
class SubjectVerbAnalyzer(BaseAnalyzer):
    """
    ATTRIBUTES:
    ===========
    * allowed_verb_tags
    * input_path
    * subject_descriptor

    Populated by do_analysis:
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
      * analyze_tree
      * do_analysis
      * itersubjects
      * print_report_basic
      * print_report_full
      * write_report_basic
      * write_report_full
    """
    def __init__(self, input_path, subject_descriptor):
        """input_path may be to directory or existing .parse file."""
        super().__init__(input_path)
        
        self.subject_descriptor = subject_descriptor
        self.allowed_verb_tags = (
            'IV', 'PV', 'VERB', 'PSEUDO_VERB',
        )

        # Instantiate all counters/dictionaries populated by do_analysis
        self._reset()

    def analyze_tree(self, tree):
        """
        Analyze a single tree and return list of associated verbs found.
        For each subject match as returned by itersubjects, update counters
        and dictionaries accordingly.
        A verb may appear multiple times in the returned list.
        """
        self.tree_count += 1
        has_subject = False
        valid_verbs = []
        
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
                valid_verbs.append(result.word)

            # Failure.
            # Store sibling tags for reporting if no associated verb
            # found matching allowed tags.
            else:
                sibtags += result
                for t in sibtags:
                    update_distinct_counts(self.ignored_tag_counts, t)
                self.failure_trees.add(tree)

        self.tree_w_subject_count += 1 if has_subject else 0

        return valid_verbs

    def do_analysis(self):
        """
        For each tree in input_path (which may involve searching multiple
        files if input_path is a directory), search for subject matches
        using itersubjects and update counters and dictionaries accordingly.
        """
        self._reset()
        
        print('Starting {0} search... '.format(
            self.subject_descriptor), end=''
        )
        for tree in self.itertrees():
            self.analyze_tree(tree)
                
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

    def write_report_full(self, out, rw=None):
        """ """
        sd = self.subject_descriptor
        if not rw:
            rw = ReportWriter(out)
        
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
class CombinedAnalyzer(BaseAnalyzer):
    """
    Used to run a combined pro-drop and non-pro-drop analysis.

    ATTRIBUTES:
      * input_path
      * verb_counts

    METHODS:
      * do_analysis
      * write_csv
    """
    class VerbData:
        """Utility object used for the values in verb_counts."""
        def __init__(self):
            self.prodrop_count = 0
            self.nonprodrop_count = 0
            
    def __init__(self, input_path):
        """input_path can be file or directory."""
        super().__init__(input_path)
        
        self.prodrop_analyzer = ProdropAnalyzer(input_path)
        self.nonprodrop_analyzer = NonProdropAnalyzer(input_path)

    def do_analysis(self):
        """
        Perform the equivalent of running do_analysis on both a
        ProdropAnalyzer and NonProdropAnalyzer object, while being more
        efficient by only iterating through the .parse files once.
        """
        self.verb_counts = {}
        pa = self.prodrop_analyzer
        npa = self.nonprodrop_analyzer

        print('Starting combined analysis... ', end='')
        for tree in self.itertrees():
            pdverbs = pa.analyze_tree(tree)
            npdverbs = npa.analyze_tree(tree)
            self._update_verb_counts(pdverbs, npdverbs)
            
        print('Conplete.')

    def print_report_basic(self):
        self.write_report_basic(stdout)

    def print_report_full(self):
        self.write_report_full(stdout)

    def write_report_basic(self, out):
        rw = ReportWriter(out)
        
        rw.write_heading_toplevel('ProdropAnalyzer Results', skipline=1)
        self.prodrop_analyzer.write_report_basic(out, rw)
        
        rw.write_heading_toplevel('NonProdropAnalyzer Results', skipline=1)
        self.nonprodrop_analyzer.write_report_basic(out, rw)

    def write_report_full(self, out):
        rw = ReportWriter(out)
        
        self.prodrop_analyzer.write_report_full(out, rw)
        self.nonprodrop_analyzer.write_report_full(out, rw)

    def write_csv(self, out):
        """
        To the file object 'out,' write a .csv file containing records
        with fields in the following order:
           verb, # pro-drop associations, # non-pro-drop associations

        The records are written in no defined order.

        'out' is expected to be an open file object or stream. Remember
        to set the proper encoding on the file if dealing with unicode.
        """
        writer = csv.writer(out, lineterminator='\n')
        writer.writerow(['VERB', 'PRO-DROP COUNT', 'NON-PRO-DROP COUNT'])

        for verb, counts in self.verb_counts.items():
            writer.writerow([verb, counts.prodrop_count, counts.nonprodrop_count])

    def _update_verb_counts(self, pdverbs, npdverbs):
        for verb in pdverbs:
            if verb in self.verb_counts:
                self.verb_counts[verb].prodrop_count += 1
            else:
                data = self.VerbData()
                data.prodrop_count = 1
                self.verb_counts[verb] = data

        for verb in npdverbs:
            if verb in self.verb_counts:
                self.verb_counts[verb].nonprodrop_count += 1
            else:
                data = self.VerbData()
                data.nonprodrop_count = 1
                self.verb_counts[verb] = data

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
        if skipline:
            self.stream.write('\n')
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
