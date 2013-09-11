import re
import Lexer
from Lexer import ParseMap

VERBAL = False

class PyBoroSyntaxError(Exception):
    def __init__(self, inputstr, expecting):
        self.input = re.escape(inputstr)
        self.expecting = expecting

    def __str__(self):
        message = "SyntaxError near %(input)s\nExpecting: %(expecting)s\n" % (self.__dict__)
        return message


class ConsumerIterator(object):
    """
    The ConsumerIterator is a class used within the Consumer class
    that keeps track of the position of the parser within the given 
    input. 
    """
    
    def __init__(self, input_str):
        self.string = input_str
        self.pos = 0
        self.newlines = input_str.count("\n")

    def __len__(self):
        """
        Gives the remaining length of the input.
        """
        return len(self.string[self.pos:])

    def __add__(self,num):
        return self.pos + num

    def __iadd__(self,num):
        self.pos += num

    def __str__(self):
        return self.string

    def __nonzero__(self):
        return self.pos < len(self.string)

    def search(self,parser):
        try:
            prev_pos = self.pos
            result = parser.parse(self.string[self.pos:])
            self.pos += len(parser.parsed_token) + parser.offset
            
        except Lexer.ParseMapError:
            # If the expression does not match, we'll let the caller
            # know it needs to try another one.
            result = None
        return result


class Consumer(object):
    """
    The Consumer class has one purpose: to consume input. 
    If it finds input it can't consume, it stops, and 
    throws a SyntaxError. A list of valid ParseMaps given to
    the consumer upon instantiation will be tested until either
    a) a PyBoroSyntaxError is thrown, or b) the end of the input
    is reached.
    """
    def __init__(self, parse_maps, help="valid syntax", formatting_func=lambda s: s):
        assert isinstance,parse_maps(list,tuple)
        for e in parse_maps:
            assert isinstance(e,ParseMap)
        self.parse_maps = parse_maps
        self.num_lines = 0
        self.help = help
        self.error_formatting = formatting_func


    def parse(self, input_string):
        """
        Takes an input string, checks it against all of the parsers
        passed in until all input is consumed (or an error is met),
        and returns a list of token results, along with the parser
        that matched them.
        """
        if not isinstance(input_string,(str,unicode)):
            raise TypeError("Expected string, %s found" % repr(type(input_string)))
        
        iterator = ConsumerIterator(input_string)
        results = []
        self.num_lines += iterator.newlines

        # This loop runs as long as there is input
        # left in the iterator.
        while iterator:

            current_position = iterator.pos

            # Tries each of the parsers pased in against the 
            # next input. 
            for parser in self.parse_maps:
                result = iterator.search(parser)
                if result:
                    results.append((result,parser))
                    break

            # If none of the parsers manage to consume any input,
            # there's a problem with the next token of the input.
            if iterator.pos == current_position:
                trunc_input = input_string[iterator.pos:]
                err_txt = self.error_formatting(trunc_input)
                raise PyBoroSyntaxError(err_text, self.help)
           
            # Set a new benchmark and keep going.
            else:
                current_position = iterator.pos

        return results
