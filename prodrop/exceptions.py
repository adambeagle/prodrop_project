"""
exceptions.py
Author: Adam Beagle

PURPOSE:
  Contains all custom exception classes for the prodrop package.
"""

###############################################################################
# ParseTreeError and iheritors
class ParseTreeError(Exception):
    """Base class for all parse tree related errors."""
    pass

class SearchFlagError(ParseTreeError):
    pass

class TreeConstructionError(ParseTreeError):
    pass

###############################################################################
# Other
class MissingParseFilesError(Exception):
    pass

class NoTreesFoundError(Exception):
    pass



