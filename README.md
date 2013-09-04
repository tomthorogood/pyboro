# What is pyboro? #

pyboro is a regular expression lexer built with python.

pyboro is suitable for parsing syntax and building symbol tables,
and it's easy to use this information to extend into building your
own code generation and so on.

The name comes from 'borosilicate', which is the type of glass used
in making [Pyrex](http://en.wikipedia.org/wiki/Pyrex) glassware. The repository
was originally called pyRex, but this conflicted with similarly named packages 
already existing in PyPi.

# Installation #

    pip install pyboro
    easy_install pyboro

Then:
    import pyboro
Or:
    from pyboro import Lexer
    from pyboro import Consumer

# The Lexer Module #

The Lexer module (`pyboro.Lexer`) is used to define your symbol
tables. You'll create `ParseMap` objects for each of the
regular expressions you want to be able to parse. 

These are set up in the following way:

    my_parser = pyboro.Lexer.ParseMap((
        ("token name",  "regular expression",   handler),
            #...
    ))

In the above, "token name" is a brief title for the regular expression.
For those that will be ignored, the name is irrevant for functionality,
but good for people who might have to maintain your code. For tokens that will
be preserved, the token name is how you will access the matched expression.
    
    # `let x = 17;`, where the ParseMap searches for a variable name and an assignment:
    
    result = my_parser.parse(input_string)
    print(result['variable name']) #prints 'x'
    print(result['assigment']) #prints '17'


"regular expression" is the regular expression matches the title.

"handler" is either a function that you create, OR a ParseMap constant.

The ParseMap class has two constants:

    pyboro.Lexer.ParseMap.IGNORE     # consumes the input matching the regex, but does not store it
    pyboro.Lexer.ParseMap.LITERAL    # consumes and stores the input exactly as its found

If you use the name of a function for the handler, it must take a single string as an argument,
and output a single string. This allows you to transform or verify inputs further. Note that in python,
basic types are also functions. This makes it easy to convert the input strings into integers, etc

    ("integer assignment", regex_foo,   int)
    

For a more in-depth look at the Lexer, read through [the tutorial](#tutorial).

# The Consumer Module #

While the Lexer module is used to set up your symbol tables, the Consumer module is used to actually
consume input and return result tables.

A Consumer object requires  a single argument a list of ParseMaps:

    my_consumer = Consumer.Consumer([my_parser,my_other_parser,my_third_parser])

Whenever an input string is given to that object, it will iterate over the input, checking against
each of the ParseMaps in order. It will do this until either a) all of the input is consumed (hooray!)
or b) a syntax error is found (boo).

It will return the results from each of the ParseMaps, along with a reference to the map that found it. 
    
    my_consumer = Consumer.Consumer([EmailAddress, Name, FavoriteColor])
    
    results = None
    with open("input_file.txt") as f: 
        results = my_consumer.parse(f.read()) #will throw an error if the entire file cannot be parsed cleanly
    
    for result in results:
        if result is EmailAddress:
            print result["address"]

Optional arguments to the conumser module:

    help: A text to be displayed if an error is found
    formatting_func: a function which takes input, formats it, and returns it.

This will produce helpful error messages like:

"Syntax error near 'dafsdfdfdjfkdljkj 12;', expecting valid type."

where 'dafsdfdfdjfkdljkj 12;' is the output of formatting\_func, and 
"valid type" is the help message.

<a name="tutorial"></a>
# Brief Tutorial of Lexing#

Before you begin using pyboro, you should have an idea how to use
regular expressions with Python's `re` module. If you need help with
this, check out the [official documentation](http://docs.python.org/library/re.html).

Next, you'll need an idea of what you'll be parsing. For this example,
let's say that you want to parse this line:

    int aNumber = 17;

We have five things here: 

+ `int` : a variable declaration 
+ `aNumber` : an identifier
+ `=` : an operator
+ `17` : an assignment to the variable

We also have whitespace between these things. 

What are the regular expressions for these things?

+ `int`
 + the literal 'int'
+ `[ \t]+`
 + at least one space or tab
+ `[_a-zA-Z][_a-zA-Z0-9]*`
 + A string of at least one character. It must start with an underscore or letter, but may have numbers after it.
+ `[ \t]*`
 + any number of spaces or tabs
+ `\=`
 + The assignment operator
+ `[ \t]*`
 + any number of spaces or tabs
+ `[^;]+`
 + at least one character that isn't a semicolon (more on this in a second)
+ `[ \t]*`
 + any number of spaces or tabs
+ `;`
 + a semicolon.

The reason we're allowing any number of things (except semicolons) in
the assignment is because we may not have a literal integer here. We may
have a function call, for instance, which returns an integer. We'll deal
with whatever that is at a later time (not in this example).

Now that we've done that, we can create a 

`ParseMap`

To create a `ParseMap` of everything above, we do it like this:

```python
a_parser = Lexer.ParseMap((
    ("type_declaration" ,   "int",                      Lexer.ParseMap.LITERAL),
    ("whitespace"       ,   "[ \t]+",                   Lexer.ParseMap.IGNORE),
    ("identifier"       ,   "[_a-zA-Z][_a-zA-Z0-9]*",   Lexer.ParseMap.LITERAL),
    ("whitespace"       ,   "[ \t]*",                   Lexer.ParseMap.IGNORE),
    ("assignment_op"    ,   "\=",                       Lexer.ParseMap.IGNORE),
    ("assignment"       ,   "[^;]+",                    validate_as_integer),
    ("whitespace"       ,   "[ \t]*",                   Lexer.ParseMap.IGNORE),
    ("statement_end"    ,   ";",                        Lexer.ParseMap.IGNORE)
))
```

We give the ParseMap a tuple of tuples, each of which has the following:

1. A short description of what the regex represents
2. A regular expression
3. Something that tells the parser what to do with the token found

Let's examine the third column:

1. `Lexer.ParseMap.LITERAL` tells the parseMap to store the data found exactly as it is stated.
2. `Lexer.ParseMap.IGNORE` will discard the information 
3. `validate_as_integer` is a function that maybe we've already written, which takes in the 
token as a string, and returns some other value which will be stored. 

We can then feed the parser input like so:
    results = a_parser.parse(input_string)

`results` will be an `OrderedDict` whose keys are the descriptions above,
and whose values are the parsed values (or literal values). Therefore, in this
instance, `results` will look like this:

```python
results['type_declaration'] = 'int'
results['identifier'] = 'aNumber'
results['assignment'] = 17
```

