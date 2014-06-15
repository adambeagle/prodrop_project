import re
import unittest

from prodrop_analysis import PRODROP_WORD_PATTERN

class TestPropdropWordPattern(unittest.TestCase):
    def setUp(self):
        self.p = PRODROP_WORD_PATTERN

    def test_successes(self):
        p = self.p

        m = re.match(p, '*')
        self.assertIsNotNone(m)
        self.assertEqual(m.group(), '*')

        m = re.match(p, '*-1')
        self.assertIsNotNone(m)
        self.assertEqual(m.group(), '*-1')

        m = re.match(p, '*-10')
        self.assertIsNotNone(m)
        self.assertEqual(m.group(), '*-10')

        m = re.match(p, '*-123')
        self.assertIsNotNone(m)
        self.assertEqual(m.group(), '*-123')

    def test_failures(self):
        p = self.p

        m = re.match(p, '*T*')
        self.assertIsNone(m)

        m = re.match(p, '*ICH*')
        self.assertIsNone(m)

        m = re.match(p, 'Wivs')
        self.assertIsNone(m)

        m = re.match(p, '123')
        self.assertIsNone(m)

        m = re.match(p, '')
        self.assertIsNone(m)

        m = re.match(p, '*1')
        self.assertIsNone(m)

###############################################################################
if __name__ == '__main__':
    unittest.main()
