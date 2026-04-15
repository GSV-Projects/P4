from lark import Lark, Transformer, v_args, Tree, Token

class MyTrans(Transformer):

    # Terminals for types
    def NUM(self, c):
        return Tree(str(c.value), [])

    def IDENT(self, c):
        return c
    
    def FLOAT(self, c):
        return c
        

    def BOOL(self, c):
        return Tree(str(c.value), [])
    
    def STRING(self, c):
        return c
    
    def NA(self, c):
        return Tree(str(c.value), [])

# Statements

    def method_call(self, c):
        return Tree(".", c)    
    
    def assign(self, c):
        return Tree("assign", c)
    
    def func_call(self, c):
        return Tree("call", c)
    
# Expressions

    # Logical expressions
    def expr(self, c):
        return Tree("or", c)
    
    def and_expr(self, c):
        return Tree("and", c)
    
    def not_expr(self, c):
        return Tree("not", [c[1]])
    
    # Equal expressions
    def equal(self, c):
        return Tree("==", c)
    
    def not_equal(self, c):
        return Tree("/=", c)
    
    def less(self, c):
        return Tree("<", c)

    def less_eq(self, c):
        return Tree("<=", c)

    def greater(self, c):
        return Tree(">", c)

    def greater_eq(self, c):
        c = self.fold(c)
        return Tree(">=", c)

    # Plus expressions
    def add(self, c):
        return Tree("add", c)
    
    def sub(self, c):
        return Tree("-", c)

    # Mult expressions
    def mult(self, c):
        return Tree("mult", c)

    def divide(self, c):
        return Tree("divide", c)

    def mod(self, c):
        return Tree("mod", c)
    
    # Misc expressions
    def exp_expr(self, c):
        return Tree("^", c)
    
    def unary_expr(self, c):
        return Tree("-", [c[1]])

# Functions

    def while_stmt(self, c):
        return Tree("while", c)

    def if_stmt(self, c):
        return Tree("if", c)
    
    def param(self, c):
        return Tree("params", c)
    
    def array(self, c):
        return Tree("array", c)
    
    def return_stmt(self, c):
        return Tree("return", c)

    def body(self, c):
        return Tree("body", c)
    
    def array_indexing(self, c):
        return Tree("index", c)
    
    def table(self, c):
        return Tree("table", c)
    
    def column(self, c):
        return Tree("column", c)