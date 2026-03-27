grammar = r"""
start: program

program: (stmt | def)*

stmt: IDENT stmt_suffix ";"
    | WHILE "(" expr ")" DO "{" stmt* "}"
    | IF "(" expr ")" THEN "{" stmt* "}" (ELSE "{" stmt* "}")?
    | STOP ";"
    | SKIP ";"
    | RETURN expr ";"

stmt_suffix: DOT call
           | ASSIGN rvalue
           | "(" (expr ("," expr)*)? ")"

rvalue: "[" (expr ("," expr)*)? "]"
      | expr

?type: "bool"
    | "float"
    | "int"
    | "string"
    | "[" type "]"

call: IDENT "(" (expr ("," expr)*)? ")"

param: (type IDENT ("," param_item)*)?
param_item: type IDENT

def: FUNCTION IDENT "(" param ")" ret

ret: RETURNS type "{" stmt* "}"
   | "{" stmt* "}"

?expr: and_expr (OR and_expr)*

?and_expr: not_expr (AND not_expr)*

?not_expr: (NOT)* eq_expr

?eq_expr: plus_expr ((EQUAL | INEQUAL | LESS | LESSEQ | GREAT | GREATEQ) plus_expr)?

?plus_expr: mult_expr ((ADD | SUB) mult_expr)*

?mult_expr: exp_expr ((MULT | DIVIDE | MOD) exp_expr)*

?exp_expr: unary_expr (EXPO unary_expr)*

?unary_expr: (SUB)* term

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
SUB: "-"
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
%import common.INT -> NUM
%ignore WS
"""

code = """
x = 5 + 2 - 1;
"""


import sys 
from typing import List, Optional, Any 
from dataclasses import dataclass 
from lark import Lark, ast_utils, Transformer, v_args 
from lark.tree import Meta 

this_module = sys.modules[__name__]

class ToAst(Transformer):
    #
    # Terminals
    #
    def IDENT(self, t):
        return str(t)

    def STRING(self, s):
        return Literal(value=s[1:-1])

    def NUM(self, n):
        return Literal(value=int(n))

    def FLOAT(self, n):
        return Literal(value=float(n))

    def TRUE(self, _):
        return Literal(value=True)

    def FALSE(self, _):
        return Literal(value=False)

    def NA(self, _):
        return Literal(value=None)

    def start(self, items):
        return items[0]

    #
    # Program
    #
    def program(self, items):
        return Program(items)

    #
    # Statements
    #
    def stmt(self, items):
        # IDENT stmt_suffix
        if len(items) == 2 and isinstance(items[0], str):
            name = items[0]
            suffix = items[1]

            if suffix[0] == "assign":
                return Assign(name, suffix[1])

            if suffix[0] == "call":
                return CallStmt(name, suffix[1])

            if suffix[0] == "method":
                return MethodCall(name, suffix[1], suffix[2])

        # already transformed (if, while, return, etc.)
        if len(items) == 1:
            return items[0]

        return items

    def stmt_suffix(self, items):
        # DOT call
        if len(items) == 2 and items[0].type == "DOT":
            call = items[1]
            return ("method", call.name, call.args)

        # ASSIGN rvalue
        if len(items) == 2 and items[0].type == "ASSIGN":
            return ("assign", items[1])

        # function call ( ... )
        return ("call", items)

    #
    # Control flow
    #
    def while_(self, items):
        cond = items[0]
        body = CodeBlock(items[1:])
        return While(cond, body)

    def if_(self, items):
        cond = items[0]
        then_block = CodeBlock(items[1])
        else_block = CodeBlock(items[2]) if len(items) > 2 else None
        return If(cond, then_block, else_block)

    def return_(self, items):
        return Return(items[0])

    def stop(self, _):
        return Stop()

    def skip(self, _):
        return Skip()

    #
    # Function definition
    #
    def def_(self, items):
        name = items[0]
        params = items[1]
        ret_type, body = items[2]
        return FunctionDef(name, params, ret_type, body)

    def ret(self, items):
        if len(items) == 2:
            return (items[0], CodeBlock(items[1]))
        return (None, CodeBlock(items[0]))

    #
    # Calls
    #
    def call(self, items):
        name = items[0]
        args = items[1:]
        return CallExpr(name, args)

    #
    # rvalue
    #
    def rvalue(self, items):
        if len(items) == 1:
            return items[0]
        return ListLiteral(items)

    #
    # Expressions
    #
    def eq_expr(self, items):
        return self._fold_binop(items)

    def plus_expr(self, items):
        return self._fold_binop(items)

    def mult_expr(self, items):
        return self._fold_binop(items)

    def exp_expr(self, items):
        return self._fold_binop(items)

    def and_expr(self, items):
        return self._fold_binop(items)

    def expr(self, items):
        return self._fold_binop(items)

    def unary_expr(self, items):
        # multiple SUB tokens → unary minus chain
        if len(items) == 1:
            return items[0]

        value = items[-1]
        for _ in items[:-1]:
            value = UnaryOp("-", value)

        return value

    def _fold_binop(self, items):
        if len(items) == 1:
            return items[0]

        left = items[0]

        i = 1
        while i < len(items):
            op = items[i].value   # IMPORTANT FIX
            right = items[i + 1]
            left = BinOp(left, op, right)
            i += 2

        return left

parser = Lark(grammar)

transformer = ast_utils.create_transformer(this_module, ToAst())

def parse(text):
    tree = (parser.parse(text))
    return transformer.transform(tree)

if __name__ == '__main__':
              print(parser.parse(code).pretty()) # parse træ
              print(parse(code)) # AST mby?


# Gammel kode
# from lark.tree import pydot__tree_to_png
# tree = parser.parse(code)
# pydot__tree_to_png(tree, "tree.png")