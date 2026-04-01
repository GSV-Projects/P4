grammar = r"""
start: program

program: (stmt | def)*

stmt: IDENT "." call ";"    -> method_call 
    | IDENT "=" rvalue ";"  -> assign
    | IDENT "(" (expr ("," expr)*)? ")" ";"     -> call
    | "while" "(" expr ")" "do" "{" stmt* "}"
    | "if" "(" expr ")" "then" "{" stmt* "}" ("else" "{" stmt* "}")?    -> ifs #
    | "stop" ";"    -> stop #
    | "skip" ";"    -> skip #
    | "return" expr ";"


rvalue: "[" (expr ("," expr)*)? "]"
    | expr
    | "{" IDENT ("," IDENT)* ":" term ("," term)* "}"


type: "bool"
    | "float"
    | "int"
    | "string"
    | "table"
    | "column"
    | "[" type "]"

call: IDENT "(" (expr ("," expr)*)? ")"

param: (type IDENT ("," type IDENT)*)?

def: "function" IDENT "(" param ")" ret

ret: "returns" type "{" stmt* "}"
   | "{" stmt* "}"

expr: and_expr ("or" and_expr)*     -> expr

and_expr: not_expr ("and" not_expr)*    -> and_expr

not_expr: ("not")* eq_expr  -> not_expr

eq_expr: additive_expr (("==" | "/=" | "<" | "<=" | ">" | ">=") additive_expr)? -> eq_expr

additive_expr: multiplicative_expr (("+" | "-") multiplicative_expr)* -> additive_expr

multiplicative_expr: expo_expr (("*" | "/" | "mod") expo_expr)* -> multiplicative_expr

expo_expr: unary_expr ("^" unary_expr)* -> expo_expr

unary_expr: ("-")* term -> unary_expr

term: IDENT ("(" (expr ("," expr)*)? ")" | "[" expr "]")?
    | "." call
    | FLOAT
    | NUM
    | STRING
    | BOOL
    | NA
    | "(" expr ")"

# Token specification 
// --- Keywords ---
WHILE: "while"
DO: "do"
IF: "if"
THEN: "then"
ELSE: "else"
STOP: "stop"
SKIP: "skip"
RETURN: "return"
FUNCTION: "function"
RETURNS: "returns"
AND: "and"
OR: "or"
NOT: "not"
MOD: "mod"

// --- Operators ---
EQUAL: "=="
INEQUAL: "/="
LESSEQ: "<="
GREATEQ: ">="
LESS: "<"
GREAT: ">"
ADD: "+"
SUB: "-"    # subtraction
#NEG: "-"    # unary negative
MULT: "*"
DIVIDE: "/"
ASSIGN: "="

// --- Literals ---
BOOL: "true" | "false"
NA: "NA"

// --- Identifiers ---
IDENT: /(?!true|false)[A-Za-z_][A-Za-z0-9_]*/

// --- Numbers ---
FLOAT: /((0|[1-9][0-9]*)\.[0-9]+)([eE][+-]?[0-9]+)?/

// --- Strings ---
STRING: /"([^"\\]|\\.)*"/

// --- Whitespace ---
%import common.WS
%import common.INT -> NUM
%ignore WS
"""

code = """
a = 5 + 5 + 5;
"""

from lark import Lark
from parsertransformer import MyTrans

def transformtree(tree):
    return MyTrans().transform(tree)

parser = Lark(grammar, parser="lalr", strict=True)


parsetree = parser.parse(code)
#result = transformtree(parsetree)
print("Parse \n", parsetree.pretty())
#print("AST \n", result.pretty())
