from lark import Lark, Transformer, v_args, Tree

class MyTranss(Transformer):
    def NUMBER(self, n):
        return int(n.value)

    def IDENT(self, i):
        return str(i.value)

    def add(self, children):
        print("child", children)
        left, right = children
        return Tree("+", children)

    def subtract(self, children):
        left, right = children
        return Tree("-", children)
    
    def assign(self, children):
        name, value = children
        return Tree("=", children)
    
    def term(self, children):
        return children[0]

    def expr(self, children):
        return children[0]

    def stmt(self, children):
        return children[0]


    def start(self, children):
        return Tree("start", children)
    

   