# -*- coding: utf-8 -*-


class Code(object):
    """
    This is a Code object that maintains and evaluable Python piece of code.
    Attributes:
        source(str): The original Python code as an string.
        code(bytes): The compiled Python code.
    """
    def __init__(self, source, code):
        self.source = source
        self.code = code


class PyParser(object):
    """
    This class parses Python code and convert it into a Code object
    """

    def __init__(self, filename=None):
        self.filename = filename or '<string>'

    def parse_python(self, source):
        """
        Given an string convert it into a Code object
        Parameters:
            source(str): The python code as string.
        Returns:
            Code: Parsed python code.
        """
        return Code(source, compile(source + "\n", filename=self.filename, mode='eval'))
