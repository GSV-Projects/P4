from lark import Lark, Transformer, v_args, Tree

class MyTrans(Transformer):
    def start(self, children):
        return Tree("start", children)