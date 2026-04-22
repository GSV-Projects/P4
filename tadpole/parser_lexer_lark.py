# "if" "(" expr ")" "then" "{" stmt* "}" ("else" "{" stmt* "}")?    -> if_stmt      gammel if statement
grammar = r"""
?start: program

program: (stmt | def)*

?stmt: lvalue "=" rvalue ";"                     -> assign
     | IDENT "(" (expr ("," expr)*)? ")" ";"     -> func_call
     | "while" "(" expr ")" "do" "{" stmt* "}"   -> while_stmt
     | "if" "(" expr ")" "then" "{" stmt* "}" (ifelse)?   -> if_stmt
     | STOP ";"                                  -> stop
     | SKIP ";"                                  -> skip
     | "return" expr ";"                         -> return_stmt

?lvalue: IDENT
       | IDENT "[" expr "]"                       -> array_assign

?ifelse:  "else" "{" stmt* "}"                     -> else

?rvalue: "[" (expr ("," expr)*)? "]"              -> array
       | IDENT "." call ("." call)*               -> method_call
       | "{" column* "}"                          -> table
       | expr

?column: ( IDENT ":" "[" column_content "]" ";" )      -> column

?column_content: (expr ("," expr)*)?                   -> array

call: IDENT "(" (expr ("," expr)*)? ")"

?def: "function" IDENT "(" param ")" body                   -> func_def
    | "function" IDENT "(" param ")" "returns" type body    -> func_def_ret

?body: "{" stmt* "}"

?type: TYPE_BOOL                                -> type_bool
     | TYPE_FLOAT                               -> type_float
     | TYPE_INT                                 -> type_int
     | TYPE_STRING                              -> type_string
     | "[" type "]"                             -> type_array
     | TYPE_TBL                                 -> type_table

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
     | IDENT "[" expr "]"                  -> array_indexing
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
TYPE_TBL: "tbl"

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

mytab = {
     col1: [1,2,3];
};

function h(int b) returns int{
return 3;
}

a = 1;

c = a.test3().test2();

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