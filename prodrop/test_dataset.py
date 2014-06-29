"""
test_dataset.py
Author: Adam Beagle

PURPOSE:
    To computationally confirm assumptions being made about any treebank
    data being used. Anything that can be decisively ruled out as a
    potential pitfall in this file will save error-checking time elsewhere.

    The tests should be re-run and verified to pass whenever new treebank
    data is added to the project.
"""
import re
import unittest

from constants import TREEBANK_DATA_PATH
from util import get_files_by_ext, itertrees_dir

INPUT_DIR = TREEBANK_DATA_PATH

class TestTreebankDataset(unittest.TestCase):
    """ """
    parse_files = get_files_by_ext(INPUT_DIR, '.parse', prepend_dir=True)
    endnode_pattern = '\([^()]+\)'

    def test_endnode_single_space(self):
        match_found = False
        
        for path in self.parse_files:
            with open(path, encoding='utf8') as f:
                for line in f:
                    match = re.search(self.endnode_pattern, line)
                    if match:
                        match_found = True
                        self.assertEqual(match.group().count(' '), 1)

        # Helps ensure test was actually run as expected
        self.assertTrue(match_found)
                    
    def test_endnode_pattern(self):
        """Test self.endnode_pattern"""
        def single_test(string, group):
            match = re.search(self.endnode_pattern, string)
            self.assertIsNotNone(match)
            self.assertEqual(match.group(), group)

        single_test('(NP-SBJ (-NONE- *))', '(-NONE- *)')
        single_test('(NP-OBJ (NP (NOUN kitten)', '(NOUN kitten)')
        single_test('(NP-OBJ (NP (NOUN كرازه)', '(NOUN كرازه)')
        single_test('\t\t\t    (DET+ADJ+CASE_DEF_ACC المَزْهُوَّ))',
            '(DET+ADJ+CASE_DEF_ACC المَزْهُوَّ)'
        )
        single_test('        (PUNC .)))', '(PUNC .)')
        single_test('(TOP (S (CONJ وَ-)', '(CONJ وَ-)')

    def test_parse_files(self):
        """Verify at least one .parse file was discovered."""
        self.assertTrue(self.parse_files)

    def test_top_token_uniqueness(self):
        """
        For each file, test that the TOP token is used ONLY:
        1. At the immediate start of a line (following a left paren)
        2. At the immediate start of a tree (i.e. after a blank line)
        """
        prev_blank = True # True so first line of file treated as new tree

        for path in self.parse_files:
            with open(path, encoding='utf8') as f: 
                for i, line in enumerate(f):
                    if prev_blank:
                        self.assertTrue(line.startswith('(TOP '))
                        self.assertEqual(line.count('TOP'), 1)
                        prev_blank = False

                    elif line == '\n':
                        prev_blank = True

                    else:
                        self.assertNotIn('(TOP', line)
                        prev_blank = False

class ParseTreeTestCase(unittest.TestCase):
    """Cases involving building ParseTree objects from dataset"""
    
    def test_tag_startswith_base_verb(self):
        """
        Verify that primary base verb tags appear at the start of a tag, if
        they appear at all.
        """
        verbs = ('PV', 'IV', 'VERB', 'PSEUDO_VERB')
        
        for tree in itertrees_dir(TREEBANK_DATA_PATH):
            for node in tree.iternodes():
                verb_in_tag = any((verb in node.tag for verb in verbs))
                
                if verb_in_tag:
                    self.assertTrue(
                        any((node.tag.startswith(verb) for verb in verbs))
                    )

###############################################################################
if __name__ == '__main__':
    unittest.main()
