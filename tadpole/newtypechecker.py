from lark import Lark, Transformer, v_args, Tree, Token
from parser_lexer_lark import result

# Test comment

class Typechecker():
    def __init__(self):
        self.vtable = {}
        self.ftable = {}
        self.RL = {
            "R" : None,
            "L" : False
        }

    def read_token(self, token, env):
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
         # --- build ftable ---
        self.build_ft(c, self.vtable, self.RL)

        for statement in c.children:
            self.check(statement, self.vtable, self.RL)

        print("ftable:", self.ftable)
        print("global vtable:", self.vtable)

    def build_ft(self, c, env, RL):
        for child in c.children:
            if isinstance(child, Tree) and child.data == 'def':
                # TODO Tilføj child.data for returns og uden

                # signature indeholder en liste med elementer: tuple af parameter typer og return typen
                func_id, signature = self.get_fun(child, env, RL)
                
                if func_id in self.ftable:
                    raise Exception(f"Semantic Error: Definition '{func_id}' already exists")
                
                # Functions are added to the global ftable.
                self.ftable[func_id] = signature

    def build_vt(self, node, env, RL):
        vtable = env.copy()
    
        # Parameters are added to the local vtable.
        for child in node.children:
            vtable[child.children[1].value] = self.check(child.children[0],env, RL)
        return vtable

    def get_fun(self, node, env, RL):
        func_name = node.children[0].value
        paramsnode = node.children[1]
        if len(node.children) == 4:
            return_type = self.check(node.children[2], env, RL)
        else:
            return_type = None

        params = []
        for x in paramsnode.children:
            params.append(self.check(x.children[0], env, RL))

        # Returns (id, (t1, ..., tn) -> t)
        return func_name, (tuple(params), return_type)
        
    def check_f(self, node, env, RL):
        paramsnode = node.children[1]
        if len(node.children) == 4:
            return_type = self.check(node.children[2], env, RL)
            RL["R"] = return_type
            body = node.children[3]
        else:
            return_type = None
            body = node.children[2]
        
        vtable_local = self.build_vt(paramsnode, env, RL)
        print("local vtable", vtable_local)

        t = self.check(body, vtable_local, RL)

        if (t == return_type) or (return_type == None):
            pass
        else:
            raise Exception("idfk error")

    
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
    def check(self, node, env, RL):
        print("node", node)
        if isinstance(node, Token):
            return self.read_token(node, env)
        
        method_name = f'check_{node.data}'
        check_method = getattr(self, method_name, self.check_unknown)
        return check_method(node, env, RL)

    
    # check method to fall back on, if the given node is unknown
    def check_unknown(self, node, env):
        raise Exception(f"No handler for node type: '{node.data}'")

    # --- directory ---
    def check_add(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_sub(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_mod(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_mult(self, node, env, RL):    return self.check_additive(node, env, RL)

    def check_div(self, node, env, RL):     return self.check_div_mult(node, env, RL)

    def check_less(self, node, env, RL):    return self.check_comparison(node, env, RL)
    def check_greater(self, node, env, RL): return self.check_comparison(node, env, RL)
    def check_leq(self, node, env, RL):     return self.check_comparison(node, env, RL)
    def check_geq(self, node, env, RL):     return self.check_comparison(node, env, RL)
    def check_equal(self, node, env, RL):   return self.check_comparison(node, env, RL)
    def check_neq(self, node, env, RL):     return self.check_comparison(node, env, RL)

    def check_or(self, node, env, RL):      return self.check_logical(node, env, RL)
    def check_and(self, node, env, RL):     return self.check_logical(node, env, RL)
    
    # --- check implements ---
    def check_IDENT(self, node, env):
        if (node.value not in env):
            raise Exception(f'{node.value} not defined')
        else: 
            return env[node.value]

    def check_assign(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(right, env, RL)
        print("left", left.value)
        print("t1",  t1)

        if (left.value not in env):
            env[left.value] = t1
        
        elif (env == self.vtable):
            if (env[left.value] != t1):
                raise Exception(f'error: {left.value} is of type {env[left.value]} and cannot be declared as type {t1}')
        else:
            env[left.value] = t1

        ## TODO Hvis env = self.vtable -> check om env(left.value) er tom -> hvis ikke -> chekc om samme type -> hvis ikke -> error
        

    def check_additive(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        if t1 in (int,) and t2 in (int,):
            return int
        elif t1 in (int, float) and t2 in (int, float):
            return float
        else:
            return (TypeError)

    def check_div_mult(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        if t1 in (int, float) and t2 in (int, float):
            return float
        else:
            raise Exception(f'{node.children[0]} or {node.children[1]} is not an int or float')
        
    def check_comparison(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        # TODO er intereseret i, om left og right bare er typern
        #print("comparison left, right:", left, right)

        if (t1 == int and t2 == int) or (t1 == float and t2 == float):
            return bool
        else: 
            raise Exception(f'different types shi in comparison')

    def check_logical(self, node, env, RL):
        pass

    def check_def(self, node, env, RL):
        # TODO: Check function body and return type matches with return when we declare the function
        self.check_f(node, env, RL)

    def check_body(self, node, env, RL):
        check_same_type = []
        for child in node.children:
            if (child.data == "return"):
                check_same_type.append(self.check(child, env, RL))
            else:
                self.check(child, env, RL)

        if (all(x == check_same_type[0] for x in check_same_type)):
            return check_same_type[0]
        
    
    def check_return(self, node, env, RL):

        t1 = self.check(node.children[0], env, RL)

        if (t1 != RL["R"]):
            raise Exception("Some return error")

        return t1
    
    def check_array(self, node, env, RL):
        # check if the array is empty
        if len(node.children) == 0:
            raise Exception("No type for an empty array")

        type_first_elem = self.check(node.children[0], env, RL)
        print("array type: ", type_first_elem)

        if (all(self.check(x, env, RL) == type_first_elem for x in node.children)):
            return [type_first_elem] # return as ARRAY of type T - [T], NOT simply T
        else: 
            raise Exception("Not all elems of array are the same")
        
    def check_array_type(self, node, env, RL):
        # Check function for [type] used in parameters and returns
        array_type = self.check(node.children[0], env, RL)
        return [array_type]
        
    # if x is an array of type T, and e is an Int, then x[e] has type T
    def check_index(self, node, env, RL):
        type_arr = self.check(node.children[0], env, RL) # find the type for the array
        type_idx = self.check(node.children[1], env, RL) # find the type for the indexing nr

        if type_idx in int:
            return type_arr
        else: 
            raise Exception(f'Did not parse an integer for array indexing')
    
    # if an array [e] has type [T], and all elements are are of type T, then column c is of type T.
    def check_column(self, node, env, RL):
        col_name = node.children[0]
        col_arr = node.children[1]
        
        type_col_arr = self.check(col_arr, env, RL)

        env[col_name] = type_col_arr

    def check_table(self, node, env, RL):
        print("table name", node.data)

        for child in node.children:
            self.check(child, env, RL)

        return node.data


Typechecker().check_p(result)