from lark import Lark, Transformer, v_args, Tree, Token
from parser_lexer_lark import result

# Test comment


class Typechecker():
    def __init__(self):
        self.vtable = {}
        self.ftable = {}

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
        return 'unknown type shi'

    # --- Check program ---
    def check_p(self, c):
        for child in c.children:
            if isinstance(child, Tree) and child.data == 'def':
                self.build_ft(child, self.vtable)

        for statement in c.children:
            print("yes", statement)
            self.check(statement, self.vtable)

        print("ftable:", self.ftable)
        print("global vtable:", self.vtable)

    """ 
    Checks a given node, and determines how to continue making checks from that. 

    Parameters: 
        self
        node
        env

    Returns: 
        If the given node is a leaf, return said token.
        Otherwise, a string literal containing 'check_' followed by the type is run and returned.
    """
    def check(self, node, env):
        print("node", node)
        if isinstance(node, Token):
            return self.read_token(node, env)
        
        method_name = f'check_{node.data}'
        check_method = getattr(self, method_name, self.check_unknown)
        return check_method(node, env)

    # check method to fall back on, if the given node is unknown
    def check_unknown(self, node, env):
        raise Exception(f"No handler for node type: '{node.data}'")

    # --- directory ---
    def check_add(self, node, env):     return self.check_additive(node, env)
    def check_sub(self, node, env):     return self.check_additive(node, env)
    def check_mod(self, node, env):     return self.check_additive(node, env)
    def check_mult(self, node, env):    return self.check_additive(node, env)

    def check_less(self, node, env):    return self.check_comparison(node, env)
    def check_greater(self, node, env): return self.check_comparison(node, env)
    def check_leq(self, node, env):     return self.check_comparison(node, env)
    def check_geq(self, node, env):     return self.check_comparison(node, env)
    def check_equal(self, node, env):   return self.check_comparison(node, env)
    def check_neq(self, node, env):     return self.check_comparison(node, env)

    def check_or(self, node, env):      return self.check_logical(node, env)
    def check_and(self, node, env):     return self.check_logical(node, env)

    # --- Table / structure builders ---
    def build_ft(self, child, env):
        func_id, signature = self.get_fun(child, env)
        
        if func_id in self.ftable:
            raise Exception(f"Semantic Error: Definition '{func_id}' already exists")
        
        self.ftable[func_id] = signature

    def build_vt(self, node, env):
        vtable = env.copy()
    
        for child in node.children:
            vtable[child.children[1].value] = self.check(child.children[0], env)
        return vtable

    def get_fun(self, node, env):
        func_name = node.children[0].value
        paramsnode = node.children[1]
        if len(node.children) == 4:
            return_type = self.check(node.children[2], env)
        else:
            return_type = None

        params = []
        for x in paramsnode.children:
            params.append(self.check(x.children[0], env))

        return func_name, (tuple(params), return_type)

    # --- check implements ---
    def check_IDENT(self, node, env):
        if (node.value in env):
            return env[node.value]

    def check_assign(self, node, env):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(right, env)

        env[left.value] = t1

    def check_def(self, node, env):
        # TODO: Check function body and return type matches with return when we declare the function
        self.check_f(node, env)

    def check_f(self, node, env):
        paramsnode = node.children[1]
        if len(node.children) == 4:
            return_type = self.check(node.children[2], env)
            body = node.children[3]
        else:
            return_type = None
            body = node.children[2]
        
        vtable_local = self.build_vt(paramsnode, env)
        print("local vtable", vtable_local)

        t = self.check(body, vtable_local)

        if (t == return_type) or (return_type == None):
            pass
        else:
            raise Exception("idfk error")

    def check_body(self, node, env):
        check_same_type = []
        for child in node.children:
            if (child.data == "return"):
                check_same_type.append(self.check(child, env))
            else:
                self.check(child, env)

            if (all(x == check_same_type[0] for x in check_same_type)):
                return check_same_type[0]

    def check_return(self, node, env):
        print("hejnode", node)
        print("hejnode2", node.children[0])
        print("hej", node.children[0])

        # TODO: Check om inde i funktion
        # TODO: hvis nej raise exception

        return self.check(node.children[0], env)

    # --- Arithmetic ---
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

    def check_div(self, node, env):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env)
        t2 = self.check(right, env)

        if t1 in (int, float) and t2 in (int, float):
            return float
        else:
            raise Exception(f'{node.children[0]} or {node.children[1]} is not an int or float')

    # --- Comparisons & logic ---
    def check_comparison(self, node, env):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env)
        t2 = self.check(right, env)

        if (t1 == int and t2 == int) or (t1 == float and t2 == float):
            return bool
        else: 
            raise Exception(f'different types shi in comparison')

    def check_logical(self, node, env):
        pass

    # --- Arrays & tables ---
    def check_array(self, node, env):
        if len(node.children) == 0:
            raise Exception("No type for an empty array")

        type_first_elem = self.check(node.children[0], env)
        print("array type: ", type_first_elem)

        if (all(self.check(x, env) == type_first_elem for x in node.children)):
            return [type_first_elem]
        else: 
            raise Exception("Not all elems of array are the same")
        
    def check_array_type(self, node, env):
        array_type = self.check(node.children[0], env)
        return [array_type]

    def check_index(self, node, env):
        type_arr = self.check(node.children[0], env)
        type_idx = self.check(node.children[1], env)

        if type_idx in int:
            return type_arr
        else: 
            raise Exception(f'Did not parse an integer for array indexing')
    
    def check_column(self, node, env):
        col_name = node.children[0]
        col_arr = node.children[1]
        
        type_col_arr = self.check(col_arr, env)

        env[col_name] = type_col_arr

    def check_table(self, node, env):
        print("table name", node.data)

        for child in node.children:
            self.check(child, env)

        return node.data


Typechecker().check_p(result)