# pyRex/Lexer.py
# This utility provides the framework for building symbol tables
# This is done with the ParseMap class, objects of which pertain
# to a string of text that is parseable with regular expressions.
# 
# ParseMap objects can create other ParseMaps in order to recursively
# handle inputs. This file, when run directly, will perform some basic 
# tests. You can view the bottom of this file for basic usage, or
# the examples folder for more robust usage examples.

import re
from collections import OrderedDict

VERBAL=False

class ParseMapError(Exception):
    def __init__(self):
        self.value = ""

    def __str__(self):
        return self.value

class InputMatchError(ParseMapError):
    def __init__(self, regex, input_str):
        self.value = "\"%s\" not a valid regular expression for \"%s\"" % (regex,input_str)

class MissingTokenError(ParseMapError):
    def __init__(self, missing, input_string, regex):
        self.missing = missing
        self.value = "Couldn't find matches for unignored tokens: %s, with regex \"%s\" and input \"%s\"" % (missing, regex, input_string)

class RegexMismatchError(ParseMapError):
    def __init__(self, mapped_regex, raw_regex):
        self.value = "mapped regex %s is not equal to %s" % (mapped_regex, raw_regex)

class NoMatchError(ParseMapError):
    def __init__(self, regex, substring):
        self.value = "Parsing cannot continue. There is no match for regex \"%s\" in substring \"%s\"" % (regex,substring)

class ParseMap(object):
    # The IGNORE argument tells the map to consume a piece of the regex
    # without doing anything with it
    IGNORE = 0x0

    # The LITERAL argument tells the map to store the symbol found
    # in the corresponding symbol table (self.symbols) 
    LITERAL = 0x1

    def __init__(self, regextable=()):
        """
        regextable is a tuple (or list) that describes the 
        symbol names and the regular expressions to be used,
        in the order they are to be consumed, as well as
        what to do with the corresponding text that is found.
    
        The last part (text to be found), can be either:
            1) ParseMap.IGNORE (consume the text without storing it)
            2) ParseMap.LITERAL (store the text as-is)
            3) Any function (store the output from the function, using the text as a single-argument input)

        for example, with the regular expression:
            "def ?[^ \(]+ ?\([^\)]\) ?:\n"
        (
            ("definition"   , "def ?"       , ParseMap.IGNORE),
            ("func_name"    , "[^ ?\(]+"    , ParseMap.LITERAL),
            ("args_open"    , "\("          , ParseMap.IGNORE),
            ("args"         , "[^\)]"       , arg_parser)
            ("args_close"   , "\)"          , ParseMap.IGNORE),
            ("colon"        , " ?:"         , ParseMap.IGNORE)
        )

        arg_parser would have to be a function that takes one argument, 
        and returns SOMETHING that can be stored in the symbol table. 

        """
        self.regex_table = regextable

        # All matches will be checked against this constructed regex
        # if it doesn't match, it's most likely because there's a problem
        # with how the ParseMap was constructed, rather than the user input
        tmp_list = [entry[1] for entry in regextable]
        self.regex = "".join(tmp_list)

    def parse(self, input_string):
        """
        Running the parse method will check the input string against
        this parser's regular expression, making sure that it's a match.
        It will then go chunk by chunk, based on the parse map, consuming
        the input and storing the symbols requested.
        The return value will be a map of the stored symbols and their values.
        """
        self.symbols = OrderedDict()
        for entry in self.regex_table:
            if entry[2] is not ParseMap.IGNORE:
                self.symbols[entry[0]] = None
        
        # Make sure that there is exactly one match for the overarching regex
        all_matches = re.findall(self.regex,input_string)

        if not all_matches:
            raise InputMatchError(self.regex,input_string)

        self.parsed_token = re.findall(self.regex,input_string)[0]
        
        table_index = 0
        str_index = 0
        
        while table_index < len(self.regex_table):
            table_index, str_index = self.consume_input(self.parsed_token, table_index,str_index)
        
        if (None in self.symbols.values()):
            raise MissingTokenError([token for token in self.symbols if self.symbols[token] is None], input_string, self.regex)

        return self.symbols


    def consume_input(self, input_string, table_index, start_index):
        global VERBAL # for givine feedback -- does not change

        # The bit of text we'll be working with 
        substring = input_string[start_index:]

        # The piece of the parse map we'll be working with
        table_row = self.regex_table[table_index]


        identifier = table_row[0]
        regex = table_row[1]
        handler = table_row[2]
        
        if VERBAL:
            print("checking substring \"%s\" against regex \"%s\"" % (substring, regex))

        # Will be a re object or None, if there is no match
        # we are only going to work with the FIRST match, after which
        # it will be consumed
        result = re.match(regex,substring)
        
        if not result:
            raise NoMatchError(regex, substring)
        
        match = result.group()

        # If we're storing it literally, then we simply do so
        if handler is ParseMap.LITERAL:
            # Make sure there hasn't been an error creating the map
            assert(self.symbols[identifier] is None)
            self.symbols[identifier] = match

        # If the handler is a function, we're going to pass the 
        # matched text into the function, and store the result instead
        elif hasattr(handler, '__call__'):
            self.symbols[identifier] = handler(match)

        # Move onto the next piece of syntax
        table_index += 1

        # Consume the substring in the input
        start_index = start_index + len(match)

        return table_index, start_index

    def assert_match(self, regex):
        """
        While it's probably easiest to simply use the piecemeal parser, 
        for more complex expressions you want to test elsewhere first, you
        can double-check that the regex you're testing matches the map
        you've created by passing the complete regex here to be sure that
        you haven't forgotten any of it.
        """
        if (self.regex != regex):
            raise(RegexMismatchError(self.regex, regex))

