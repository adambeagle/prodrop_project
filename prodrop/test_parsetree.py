﻿"""
test_parsetree.py
Author: Adam Beagle
"""
import re
import unittest

from exceptions import SearchFlagError
from parsetree import (endnode_pattern, ParseTree, ParseTreeEndNode,
    ParseTreeThruNode, thrunode_pattern
)

class ThruNodePatternTestCase(unittest.TestCase):
    def _test_failure(self, line):
        m = re.match(thrunode_pattern, line)
        
        self.assertIsNone(m)
        
    def _test_success(self, line, group, tag):
        m = re.match(thrunode_pattern, line)
        
        self.assertIsNotNone(m)
        self.assertEqual(m.group(), group)
        self.assertEqual(m.group('tag'), tag)
    
    def test_simple_english(self):
        full_line = '(TOP (S (NP (NNP John))\n'
        
        self._test_success(full_line, '(TOP (', 'TOP')
        self._test_success(full_line[5:], '(S (', 'S')
        self._test_success(full_line[8:], '(NP (', 'NP')
        self._test_failure('(NNP John))\n')
        
        self._test_failure(full_line[1:])
        
    def test_simple_arabic(self):
        full_line = '(VP (PRT (NEG_PART لا))\n'
        
        self._test_success(full_line, '(VP (', 'VP')
        self._test_success(full_line[4:], '(PRT (', 'PRT')
        self._test_failure('(NEG_PART لا))\n')
        
    def test_elaborate_arabic(self):
        full_line = ('(NP-SBJ (S-NOM-1 ' +
            '(DET+NOUN+NSUFF_FEM_PL+CASE_DEF_NOM المَعْلُوماتُ))\n'
        )
        
        self._test_success(full_line, '(NP-SBJ (', 'NP-SBJ')
        self._test_success(full_line[8:], '(S-NOM-1 (', 'S-NOM-1')
        self._test_failure('(DET+NOUN+NSUFF_FEM_PL+CASE_DEF_NOM المَعْلُوماتُ))\n')
        
        
class EndPatternTestCase(unittest.TestCase):
    def _test_failure(self, line):
        m = re.match(endnode_pattern, line)
        
        self.assertIsNone(m)
        
    def _test_success(self, line, group, tag, word):
        m = re.match(endnode_pattern, line)
        
        self.assertIsNotNone(m)
        self.assertEqual(m.group(), group)
        self.assertEqual(m.group('tag'), tag)
        self.assertEqual(m.group('word'), word)
    
    def test_simple_english(self):
        full_line = '(TOP (S (NP (NNP John))\n'
        
        for i in range(12):
            self._test_failure(full_line[i:])
            
        self._test_success(full_line[12:], '(NNP John)', 'NNP', 'John')
        
        self._test_success('(PUNC .)\n', '(PUNC .)', 'PUNC', '.')
        
    def test_simple_arabic(self):
        full_line = '(VP (PRT (NEG_PART لا))\n'
        
        for i in range(9):
            self._test_failure(full_line[i:])
        
        self._test_success(full_line[9:], '(NEG_PART لا)', 'NEG_PART', 'لا')
        
    def test_elaborate_arabic(self):
        full_line = ('(NP-SBJ (S-NOM-1 ' +
            '(DET+NOUN+NSUFF_FEM_PL+CASE_DEF_NOM المَعْلُوماتُ))\n'
        )
        
        for i in range(17):
            self._test_failure(full_line[i:])
        
        self._test_success(
            full_line[17:], 
            '(DET+NOUN+NSUFF_FEM_PL+CASE_DEF_NOM المَعْلُوماتُ)',
            'DET+NOUN+NSUFF_FEM_PL+CASE_DEF_NOM',
            'المَعْلُوماتُ'
        )
        
