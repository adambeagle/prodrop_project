"""
test_dataset.py
Author: Adam Beagle

PURPOSE:
    To computationally confirm assumptions being made about any treebank
    data being used. Anything that can be deciseively ruled out as a
    potential pitfall in this file will save error-checking time elsewhere.

    The tests should be re-run and verified to pass whenever new treebank
    data is added to the project.
"""
import unittest
from util import get_files_by_ext

INPUT_DIR = '../treebank_data/00' # TODO allow multi-directory walk from root

class TestTreeStart(unittest.TestCase):
    """ """
    parse_files = get_files_by_ext(INPUT_DIR, '.parse', prepend_dir=True)

    def test_top_token_uniqueness(self):
        """
        For each file, test that the TOP token is used ONLY:
          1. At the immediate start of a line (following a left paren)
          2. At the immediate start of a tree (i.e. after a blank line)
        """
        prev_blank = False

        for path in self.parse_files:
            with open(path, encoding='utf8') as f: 
                for i, line in enumerate(f):
                    if 'TOP' in line:
                        self.assertEqual(line.count('TOP'), 1)
                        self.assertEqual(line[:4], '(TOP')
                        self.assertTrue(prev_blank or i == 0)
                        prev_blank = False
                    elif line == '\n':
                        prev_blank = True
                    else:
                        prev_blank = False

###############################################################################
if __name__ == '__main__':
    unittest.main()
