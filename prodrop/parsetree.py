"""
parsetree.py
Author: Adam Beagle

PURPOSE:
    Contains a data structure that holds a parse tree and facilitates
    easy navigation and searching.
"""
import re

from exceptions import TreeConstructionError
   
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
    Defines a rudimentary syntactic parse tree built from Penn Treebank
    bracketed notation as found in .parse files.
    
    Nodes are either ParseTreeThruNode or ParseTreeEndNode, defined above and
    have 'children' and 'word' attributes, respectively. All nodes have a 
    'parent' attribute.
    
    TODO improved navigation and searching. 
    
    ATTRIBUTES:
      * sentence
      * top - The top-level tree node. This will always have the tag 'TOP'
      * treebank_notation - The Penn Treebank bracketed notation from which
                            the tree was built.
      
    METHODS:
      * iternodes
      * search_by_tag
    """
    def __init__(self, lines):
        """
        Expects list of strings 'lines' that represent a tree as given in a
        .parse file.
        """
        self.top = None
        
        join_char = '' if lines[0][-1] == '\n' else '\n'
        self.treebank_notation = join_char.join(lines)

        self._build_from_lines(lines)
        
    def iterendnodes(self):
        """
        Yield each end node of tree in order of depth-first traversal.
        """
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
        return (node.word for node in self.iterendnodes())

    def search_by_tag(self, tag):
        """
        Return list of nodes with tag given by 'tag.'
        
        Currently returns only tags that are exact matches. 
        TODO allow for base tag only search, etc.
        TODO case-insensitive?
        """
        matches = []
        
        for node in self.iternodes():
            if node.tag == tag:
                matches.append(node)
                
        return matches

    def _build_from_lines(self, lines):
        """
        Lines expects list of strings that may or may not end in a newline.
        """
        # Create top node
        self.top = ParseTreeThruNode(None, 'TOP')
        lines[0] = lines[0][5:] # Ignore '(TOP ' in first line
        
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
            
                match = re.match(thrunode_pattern, stripped)
                
                if match is not None:
                    node = ParseTreeThruNode(node, match.group('tag'))
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
      
    # TODO
    # Currently each word is separated by a space. At minimum, punctuation
    # should be accounted for.
    @property
    def sentence(self):
        sentence = ''
        
        for i, node in enumerate(self.iterendnodes()):
            if node.tag == 'PUNC':
                sentence += node.word
            elif i == 0:
                sentence += node.word
            else:
                sentence += ' {0}'.format(node.word)
                
        return sentence
            
