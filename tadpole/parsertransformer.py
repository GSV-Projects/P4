from lark import Lark, Transformer, v_args, Tree, Token

class MyTrans(Transformer):

# Terminals for types

    def IDENT(self, c):
        return c
    
    def FLOAT(self, c):
        return c

    def BOOL(self, c):
        return c
    
    def STRING(self, c):
        return c
    
    def NA(self, c):
        return c
    
    def type_int(self, c):
        return c[0]

    def type_float(self, c):
        return c[0]

    def type_bool(self, c):
        return c[0]

    def type_string(self, c):
        return c[0]

    def type_array(self, c):
        return Tree("array_type", c)

    def type_table(self, c):
        return c[0]

    def param_item(self, c):
        return Tree("param_item", c)  # c[0] = type, c[1] = ident


# Statements

    def method_call(self, c):
        return Tree("dot", c)    
    
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
        c = self.fold(c)
        return Tree("geq", c)

    # Plus expressions
    def add(self, c):
        return Tree("add", c)
    
    def sub(self, c):
        return Tree("sub", c)

    # Mult expressions
    def mult(self, c):
        return Tree("mult", c)

    def divide(self, c):
        return Tree("div", c)

    def mod(self, c):
        return Tree("mod", c)
    
    # Misc expressions
    def exp_expr(self, c):
        return Tree("^", c)
    
    def unary_expr(self, c):
        return Tree("neg", [c[1]])

# Functions

    def func_def(self, c):
        return Tree("func_def", c)

    def func_def_ret(self, c):
        return Tree("func_def_ret", c)

    def while_stmt(self, c):
        return Tree("while", c)

    def if_stmt(self, c):
        return Tree("if", c)
    
    def else_stmt(self, c):
        return Tree("else", c)
    
    def param(self, c):
        return Tree("param", c)
    
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
    
    def array_assign(self, c):
        return Tree("assign_index", c)