class SimpleArabicTreeTestCase(unittest.TestCase):
    """ """
    def setUp(self):
        self.rawdata = """(TOP (SQ (CONJ وَ-)
         (VP (IV3FS+IV+IVSUFF_MOOD:I -تُسَيْطِرُ)
             (NP-SBJ (-NONE- *))
             (PP-CLR (PREP عَلَي-)
                     (NP (PRON_3FS -ها))))
         (PUNC ?)))"""
         
        self.tree = ParseTree(self.rawdata.split('\n'))

    def test_iternodes(self):
        correct_tag_order = ('TOP', 'SQ', 'CONJ', 'VP', 
            'IV3FS+IV+IVSUFF_MOOD:I', 'NP-SBJ', '-NONE-', 'PP-CLR', 'PREP',
            'NP', 'PRON_3FS', 'PUNC'
        )
        visited = 0
        
        for i, node in enumerate(self.tree.iternodes()):
            visited += 1
            self.assertEqual(node.tag, correct_tag_order[i])
        
        # The above loop may not raise an exception if some nodes were never yielded.
        # This ensures each was actually visited.
        self.assertEqual(visited, len(correct_tag_order))
        
    def test_treebank_notation(self):
        self.assertEqual(self.rawdata, self.tree.treebank_notation)
        
        # Test that treebank_notation is identical whether or not given lines
        # end in a newline.
        lines = self.rawdata.split('\n')
        for line in lines:
            line += '\n'
            
        newtree = ParseTree(lines)
        self.assertEqual(self.rawdata, newtree.treebank_notation)
        
