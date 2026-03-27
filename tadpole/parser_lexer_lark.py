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

?plus_expr: mult_expr ((ADD | SUB) mult_expr)*

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
x = 5 + 2 - 1;
"""

import sys
from typing import List, Optional, Any
from dataclasses import dataclass
from lark import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta

this_module = sys.modules[__name__]

#
#   Base AST
#
class _Ast(ast_utils.Ast):
    pass


class _Statement(_Ast):
    pass


#
#   Program structure
#
@dataclass
class Program(_Ast, ast_utils.AsList):
    items: List[_Ast]   # stmt | def


@dataclass
class CodeBlock(_Ast, ast_utils.AsList):
    statements: List[_Statement]


#
#   Statements
#
@dataclass
class Assign(_Statement):
    name: str
    value: _Ast


@dataclass
class CallStmt(_Statement):
    name: str
    args: List[_Ast]


@dataclass
class MethodCall(_Statement):
    obj: str
    name: str
    args: List[_Ast]


@dataclass
class While(_Statement):
    cond: _Ast
    body: CodeBlock


@dataclass
class If(_Statement):
    cond: _Ast
    then: CodeBlock
    otherwise: Optional[CodeBlock]


@dataclass
class Stop(_Statement):
    pass


@dataclass
class Skip(_Statement):
    pass


@dataclass
class Return(_Statement):
    value: _Ast


#
#   Function definitions
#
@dataclass
class FunctionDef(_Ast):
    name: str
    params: List[Any]
    return_type: Optional[Any]
    body: CodeBlock


#
#   Expressions (generic but structured)
#
@dataclass
class Name(_Ast):
    name: str


@dataclass
class Literal(_Ast):
    value: Any


@dataclass
class CallExpr(_Ast):
    name: str
    args: List[_Ast]


@dataclass
class Index(_Ast):
    value: _Ast
    index: _Ast


@dataclass
class BinOp(_Ast):
    left: _Ast
    op: str
    right: _Ast


@dataclass
class UnaryOp(_Ast):
    op: str
    value: _Ast


@dataclass
class ListLiteral(_Ast):
    items: List[_Ast]

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

    def BOOL(self, b):
        return Literal(value=(b == "true"))

    def NA(self, _):
        return Literal(value=None)

    def start(self, items):
        return items

    #
    # Program
    #
    def program(self, items):
        return Program(items)

    #
    # Statements
    #
    def stmt(self, items):
        # IDENT stmt_suffix case
        if len(items) == 2 and isinstance(items[0], str):
            name = items[0]
            suffix = items[1]

            if isinstance(suffix, tuple) and suffix[0] == "assign":
                return Assign(name, suffix[1])

            if isinstance(suffix, tuple) and suffix[0] == "call":
                return CallStmt(name, suffix[1])

            if isinstance(suffix, tuple) and suffix[0] == "method":
                return MethodCall(name, suffix[1], suffix[2])

        # everything else → already transformed
        if len(items) == 1:
            return items[0]

        return items

    def stmt_suffix(self, items):
        # "=" rvalue
        if len(items) == 2:
            return ("assign", items[1])

        # "." call
        if isinstance(items[0], tuple) and items[0][0] == "call":
            return ("method", items[0][1], items[0][2])

        # "(" args ")"
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
        ret = items[2]
        return FunctionDef(name, params, ret[0], ret[1])

    def ret(self, items):
        if len(items) == 2:
            return (items[0], CodeBlock(items[1]))
        return (None, CodeBlock(items[0]))

    #
    # Expressions (generic folding)
    #
    def eq_expr(self, items):
        if len(items) == 1:
            return items[0]
        return BinOp(items[0], "eq", items[1])

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

    def _fold_binop(self, items):
        if len(items) == 1:
            return items[0]

        left = items[0]

        i = 1
        while i < len(items):
            op = items[i]

            # safety check
            if i + 1 >= len(items):
                break

            right = items[i + 1]
            left = BinOp(left, str(op), right)

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