if __name__ == "__main__":
    # Running this program directly will run tests
    # in verbal mode. You can turn off verbal mode
    # by using the --quiet flag

    from argparse import ArgumentParser
    parser = ArgumentParser("Tests the pyRex regular expression lexer utility")
    parser.add_argument("--quiet", action="store_false", default=True)
    args = parser.parse_args()

    VERBAL = args.quiet
    test_regex = "(def)[\t ]+[a-zA-Z_][a-zA-Z0-9_]+[\t ]*:[\t ]*\n"

    # Make sure there's not a problem with the above regular expression
    # in its most basic form before beginning the tests
    assert(re.match(test_regex, "def foo:\n"))

    # Set up the parse map
    regex_table = (
            ("def"      , "(def)[\t ]+"             , ParseMap.IGNORE),
            ("func_name", "[a-zA-Z_][a-zA-Z0-9_]+"  , ParseMap.LITERAL),
            ("endl"     , "[\t ]*:[\t ]*\n"         , ParseMap.IGNORE)
    )
    
    parser = ParseMap(regex_table)
    parser.assert_match(test_regex)
    passing_tests = {
            "def foo:\n"             : "foo", 
            "def        f2oo:\n"    : "f2oo", 
            "def foo3 : \n"         : "foo3"
            }

    failing_tests = ("def 1foo:\n", "def\tfoo:", "def:")

    for test in passing_tests:
        result = parser.parse(test)
        if (result["func_name"] != passing_tests[test]): raise Exception

    for test in failing_tests:
        try:
            result = parser.parse(test)
            raise Exception
        except ParseMapError:
            continue

    # Run a test against input that must be transformed with a function
    test_regex = "(sum)[\t ]+[0-9]+[\t ]*(and)[\t ]*[0-9]+"
    parser = ParseMap((
        ("sum"  , "(sum)[\t ]+"         , ParseMap.IGNORE),
        ("int1" , "[0-9]+"              , int),
        ("and"  , "[\t ]*(and)[\t ]*"   , ParseMap.IGNORE),
        ("int2" , "[0-9]+"              , int)
        )
    )
    parser.assert_match(test_regex)
    test_string = "sum 4 and 5"
    result = parser.parse(test_string)
    assert( ( result["int1"] + result["int2"]) == 9 )

    print("All tests passed!")
