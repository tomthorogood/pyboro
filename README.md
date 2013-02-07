# What is pyRex? #

pyRex is a regular expression lexer built with python.

pyRex is suitable for parsing syntax and building symbol tables,
and it's easy to use this information to extend into building your
own code generation and so on.

# Installation #

No installation required. Just download it and you can use

    from pyRex import Lexer
    # or
    from pyRex import Consumer


# Brief Tutorial #

Before you begin using pyrex, you should have an idea how to use
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

