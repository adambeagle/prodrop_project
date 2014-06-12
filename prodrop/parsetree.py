"""
parse_tree.py
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
        self._children += (child, )
        
    @property
    def children(self):
        return self._children
    
class ParseTreeEndNode(ParseTreeNode):
    """
    ATTRIBUTES:
      * word
    """
    def __init__(self, parent, tag, word):
        super().__init__(parent, tag)
        self.word = word

class ParseTree:
    """
    Defines a rudimentary syntactic parse tree built from Penn Treebank
    bracketed notation as found in .parse files.
    
    Nodes are either ParseTreeThruNode or ParseTreeEndNode, defined above and
    have 'children' and 'word' attributes, respectively. All nodes have a 
    'parent' attribute.
    
    TODO improved navigation and searching. 
    
    ATTRIBUTES:
      * top - The top-level tree node. This will always have the tag 'TOP'
    """
    def __init__(self, lines):
        """Expects list of strings 'lines.'"""
        self.top = None
        
        self._build_from_lines(lines)
        
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
                        
