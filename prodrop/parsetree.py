"""
parsetree.py
Author: Adam Beagle

PURPOSE:
    Contains a data structure that holds a parse tree and facilitates
    easy navigation and searching.
"""
import re

from exceptions import SearchFlagError, TreeConstructionError

# Regex patterns for building from .parse files.
# Placed here so they are available to tests.
thrunode_pattern = r'^\((?P<tag>\S+) \('
endnode_pattern = r'^\((?P<tag>\S+) (?P<word>[^\s()]+)\)'

class ParseTreeNode:
    """
    ATTRIBUTES:
      * parent
      * tag
    """
    def __init__(self, parent, tag):
        self.parent = parent
        self.tag = tag
        
        if self.parent is not None:
            self.parent.add_child(self)
            
    @property
    def has_children(self):
        raise NotImplementedError()
        
    @property
    def is_end(self):
        raise NotImplementedError()

class ParseTreeThruNode(ParseTreeNode):
    """
    ATTRIBUTES:
      * children (read-only)

    INHERITED ATTRIBUTES:
      * has_children
      * is_end
      * parent
      * tag
      
    METHODS:
      * add_child
    """
    def __init__(self, parent, tag):
        super().__init__(parent, tag)
        self._children = ()
        
    def add_child(self, child):
        if not isinstance(child, ParseTreeNode):
            raise TypeError()
        self._children += (child, )
        
    @property
    def children(self):
        return self._children[:]
        
    @property
    def has_children(self):
        return bool(self._children)
        
    @property
    def is_end(self):
        return False
    
class ParseTreeEndNode(ParseTreeNode):
    """
    ATTRIBUTES:
      * word

    INHERITED ATTRIBUTES:
      * has_children
      * is_end
      * parent
      * tag
    """
    def __init__(self, parent, tag, word):
        super().__init__(parent, tag)
        self.word = word
        
    @property
    def has_children(self):
        return False
        
    @property
    def is_end(self):
        return True

