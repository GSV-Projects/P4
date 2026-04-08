grammar = r"""
?start: program

?program: (stmt | def)*

?stmt: IDENT "." call ";"                       -> method_call
     | IDENT "=" rvalue ";"                      -> assign
     | IDENT "(" (expr ("," expr)*)? ")" ";"     -> func_call
     | "while" "(" expr ")" "do" "{" stmt* "}"   -> while_stmt
     | "if" "(" expr ")" "then" "{" stmt* "}" ("else" "{" stmt* "}")?    -> if_stmt
     | STOP ";"                                  -> stop
     | SKIP ";"                                  -> skip
     | RETURN expr ";" -> return_stmt

?rvalue: "[" (expr ("," expr)*)? "]" -> array
       | expr

?type: "bool"
     | "float"
     | "int"
     | "string"
     | "[" type "]"

?call: IDENT "(" (expr ("," expr)*)? ")"

?param: (param_item ("," param_item)*)?

?param_item: type IDENT

?def: "function" IDENT "(" param ")" body
    | "function" IDENT "(" param ")" "returns" type body

?body: "{" stmt* "}"

?expr: and_expr "or" expr
     | and_expr

?and_expr: not_expr "and" and_expr
         | not_expr

?not_expr: "not" not_expr 
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

?term: IDENT ("(" (expr ("," expr)*)? ")" | "[" expr "]")?
     | DOT call
     | FLOAT
     | NUM
     | STRING
     | TRUE
     | FALSE
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

// --- Strings ---
STRING: /"([^"\\]|\\.)*"/

// --- Whitespace ---
%import common.WS
%import common.INT  -> NUM
%ignore WS
"""

code = """
function myfunc() returns int {
    a = 2; 
    b = 1;
}
"""

from lark import Lark
from parsertransformer import MyTrans

def transformtree(tree):
    return MyTrans().transform(tree)

parser = Lark(grammar, parser="lalr", strict=True)

parsetree = parser.parse(code)
result = transformtree(parsetree)
print("Parse \n", parsetree.pretty())
print("AST \n", result.pretty())