class SimpleEnglishTreeTestCase(unittest.TestCase):
    """ """
    def setUp(self):
        self.rawdata = """(TOP (S (NP (NNP John))
   (VP (VPZ loves)
       (NP (NNP Mary)))
   (PUNC .))"""

        self.tree = ParseTree(self.rawdata.split('\n'))
    
    def test_depth_first_traversal(self):
        node = self.tree.top
        self.assertEqual(node.tag, 'TOP')
        
        node = node.children[0]
        self.assertEqual(node.tag, 'S')
        self.assertEqual(node.parent.tag, 'TOP')
        
        node = node.children[0]
        self.assertEqual(node.tag, 'NP')
        self.assertEqual(node.parent.tag, 'S')
        
        node = node.children[0]
        self.assertEqual(node.tag, 'NNP')
        self.assertEqual(node.word, 'John')
        self.assertEqual(node.parent.tag, 'NP')
        
        node = node.parent.parent
        self.assertEqual(node.tag, 'S')
        
        node = node.children[1]
        self.assertEqual(node.tag, 'VP')
        self.assertEqual(node.parent.tag, 'S')
        
        node = node.children[0]
        self.assertEqual(node.tag, 'VPZ')
        self.assertEqual(node.word, 'loves')
        self.assertEqual(node.parent.tag, 'VP')
        
        node = node.parent.children[1]
        self.assertEqual(node.tag, 'NP')
        self.assertEqual(node.parent.tag, 'VP')
        
        node = node.children[0]
        self.assertEqual(node.tag, 'NNP')
        self.assertEqual(node.word, 'Mary')
        self.assertEqual(node.parent.tag, 'NP')
        
        node = node.parent.parent.parent
        self.assertEqual(node.tag, 'S')
        
        node = node.children[2]
        self.assertEqual(node.tag, 'PUNC')
        self.assertEqual(node.word, '.')

    def test_get_siblings(self):
        tree = self.tree
        
        def test_no_siblings(node):
            sibs = tuple(tree.get_siblings(node))
            self.assertEqual(sibs, ())
            for sib in tree.get_siblings(node):
                raise AssertionError("{0} should have no siblings.".format(
                    node.tag
                ))

        test_no_siblings(tree.top)
        test_no_siblings(tree.search(tag='S')[0])
        for node in tree.search(tag='NNP'):
            test_no_siblings(node)

        sibs = tuple(tree.get_siblings(tree.search(tag='NP',
                                                   parent_tag='S')[0])
        )
        self.assertEqual(len(sibs), 2)
        self.assertEqual(sibs[0].tag, 'VP')
        self.assertEqual(sibs[1].tag, 'PUNC')

        sibs = tuple(tree.get_siblings(tree.search(tag='VP')[0]))
        self.assertEqual(len(sibs), 2)
        self.assertEqual(sibs[0].tag, 'NP')
        self.assertEqual(sibs[1].tag, 'PUNC')

        sibs = tuple(tree.get_siblings(tree.search(tag='PUNC')[0]))
        self.assertEqual(len(sibs), 2)
        self.assertEqual(sibs[0].tag, 'NP')
        self.assertEqual(sibs[1].tag, 'VP')

        sibs = tuple(tree.get_siblings(tree.search(tag='VPZ')[0]))
        self.assertEqual(len(sibs), 1)
        self.assertEqual(sibs[0].tag, 'NP')
        self.assertEqual(sibs[0].children[0].word, 'Mary')
        
        
        
    def test_iterendnodes(self):
        correct_tag_order = ('NNP', 'VPZ', 'NNP', 'PUNC')
        correct_word_order = ('John', 'loves', 'Mary', '.')
        visited = 0
        
        for i, node in enumerate(self.tree.iterendnodes()):
            visited  += 1
            self.assertEqual(node.tag, correct_tag_order[i])
            self.assertEqual(node.word, correct_word_order[i])
            
        self.assertEqual(visited, len(correct_tag_order))
            
    def test_iternodes(self):
        correct_tag_order = ('TOP', 'S', 'NP', 'NNP', 'VP', 'VPZ', 'NP', 'NNP', 'PUNC')
        visited = 0
        
        for i, node in enumerate(self.tree.iternodes()):
            visited += 1
            self.assertEqual(node.tag, correct_tag_order[i])
        
        # The above loop may not raise an exception if some nodes were never yielded.
        # This ensures each was actually visited.
        self.assertEqual(visited, len(correct_tag_order))
        
    def test_iterwords(self):
        correct_words = ('John', 'loves', 'Mary', '.')
        
        for word, correct_word in zip(self.tree.iterwords(), correct_words):
            self.assertEqual(word, correct_word)

    # TODO test REMATCH flag
    def test_search(self):
        t = self.tree

        # SUCCESSES
        matches = t.search(tag='TOP')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'TOP')

        matches = t.search(tag='NNP', tag_flag=t.EXACT)
        self.assertEqual(len(matches), 2)
        for m in matches:
            self.assertEqual(m.tag, 'NNP')
        self.assertNotEqual(matches[0].word, matches[1].word)

        matches = t.search(word='J', word_flag=t.STARTSWITH)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].word, 'John')

        matches = t.search(tag='NP', word='ar',
            tag_flag=t.CONTAINS, word_flag=t.CONTAINS
        )
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].word, 'Mary')

        matches = t.search(tag='S', tag_flag=t.CONTAINS)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'S')

        matches = t.search(tag='VP', tag_flag=t.CONTAINS)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].tag, 'VP')
        self.assertEqual(matches[1].tag, 'VPZ')

        matches = t.search(tag='VP', tag_flag=t.STARTSWITH)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].tag, 'VP')
        self.assertEqual(matches[1].tag, 'VPZ')

        matches = t.search(tag='VP', tag_flag=t.EXACT)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'VP')

        matches = t.search(word='.')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'PUNC')
        self.assertEqual(matches[0].word, '.')

        matches = t.search(tag='NNP', word='John', word_flag=t.IS_NOT)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'NNP')
        self.assertEqual(matches[0].word, 'Mary')

        matches = t.search(word='', word_flag=t.IS_NOT)
        self.assertEqual(len(matches), 4)
        for node in matches:
            self.assertTrue(hasattr(node, 'word'))
        

        # FAILURES
        matches = t.search(tag='NP', word='John')
        self.assertFalse(matches)

        with self.assertRaises(SearchFlagError) as cm:
            matches = t.search(tag='S', tag_flag='INCLUDES')

        with self.assertRaises(SearchFlagError) as cm:
            matches = t.search(tag='S', tag_flag=-5)

        with self.assertRaises(SearchFlagError) as cm:
            matches = t.search(tag='S', tag_flag=15)

    def test_search_custom(self):
        t = self.tree

        def customfunc(phrase, s):
            try:
                return phrase == s[1]
            except IndexError:
                return False

        is_np = lambda phrase, s: s == 'NP'
        matches = t.search(tag_flag=t.CUSTOM, tag_func=is_np)
        self.assertEqual(len(matches), 2)
        for match in matches:
            self.assertEqual(match.tag, 'NP')

        matches = t.search(word_flag=t.CUSTOM, word_func=is_np)
        self.assertEqual(len(matches), 0)

        matches = t.search(word= 'o', word_flag=t.CUSTOM, word_func=customfunc)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].word, 'John')
        self.assertEqual(matches[1].word, 'loves')

        matches = t.search(tag='N', tag_flag=t.CUSTOM, tag_func=customfunc,
            parent_tag='P', parent_flag=t.CUSTOM, parent_func=customfunc
        )
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].tag, 'NNP')
        self.assertEqual(matches[0].word, 'John')
        self.assertEqual(matches[1].tag, 'NNP')
        self.assertEqual(matches[1].word, 'Mary')

        matches=t.search(tag_flag=t.CUSTOM, tag_func=is_np, parent_tag='P',
            parent_flag=t.CUSTOM, parent_func=customfunc
        )
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'NP')
        self.assertEqual(matches[0].parent.tag, 'VP')

    def test_search_parent(self):
        """Test searching with parent_tag and parent_flag"""
        t = self.tree

        matches = t.search(tag='TOP', parent_tag='.+', parent_flag=t.REMATCH)
        self.assertEqual(len(matches), 0)

        matches = t.search(tag='S', parent_tag='TOP')
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'S')
        self.assertEqual(matches[0].parent.tag, 'TOP')

        matches = t.search(parent_tag='S', parent_flag=t.STARTSWITH)
        for node in matches:
            self.assertEqual(node.parent.tag, 'S')
        self.assertEqual(len(matches), 3)
        self.assertEqual(matches[0].tag, 'NP')
        self.assertEqual(matches[1].tag, 'VP')
        self.assertEqual(matches[2].tag, 'PUNC')
        
        matches = t.search(parent_tag='VP', word='o', word_flag=t.CONTAINS)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].tag, 'VPZ')
        self.assertEqual(matches[0].word, 'loves')

        matches = t.search(parent_tag='P', parent_flag=t.CONTAINS)
        for node in matches:
            self.assertTrue('P' in node.parent.tag)
        self.assertEqual(len(matches), 5)
        self.assertEqual(matches[0].tag, 'S')
        self.assertEqual(matches[1].tag, 'NNP')
        self.assertEqual(matches[1].word, 'John')
        self.assertEqual(matches[2].tag, 'VPZ')
        self.assertEqual(matches[2].word, 'loves')
        self.assertEqual(matches[3].tag, 'NP')
        self.assertEqual(matches[3].parent.tag, 'VP')
        self.assertEqual(matches[4].tag, 'NNP')
        self.assertEqual(matches[4].word, 'Mary')
        
    def test_sentence(self):
        self.assertEqual(self.tree.sentence, 'John loves Mary.')
        
    def test_treebank_notation(self):
        self.assertEqual(self.rawdata, self.tree.treebank_notation)
        
        # Test that treebank_notation is identical whether or not given lines
        # end in a newline.
        lines = self.rawdata.split('\n')
        for line in lines:
            line += '\n'
            
        newtree = ParseTree(lines)
        self.assertEqual(self.rawdata, newtree.treebank_notation)

class ComplexArabicTreeTestCase(unittest.TestCase):
    """
    The file in this case begins with the BOM \ufeff character that is
    automatically placed at the head of a file by some text editors.
    """
    def setUp(self):
        path = '../treebank_data/testdata/sample_tree_large.parse'
        with open(path, encoding='utf8') as f:
            self.rawdata = f.read()

        self.tree = ParseTree(self.rawdata.split('\n'))

    def test_treebank_notation(self):
        self.assertEqual(self.rawdata, self.tree.treebank_notation)
    
##############################################################################
if __name__ == '__main__':
    unittest.main()
