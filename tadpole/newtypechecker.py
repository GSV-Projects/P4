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
        self.PD = {
            "filter" : ((int, 'tbl'), 'tbl'), # Test predefined function
            "test2" : ((float,), int), # another one
            "test3" : ((), str)
        }


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
            if isinstance(child, Tree) and (child.data == 'func_def' or child.data == 'func_def_ret'):
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
        #print("node", node)
        if isinstance(node, Token):
            return self.read_token(node, env)
        
        method_name = f'check_{node.data}'
        check_method = getattr(self, method_name, self.check_unknown)
        return check_method(node, env, RL)

    
    # check method to fall back on, if the given node is unknown
    def check_unknown(self, node, env, RL):
        raise Exception(f"No handler for node type: '{node.data}'")

    # --- directory ---
    # Rerouting similar checks
    def check_add(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_sub(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_mod(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_mult(self, node, env, RL):    return self.check_additive(node, env, RL)

    def check_less(self, node, env, RL):    return self.check_comparison(node, env, RL)
    def check_greater(self, node, env, RL): return self.check_comparison(node, env, RL)
    def check_leq(self, node, env, RL):     return self.check_comparison(node, env, RL)
    def check_geq(self, node, env, RL):     return self.check_comparison(node, env, RL)
    def check_equal(self, node, env, RL):   return self.check_comparison(node, env, RL)
    def check_neq(self, node, env, RL):     return self.check_comparison(node, env, RL)

    def check_or(self, node, env, RL):      return self.check_logical(node, env, RL)
    def check_and(self, node, env, RL):     return self.check_logical(node, env, RL)

    def check_func_def(self, node, env, RL):     return self.check_f(node, env, RL)
    def check_func_def_ret(self, node, env, RL): return self.check_f(node, env, RL)
    
    # --- check implements ---
    def check_IDENT(self, node, env):
        if (node.value not in env):
            raise Exception(f'{node.value} not defined')
        else: 
            return env[node.value]

    def check_assign(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        if isinstance(right, Tree) and right.data == "table":
            self.check_table(right, env, RL, table_id=left.value)
            return

        t1 = self.check(right, env, RL)
        #print("left", left.value)
        #print("t1",  t1)

        if (left.value not in env):
            env[left.value] = t1
        
        elif (env == self.vtable):
            if (env[left.value] != t1):
                raise Exception(f'{left.value} is of type {env[left.value]} and cannot be declared as type {t1}')
        else:
            env[left.value] = t1

        # Should be done
        ## TODO Hvis env = self.vtable -> check om env(left.value) er tom -> hvis ikke -> chekc om samme type -> hvis ikke -> error
        

    def check_additive(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        if t1 == int and t2 == int:
            return int
        elif t1 == float or t2 == float:
            return float
        else:
            raise Exception(f'Values {left.value} and {right.value} must be of type int or float')

    def check_div(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        if t1 in (int, float) and t2 in (int, float):
            return float
        else:
            raise Exception(f'Values {left.value} and {right.value} must be of type int or float')
        
    def check_comparison(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        if (t1 == int and t2 == int) or (t1 == float and t2 == float):
            return bool
        else: 
            raise Exception(f'Different types shi in comparison')

    def check_logical(self, node, env, RL):
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        if (t1 == bool and t2 == bool):
            return bool
        else:
            raise Exception(f'Values {left.value} and {right.value} must be of type bool')
        
    def check_not(self, node, env, RL):
        t1 = self.check(node.children[0], env, RL)

        if (t1 != bool): 
            raise Exception(f'To use the "not"-operator, subject must be a bool')
        return bool

    def check_neg(self, node, env, RL):
        t1 = self.check(node.children[0], env, RL)

        if t1 == int:
            return int
        elif t1 == float:
            return float
        else:
            raise Exception(f'{node.children[0]} must be of type int or float to negate the value')

    def check_array(self, node, env, RL):
        # check if the array is empty
        if len(node.children) == 0:
            raise Exception("No type for an empty array")

        type_first_elem = self.check(node.children[0], env, RL)
        #print("array type: ", type_first_elem)

        if (all(self.check(x, env, RL) == type_first_elem for x in node.children)):
            return [type_first_elem] # return as ARRAY of type T - [T], NOT simply T
        else: 
            raise Exception("Not all elems of array are of the same type")
        
    def check_array_type(self, node, env, RL):
        # Check function for [type] used in parameters and returns
        array_type = self.check(node.children[0], env, RL)
        return [array_type]
        
    # if x is an array of type T, and e is an Int, then x[e] has type T
    def check_index(self, node, env, RL):
        type_id = self.check(node.children[0], env, RL) # find the type for the array itself
        type_idx = self.check(node.children[1], env, RL) # find the type for the indexing nr

        if type_idx == int:
            return type_id
        else: 
            raise Exception(f'Did not parse an integer for array indexing')

    def check_table(self, node, env, RL, table_id = None):
        if table_id == None:
            table_id = node.data

        for col in node.children:
            c_id = col.children[0]
            arr = col.children[1]
            # Turn the use of dot-notation into an identifier, that the array can be assigned to
            token = Token('IDENT', f'{table_id}.{c_id.value}')
            S = Tree("assign", [token, arr])
        
            self.check(S, env, RL)

        # TODO: Why this
        env[table_id] = "tbl"

        # TODO: behøves det her return?
        #return table_id

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

        if len(body.children) == 0:
            raise Exception("function can't have an empty body")
            
        self.check(body, vtable_local, RL)

    def check_body(self, node, env, RL):
        for child in node.children:
            self.check(child, env, RL)
        
    def check_return(self, node, env, RL):
        t1 = self.check(node.children[0], env, RL)

        if (t1 != RL["R"]):
            raise Exception(f'{t1} doesnt match with function return type')

        return t1
    
    def check_call(self, node, env, RL):
        f_id = node.children[0]

        if (f_id not in self.ftable):
            raise Exception(f'Function not previously defined')

        print("id", f_id)

        formal_params, return_type = self.ftable[f_id]
        actual_params = node.children[1:]

        if len(formal_params) != len(actual_params):
            raise Exception("Amount of formal parameters do not match actual parameters")

        for i in range(len(formal_params)):
            t1 = self.check(actual_params[i], env, RL)
            t2 = formal_params[i]
            
            if t1 != t2:
                raise Exception(f'Formal and actual parameters of function {f_id} not of same type')
            
        return return_type
    
    def check_dot(self, node, env, RL):
        left = node.children[0]
        right = node.children[1:]

        id1 = self.check(left, env, RL)

        if id1 != 'tbl':
            raise Exception(f'{left} not a table')


        for child in right:
            child_left = child.children[0] # Name of predefined function
            actual_params = child.children[1:] # Actual parameters of predefined function
            if child_left not in self.PD:
                raise Exception(f'{child_left} is not defined')
            
            formal_params, return_type = self.PD[child_left]
            print("formal", formal_params)
            print("retu", return_type)

            if len(formal_params) != len(actual_params):
                raise Exception("Amount of formal parameters do not match actual parameters")

            for i in range(len(formal_params)):

                t1 = self.check(actual_params[i], env, RL) # Check type of actual parameter
                t2 = formal_params[i]

                if t1 != t2: # Check if actual and formal parameter types are the same
                    raise Exception(f'Formal and actual parameters of function {child_left} not of same type')

        return return_type # Return type if its an assignment

    def check_skip(self, node, env, RL):
        if RL["L"] == False:
            raise Exception(f'Cannot skip, not in loop')

    def check_stop(self, node, env, RL):
        if RL["L"] == False:
            raise Exception(f'Cannot stop, not in loop')

    def check_if(self, node, env, RL):
        t1 = self.check(node.children[0], env, RL)

        if t1 != bool:
            raise Exception(f'{node.children[0]} is not a boolean expression')

        body = node.children[1:]

        for child in body:
            self.check(child, env, RL)
    

    def check_else(self, node, env, RL):
        body = node.children
        
        for child in body:
            self.check(child, env, RL)

    def check_while(self, node, env, RL):
        print(node)
        t1 = self.check(node.children[0], env, RL)

        if t1 != bool:
            raise Exception(f'{node.children[0]} is not a boolean expression')

        body = node.children[1:]

        RL_new = RL.copy()
        RL_new["L"] = True

        for child in body:
            self.check(child, env, RL_new)


Typechecker().check_p(result)
