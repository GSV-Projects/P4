from lark import Lark, Transformer, v_args, Tree, Token
from parser_lexer_lark import result

class Interpreter():
    def __init__(self):
        self.vtable = {}
        self.ftable = {}


    # --- Run program ---
    def Eval_P(self, p):
    
        for statement in p.children:
            self.SEval(statement, self.vtable)

        print("ftable:", self.ftable)
        print("global vtable:", self.vtable)

    def SEval(statement, env):
        if statement == "assign":
            SEval_assign(statement, env)

        
    def SEval_assign(self, node, env):
        node.Eval(self, node)


    def Eval(self, tree, env):
        # --- Tokens (leaf nodes) ---
        if isinstance(tree, Token):
            if tree.type == "INT":
                return int(tree)
            elif tree.type == "FLOAT":
                return float(tree)
            elif tree.type == "STRING":
                return str(tree).strip('"')
            elif tree.type == "TRUE":
                return True
            elif tree.type == "FALSE":
                return False
            elif tree.type == "NA":
                return None
            elif tree.type == "IDENT":
                return env[str(tree)]

        # --- Arithmetic ---
        elif tree.data == "add":
            return self.Eval(tree.children[0]) + self.Eval(tree.children[1])
        elif tree.data == "sub":
            return self.Eval(tree.children[0]) - self.Eval(tree.children[1])
        elif tree.data == "mult":
            return self.Eval(tree.children[0]) * self.Eval(tree.children[1])
        elif tree.data == "divide":
            return self.Eval(tree.children[0]) / self.Eval(tree.children[1])
        elif tree.data == "mod":
            return self.Eval(tree.children[0]) % self.Eval(tree.children[1])
        
        # --- Boolean expressions ---
        elif tree.data == "equal":
            return self.Eval(tree.children[0]) == self.Eval(tree.children[1])
        elif tree.data == "not_equal":
            return self.Eval(tree.children[0]) != self.Eval(tree.children[1])
        elif tree.data == "less":
            return self.Eval(tree.children[0]) < self.Eval(tree.children[1])
        elif tree.data == "less_eq":
            return self.Eval(tree.children[0]) <= self.Eval(tree.children[1])
        elif tree.data == "greater":
            return self.Eval(tree.children[0]) > self.Eval(tree.children[1])
        elif tree.data == "greater_eq":
            return self.Eval(tree.children[0]) >= self.Eval(tree.children[1])


    def check(self, node, env):
        #print("node", node)
        if isinstance(node, Token):
            return self.read_token(node, env)
        
        method_name = f'check_{node.data}'
        Eval_method = getattr(self, method_name, self.check_unknown)
        return EVal_method(node, env)

    def read_token(self, token, env):
        if token.type == 'IDENT':
            return self.check_IDENT(token, env)
        if token.type == 'TYPE_INT' or token.type == 'INT':
            return int
        if token.type == 'TYPE_FLOAT' or token.type == 'FLOAT':
            return float
        if token.type == 'TYPE_STRING' or token.type == 'STRING':
            return str
        if token.type == 'TYPE_BOOL' or token.type == 'FALSE' or token.type == 'TRUE':
            return bool
        if token.type == 'TYPE_TBL' or token.type == 'tbl':
            return 'tbl'
        return 'unknown type shi'

Interpreter().Eval_P(result)