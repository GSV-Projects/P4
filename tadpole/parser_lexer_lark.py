grammar = r"""
?start: program

program: (stmt | def)*

?stmt: IDENT "=" rvalue ";"                         -> assign
     | IDENT "(" (expr ("," expr)*)? ")" ";"        -> func_call
     | IDENT "[" expr "]" ";"                       -> array_indexing
     | "while" "(" expr ")" "do" "{" stmt* "}"      -> while_stmt
     | "if" "(" expr ")" "then" "{" stmt* "}" ("else" "{" stmt* "}")?    -> if_stmt
     | STOP ";"                                     -> stop
     | SKIP ";"                                     -> skip
     | "return" expr ";" -> return_stmt

?rvalue: "[" (expr ("," expr)*)? "]"                -> array
       | IDENT "." call ("." call)*                 -> method_call
       | "{" column* "}"                            -> table
       | expr

?column: ( IDENT ":" "[" column_content "]" ";" )   -> column

?column_content: (expr ("," expr)*)?                -> array

?call: IDENT "(" (expr ("," expr)*)? ")"

?def: "function" IDENT "(" param ")" body
    | "function" IDENT "(" param ")" "returns" type body

body: "{" stmt* "}"

?type: TYPE_BOOL
     | TYPE_FLOAT
     | TYPE_INT
     | TYPE_STRING
     | "[" type "]"

param: (param_item ("," param_item)*)?

?param_item: type IDENT

?expr: and_expr "or" expr
     | and_expr

?and_expr: not_expr "and" and_expr
         | not_expr

?not_expr: NOT not_expr 
         | eq_expr

?eq_expr: eq_expr "==" plus_expr        -> equal
        | eq_expr "/=" plus_expr        -> not_equal
        | eq_expr "<" plus_expr         -> less
        | eq_expr "<=" plus_expr        -> less_eq
        | eq_expr ">" plus_expr         -> greater
        | eq_expr ">=" plus_expr        -> greater_eq
        | plus_expr

?plus_expr: plus_expr "+" mult_expr     -> add
          | plus_expr "-" mult_expr     -> sub
          | mult_expr

?mult_expr: mult_expr "*" exp_expr      -> mult
          | mult_expr "/" exp_expr      -> divide
          | mult_expr "mod" exp_expr    -> mod
          | exp_expr

?exp_expr: unary_expr ("^" unary_expr)*

?unary_expr: NEG unary_expr
           | term

?term: IDENT "(" (expr ("," expr)*)? ")"   -> func_call
     | IDENT "[" expr "]" ";"              -> array_indexing
     | IDENT
     | FLOAT
     | INT
     | STRING
     | TRUE
     | FALSE
     | NA
     | "(" expr ")"

// --- Keywords ----
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

TYPE_BOOL: "bool"
TYPE_FLOAT: "float"
TYPE_INT: "int"
TYPE_STRING: "string"


// --- Operators ---
EQUAL: "=="
INEQUAL: "/="
LESSEQ: "<="
GREATEQ: ">="
LESS: "<"
GREAT: ">"
ADD: "+"
NEG: "-"
EXPO: "^"
MULT: "*"
DIVIDE: "/"
ASSIGN: "="
DOT: "."

// --- Literals ---
TRUE: "true"
FALSE: "false"
NA: "NA"

// --- Identifiers ---
IDENT: /[A-Za-z_][A-Za-z0-9_]*/

// --- Numbers ---
FLOAT: /((0|[1-9][0-9]*)\.[0-9]+)([eE][+-]?[0-9]+)?/
%import common.INT

// --- Strings ---
STRING: /"([^"\\]|\\.)*"/ 

// --- Whitespace ---
%import common.WS
%ignore WS
"""

code = """
tappel = {
col1: [1, 2];
col2: ["hej", "hvad"];
};
"""

from lark import Lark
# Dårlig løsning på at vi gerne skulle kunne køre de forskellige filer fra forskellige stedet
try:
    from .parsertransformer import MyTrans
    #from .typechecker import Typechecker
except ImportError:
    from parsertransformer import MyTrans
    #from typechecker import Typechecker


def transformtree(tree):
    return MyTrans().transform(tree)

parser = Lark(grammar, parser="lalr", strict=True)

parsetree = parser.parse(code)

result = transformtree(parsetree)
#Typechecker().transform(result)
#print("Parse \n", parsetree.pretty())

print("AST \n", result.pretty())






