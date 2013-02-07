from src import *

IGNORE  = Lexer.ParseMap.IGNORE
LITERAL = Lexer.ParseMap.LITERAL
Lexer.VERBAL = True
def trim(string):
    return string.strip()

PoemDeclaration = Lexer.ParseMap((
    ("begin",   r"poem[ \t]+",               IGNORE),
    ("title",   r"[^(:]+",                   trim),
    ("author",  r"(\([^)]+\))?",             LITERAL),
    ("delim",   r":\n",                      IGNORE),
    ("poem",    r"((.*\n)+)(?=end poem\n)",  LITERAL),
    ("end",     r"end poem\n",               IGNORE)
))


LetDeclaration = Lexer.ParseMap((
    ("begin",       "let[ \t]+",        IGNORE),
    ("identifier",  "[a-z]+",           LITERAL),
    ("oper_assign", "[ \t]*\=[ \t]*",   IGNORE),
    ("assignment",  "[^\n]+",           LITERAL)
))

AliasDeclaration = Lexer.ParseMap((
    ("begin",       "alias[ \t]+",      IGNORE),
    ("identifier",  "[a-z]+",           LITERAL),
    ("prep",        "[ \t]+as[ \t]+",   IGNORE),
    ("alias",       "[a-z]+",           LITERAL),
    ("end",         "[ \t]*\n" ,        IGNORE)
))

NewLines = Lexer.ParseMap([
    ("newline", "[\n]+",            IGNORE)
])

Comment = Lexer.ParseMap([
    ("comment", "#.*\n",            IGNORE)
])

testConsumer = Consumer.Consumer([PoemDeclaration,LetDeclaration,AliasDeclaration,NewLines,Comment])

results = None
with open("test_input.txt") as f:
    inputstr = f.read()
    print(inputstr)
    results = testConsumer.parse(inputstr)

for result in results:
    if result[1] is PoemDeclaration:
        print("I've found a poem by %s called \"%s\": %s" % (result[0]["author"],result[0]["title"],result[0]["poem"]))
