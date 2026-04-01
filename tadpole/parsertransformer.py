from lark import Lark, Transformer, v_args, Tree


class MyTrans(Transformer):
    # Terminals for types
    def NUMBER(self, children):
        return int(children.value)

    def IDENT(self, children):
        return str(children.value)
    
    def FLOAT(self, children):
        return float(children.value)

    def BOOL(self, children):
        return bool(children.value) 
    
    def STRING(self, children):
        return str(children.value)
    
    def NA(self, children):
        return str(children.value)
    
    # Starting node needed to create the tree
    def start(self, c):
        return c[0]
    
    def program(self, children):
        return children[0]
    
    def method_call(self, c):
        return Tree(".", c)    

    def assign(self, c):
        return Tree("=", c)
    
    def call(self, c):
        return Tree("call", c)
    
    def rvalue(self, c):
        return c[0]
    
    def expr(self, c):
        if (len(c) == 1):
            return c[0]
        return Tree("or", c)
    
    def and_expr(self, c):
        if (len(c)==1):
            return c[0]
        return Tree("and", c)
    
    def not_expr(self, c):
        if (len(c)==1):
            return c[0]
        return Tree("not", c)

    # Equal expressions
    def eq_expr(self, c):
        return c[0]
    
    # Additive expressions
    def additive_expr(self, c):
        return self.fold_left(c)
    
    # Multiplicative expressions
    def multiplicative_expr(self, c):
        return self.fold_left(c)

    # Exponential expression
    def expo_expr(self, c):
        if (len(c)==1):
            return c[0]
        return Tree("^", c)
    
    def unary_expr(self, c):
        return c[0]
    
    def term(self, c):
        return c[0]

    def fold_left(self, items):
        if len(items) == 1:
            return items[0]

        left = items[0]
        i = 1
        while i < len(items):
            op = items[i]
            right = items[i+1]
            left = Tree(op.value, [left, right])
            i += 2

        return left