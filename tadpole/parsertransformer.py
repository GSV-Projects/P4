from lark import Transformer, v_args, Tree, Token

# Class for folding unnecessary nodes in the AST,
#   for each function it returns either the left node,
#   or the current tree with a label.
class MyTrans(Transformer):

# Terminals for types
    # Methods for types simply return the left node of the AST and are not presented in the AST
    def type_int(self, c):
        return c[0]

    def type_float(self, c):
        return c[0]

    def type_bool(self, c):
        return c[0]

    def type_string(self, c):
        return c[0]

    # Methods for types return the left node of the AST and are presented in the AST,
    #   with a label.
    def type_column(self, c):
        return Tree("clmn", c)
    
    def type_array(self, c):
        return Tree("array_type", c)

    def type_table(self, c):
        return c[0]

    def param_item(self, c):
        return Tree("param_item", c)

# Statements
    # Print nodes in the AST for dot functions call, assigments and function calls.
    def assign(self, c):
        return Tree("assign", c)

    def array_assign(self, c):
        return Tree("assign_index", c)

    def while_stmt(self, c):
        return Tree("while", c)

    def if_stmt(self, c):
        return Tree("if", c)

    def else_stmt(self, c):
        return Tree("else", c)

    def return_stmt(self, c):
        return Tree("return", c)
    
# Expressions
# For each expression a node is needed, to match the operator to an operation.
    # Logical expressions- returns label and tree.
    def expr(self, c):
        return Tree("or", c)
    
    def and_expr(self, c):
        return Tree("and", c)
    
    def not_expr(self, c):
        return Tree("not", [c[1]])
    
    # Equal expressions - returns label and tree.
    def equal(self, c):
        return Tree("equal", c)
    
    def not_equal(self, c):
        return Tree("neq", c)
    
    def less(self, c):
        return Tree("less", c)

    def less_eq(self, c):
        return Tree("leq", c)

    def greater(self, c):
        return Tree("greater", c)

    def greater_eq(self, c):
        return Tree("geq", c)

    # Plus expressions - returns label and tree.
    def add(self, c):
        return Tree("add", c)
    
    def sub(self, c):
        return Tree("sub", c)

    # Mult expressions - returns label and tree.
    def mult(self, c):
        return Tree("mult", c)

    def divide(self, c):
        return Tree("div", c)

    def mod(self, c):
        return Tree("mod", c)
    
    # Misc expressions - returns label and tree.
    def exp_expr(self, c):
        return Tree("exp", c)
    
    def unary_expr(self, c):
        return Tree("neg", [c[1]])

# Functions, array/column and tables.
    # Function methods - returns label and tree.
    def dot_call(self, c):
        return Tree("dot", c)

    def func_call(self, c):
        return Tree("call", c)

    def func_def(self, c):
        return Tree("func_def", c)

    def func_def_ret(self, c):
        return Tree("func_def_ret", c)

    def body(self, c):
        return Tree("body", c)

    def param(self, c):
        return Tree("param", c)

    # Table, columns and arrays - returns label and tree.
    def array(self, c):
        return Tree("array", c)
    
    def array_indexing(self, c):
        return Tree("index", c)
    
    def table(self, c):
        return Tree("table", c)
    
    def column(self, c):
        return Tree("column", c)