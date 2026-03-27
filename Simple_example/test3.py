from lark import Lark, Transformer, v_args

class MyTrans(Transformer):
    def NUMBER(self, n):
        return int(n.value)

    def IDENT(self, i):
        return str(i.value)

    def add(self, children):
        left, right = children
        return {"op": "+", "left": left, "right": right}


    def assign(self, children):
        name, value = children
        return {"op": "=", "left": name, "right": value}

    def start(self, children):
        return children
    

   