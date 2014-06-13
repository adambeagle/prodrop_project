"""
test_dataset.py
Author: Adam Beagle

PURPOSE:
    To computationally confirm assumptions being made about any treebank
    data being used. Anything that can be decisively ruled out as a
    potential pitfall in this file will save error-checking time elsewhere.

    The tests should be re-run and verified to pass whenever new treebank
    data is added to the project.
    
TODO:
    * Verify the assumed (tag word) format. Specifically, test that an end
      node only ever contains a single space, which can be assumed to separate
      the tag and the word.
"""
import unittest

from constants import TREEBANK_DATA_PATH
from util import get_files_by_ext

INPUT_DIR = TREEBANK_DATA_PATH

class TestTreeStart(unittest.TestCase):
    """ """
    parse_files = get_files_by_ext(INPUT_DIR, '.parse', prepend_dir=True)
    
    def test_parse_files(self):
        """Verify .parse files discovered."""
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

###############################################################################
if __name__ == '__main__':
    unittest.main()
