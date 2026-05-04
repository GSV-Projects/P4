# "if" "(" expr ")" "then" "{" stmt* "}" ("else" "{" stmt* "}")?    -> if_stmt      gammel if statement
grammar = r"""
?start: program

program: (stmt | def)*

?stmt: IDENT "=" rvalue ";"                      -> assign
     | IDENT "[" expr "]" "=" rvalue ";"         -> array_assign
     | call ";"                                  
     | "while" "(" expr ")" "do" "{" stmt* "}"   -> while_stmt
     | "if" "(" expr ")" ifthen (ifelse)?   -> if_stmt
     | STOP ";"                                  -> stop
     | "return" expr ";"                         -> return_stmt

?ifthen:  "then" "{" stmt* "}"                     -> then
?ifelse:  "else" "{" stmt* "}"                     -> else

?rvalue: "[" (expr ("," expr)*)? "]"              -> array
       | IDENT "." call ("." call)*               -> method_call
       | table
       | expr

?table: "{" column* "}" -> table
       
?column: ( COLUMN ":" "[" column_content "]" ";" )      -> column

?column_content: (expr ("," expr)*)?                   -> array

?call: IDENT "(" (expr ("," expr)*)? ")"               -> func_call

?def: "function" IDENT "(" param ")" body                   -> func_def
    | "function" IDENT "(" param ")" "returns" type body    -> func_def_ret

?body: "{" stmt* "}"

?type: TYPE_BOOL                                -> type_bool
     | TYPE_FLOAT                               -> type_float
     | TYPE_INT                                 -> type_int
     | TYPE_STRING                              -> type_string
     | TYPE_TABLE                               -> type_table
     | "clmn" "[" type "]"                      -> type_column
     | "[" type "]"                             -> type_array
     | "clmn" "[" type "]"                      -> type_column

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

?term: call                                
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
TYPE_TABLE: "tbl"

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
COLUMN: /[A-Za-z_][A-Za-z0-9_]*/

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
col1 : ["hej", "lol", "å"];
col2 : [3, 4, 5, 5, 6, 2];
col3 : [1.1, 2.2, 3.3];
};

name = "col4";
arr = [1,2,3,4];

newtab = mytab.append(name, arr);

"""

from lark import Lark
from parsertransformer import MyTrans
from interpreter import Interpreter
from type_checker import Typechecker

def transformtree(tree):
    return MyTrans().transform(tree)

parser = Lark(grammar, parser="lalr", strict=True)

parsetree = parser.parse(code)
result = transformtree(parsetree)

print("Parse \n", parsetree.pretty())
print("AST \n", result.pretty())

#Typechecker().check_p(result)
fortolker = Interpreter()
fortolker.Eval_P(result)