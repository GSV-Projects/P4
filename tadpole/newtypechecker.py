from lark import Lark, Transformer, v_args, Tree, Token
from parser_lexer_lark import result


class Typechecker():
    def __init__(self):
        self.vtable = {}
        self.ftable = {}

    def read_token(self, token):
        if token.type == 'TYPE_INT' or token.type == 'INT':
            return int
        if token.type == 'TYPE_FLOAT' or token.type == 'FLOAT':
            return float
        if token.type == 'TYPE_STRING' or token.type == 'STRING':
            return str
        if token.type == 'TYPE_BOOL' or token.type == 'FALSE' or token.type == 'TRUE':
            return bool
        return 'unknown type shi'

    def build_ft(self, child, env):

        # signature indeholder en liste med elementer: tuple af parameter typer og return typen
        func_id, signature = self.get_fun(child, env)
        
        if func_id in self.ftable:
            raise Exception(f"Semantic Error: Definition '{func_id}' already exists")
        
        # Tilføj funktion til ftable
        self.ftable[func_id] = signature

    def build_vt(self, node, env):
        vtable = env.copy()
    

        # Tilføj parametre til vtable
        for child in node.children:
            vtable[child.children[1].data] = self.check(child.children[0],env)
        return vtable

    def get_fun(self, node, env):
        func_name = node.children[0].data
        paramsnode = node.children[1]
        if len(node.children) == 4:
            return_type = self.check(node.children[2], env)
        else:
            return_type = None

        params = []
        for x in paramsnode.children:
            params.append(self.check(x.children[0], env))


        # Return (id, (t1, ..., tn) -> t)
        return func_name, (tuple(params), return_type)

    # --- Check program ---
    def check_p(self, c):
        for child in c.children:
            if isinstance(child, Tree) and child.data == 'def':
                self.build_ft(child, self.vtable)
                self.check_f(child, self.vtable)

        for statement in c.children:
            # print(statement)
            self.check(statement, self.vtable)

        print(self.ftable)
        print(self.vtable)
        
    def check_f(self, node, env):
        paramsnode = node.children[1]
        if len(node.children) == 4:
            return_type = self.check(node.children[2], env)
            body = node.children[3]
        else:
            return_type = None
            body = node.children[2]
        
        vtable_local = self.build_vt(paramsnode, env)
        print("local", vtable_local)

        t = self.check(body, vtable_local)

        if (t == return_type) or (return_type == None):
            pass
        else:
            raise Exception("idfk error")

    def check(self, node, env):
        if isinstance(node, Token):
            return self.read_token(node)
        

        method_name = f'check_{node.data}'
        check_method = getattr(self, method_name, self.check_unknown)
        return check_method(node, env)

    def check_unknown(self, node, env):
        raise Exception(f"No handler for node type: '{node.data}'")
    
    # --- directory ---
    def check_add(self, node, env):  return self.check_additive(node, env)
    def check_sub(self, node, env):  return self.check_additive(node, env)
    def check_mod(self, node, env):  return self.check_additive(node, env)
    def check_div(self, node, env):  return self.check_div_mult(node, env)
    def check_mult(self, node, env): return self.check_div_mult(node, env)
    
    # --- check implements ---
    def check_assign(self, node ,env):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(right, env)
        self.vtable[left.data] = t1

    def check_additive(self, node, env):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env)
        t2 = self.check(right, env)

        if t1 in (int,) and t2 in (int,):
            return int
        elif t1 in (int, float) and t2 in (int, float):
            return float
        else:
            return (TypeError)

    def check_div_mult(self, node, env):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env)
        t2 = self.check(right, env)

        if t1 in (int, float) and t2 in (int, float):
            return float
        else:
            return (TypeError)
        
    def check_comparison(self, node, env):
        pass

    def check_def(self, node, env):
        pass

    def check_body(self, node, env):
        return node

Typechecker().check_p(result)