class ParseTree:
    """
    Defines a syntactic parse tree built from Penn Treebank bracketed notation
    as found in .parse files.
    
    Nodes are either ParseTreeThruNode or ParseTreeEndNode, defined above and
    have 'children' and 'word' attributes, respectively. All nodes have a 
    'parent' attribute.
    
    ATTRIBUTES:
      * sentence
      * top - The top-level tree node. This will always have the tag 'TOP'
      * treebank_notation - The Penn Treebank bracketed notation from which
                            the tree was built.
      
    METHODS:
      * iterendnodes
      * iternodes
      * search

    SEARCH FLAGS
    =========================================================================
    The following flags may be passed to ParseTree.search() to modify how a
    search is performed for a tag or word. See search() for more information.

    EXACT      - Search phrase matches an attribute exactly.
    
    CONTAINS   - Search phrase, exactly as written, appears anywhere in the
                 attribute at least once.
    
    STARTSWITH - Search phrase, exactly as written, appears at the start of
                 the attribute.
    
    REMATCH    - Search phrase is assumed to be a regular expression
                 pattern which is passed to re.match(). If re.match returns
                 any Match object, the attribute is considered a match for
                 the purpose of the search.
    """
    EXACT = 0
    CONTAINS = 1
    STARTSWITH = 2
    REMATCH = 3
    
    def __init__(self, lines, cache_end_nodes=True):
        """
        Expects list of strings 'lines' that represent a tree as given in a
        .parse file.

        Caching of end nodes is on by default. The speed of searches involving
        'word' attributes is GREATLY increased with caching turned on. The only
        reason to turn off caching is if you are doing a single search per
        tree, or none of your searches involve the 'word' attribute (and even
        then the time difference to leave caching on will be miniscule unless
        a corpus contains >10000 trees, in which case it may add a few seconds
        of execution time).
        """
        self.top = None
        self._end_nodes = []
        
        join_char = '' if lines[0][-1] == '\n' else '\n'
        self.treebank_notation = join_char.join(lines)

        self._build_from_lines(lines)

        if cache_end_nodes:
            self._end_nodes = tuple(self.iterendnodes())

    def get_siblings(self, node):
        """
        Yield each sibling of a node, i.e. other nodes that have the same
        parent.
        """
        parent = node.parent

        if parent is None:
            return

        if len(parent.children) > 1:
            for child in parent.children:
                if not child == node:
                    yield child
        
    def iterendnodes(self):
        """
        Yield each end node of tree in order of depth-first traversal.
        """
        if self._end_nodes:
            return (node for node in self._end_nodes)
        else:
            return (node for node in self.iternodes() if node.is_end)

    def iternodes(self, **kwargs):
        """
        Yield each node during depth-first traversal of tree.
        """
        node = kwargs.get('node', self.top)
        yield node

        if isinstance(node, ParseTreeThruNode):
            for child in node.children:
                for n in self.iternodes(node=child):
                    yield n
                    
    def iterwords(self):
        """
        Yield each word of the sentence in proper order.
        """
        return (node.word for node in self.iterendnodes() if not node.tag == '-NONE-')

    def search(self, tag=None, word=None, tag_flag=0, word_flag=0, **kwargs):
        """
        Return list of nodes matching parameters.

        No constraint is placed on a field that evaluates to False, i.e. calling
        with tag='PREP' and word='' with no flags will return every node whose
        tag is exactly PREP. If both tag and word evaluate to False, every node
        in the tree will be returned.

        Flags are documented in the docstring of this class. If no flag is
        passed for an attribute, the default style of search is exact match.

        All searches are case-sensitive for the time being.
        """
        results = []
        
        tagfunc = self._get_comparison_function(tag_flag)
        wordfunc = self._get_comparison_function(word_flag)

        if word:
            for node in self.iterendnodes():
                if tagfunc(tag, node.tag) and wordfunc(word, node.word):
                    results.append(node)
        else:
            for node in self.iternodes():
                if tagfunc(tag, node.tag):
                    results.append(node)

        return results

    def _build_from_lines(self, lines):
        """
        Lines expects list of strings that may or may not end in a newline.
        """
        # Create top node
        self.top = ParseTreeThruNode(None, 'TOP')
        
        # Build tree line by line
        node = self.top
        for line in lines:
            stripped = line.strip()
            
            while stripped:
                # If closing a tag, move up to parent and continue
                if stripped[0] == ')':
                    node = node.parent
                    stripped = stripped[1:]
                    continue
                elif stripped[0] == '\ufeff': # Skip BOM character
                    stripped = stripped[1:]
            
                match = re.match(thrunode_pattern, stripped)
                
                if match is not None:
                    tag = match.group('tag')
                    if not tag == 'TOP':
                        node = ParseTreeThruNode(node, tag)
                    stripped = stripped[len(match.group()) - 1:]
                else:
                    match = re.match(endnode_pattern, stripped)
                    
                    if match is None:
                        raise TreeConstructionError("Unexpected tag situation. " +
                            "No tag opening or close found.\n" +
                            "Segment: {0}\nLine: {1}\n".format(stripped, line)
                        )
                    
                    node = ParseTreeEndNode(node, 
                        match.group('tag'), match.group('word')
                    )
                    stripped = stripped[len(match.group()) - 1:]

    def _get_comparison_function(self, flag):
        """
        Return the comparison functions for tag and word to be used in
        search(), in that order.

        The comparisons all have the signature (phrase, s)
        """
        exact = lambda phrase, s: phrase == s if phrase else True
        contains = lambda phrase, s: phrase in s
        startswith = lambda phrase, s: s.startswith(phrase)
        rematch = lambda pattern, s: re.match(pattern, s)

        funcmap = {
            self.EXACT : exact,
            self.CONTAINS : contains,
            self.STARTSWITH : startswith,
            self.REMATCH : rematch
        }

        try:
            comparison_func = funcmap[flag]
        except KeyError:
            raise SearchFlagError(
                'Invalid flag passed for flag: {0}\n'.format(flag) +
                'Use the named constants in the ParseTree class (e.g. ' +
                'ParseTree.CONTAINS, ParseTree.EXACT) as flags.'
            )

        return comparison_func

    # TODO
    # Currently each word is separated by a space, excluding punctuation.
    # Must figure out Arabic rules.
    @property
    def sentence(self):
        sentence = ''
        
        for i, node in enumerate(self.iterendnodes()):
            if node.tag == 'PUNC':
                sentence += node.word
            elif i == 0:
                sentence += node.word
            elif not node.tag == '-NONE-':
                sentence += ' {0}'.format(node.word)
                
        return sentence
