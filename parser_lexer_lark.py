grammar = r"""
start: program

program: (stmt | def)*

stmt: IDENT stmt_suffix ";"
    | "while" "(" expr ")" "do" "{" stmt* "}"
    | "if" "(" expr ")" "then" "{" stmt* "}" ("else" "{" stmt* "}")?
    | "stop" ";"
    | "skip" ";"
    | "return" expr ";"

stmt_suffix: "." call
           | "=" rvalue
           | "(" (expr ("," expr)*)? ")"

rvalue: "[" (expr ("," expr)*)? "]"
      | expr

?type: "bool"
    | "float" -> float
    | "int" -> int
    | "string" -> hejsa
    | "table"
    | "column"
    | "[" type "]"

call: IDENT "(" (expr ("," expr)*)? ")"

param: (type IDENT ("," type IDENT)*)?

def: "function" IDENT "(" param ")" ret

ret: "returns" type "{" stmt* "}"
   | "{" stmt* "}"

?expr: and_expr ("or" and_expr)*

?and_expr: not_expr ("and" not_expr)*

?not_expr: ("not")* eq_expr

?eq_expr: plus_expr (("==" | "/=" | "<" | "<=" | ">" | ">=") plus_expr)?

?plus_expr: mult_expr (("+" | "-") mult_expr)*

?mult_expr: exp_expr (("*" | "/" | "mod") exp_expr)*

?exp_expr: unary_expr ("^" unary_expr)*

?unary_expr: ("-")* term

?term: IDENT ("(" (expr ("," expr)*)? ")" | "[" expr "]")?
     | "." call
     | FLOAT
     | NUM
     | STRING
     | BOOL
     | NA
     | "(" expr ")"

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
SUB: "-"
MULT: "*"
DIVIDE: "/"
ASSIGN: "="

// --- Literals ---
BOOL: "true" | "false"
NA: "NA"

// --- Identifiers ---
IDENT: /[A-Za-z_][A-Za-z0-9_]*/

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
x = 5;

result = x + 5;

function hej (string x) returns int {
    return 15;
}

hej(x);

if (result == 10) then {
    return 1;
} else {
    return 0;
}

"""

from lark import Lark
from lark.tree import pydot__tree_to_png
parser = Lark(grammar)

print(parser.parse(code).pretty())
tree = parser.parse(code)
pydot__tree_to_png(tree, "tree.png")