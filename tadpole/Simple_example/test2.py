from test3 import MyTrans
import time
from lark import Lark, ast_utils, Transformer, v_args

start = time.process_time()


grammar = r"""
start: stmt+

?expr: expr "+" term -> add
    | expr "-" term -> subtract
    | term

?term: NUMBER
    | IDENT
    | BOOL 


?stmt: assign 
| defi

defi: IDENT param "=" expr 

param: "("(term)+")"


assign: IDENT "=" expr

NUMBER: ("0".."9")+
BOOL: "TRUE" | "FALSE"
LETTER: ("A".."Z" | "a".."z")
IDENT: LETTER (LETTER | NUMBER)*
WHITESPACE: (" " | "\n")+
%ignore WHITESPACE
"""

text = """
A = 1+2
"""

from lark import Lark
parser = Lark(grammar, start="start")  # Scannerless Earley is the default

#tokens = parser.lex(text)
#print("Tokens (lexer output):")
#for t in tokens:
#    print(t)

#tree = parser.parse(text)
#print(tree.pretty())

#print(time.process_time() - start)

tree = parser.parse(text)

def parse(tree):
    return MyTrans().transform(tree)
    
result = parse(tree)
print(tree.pretty())
print(result)
