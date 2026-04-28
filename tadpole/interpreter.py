from lark import Lark, Transformer, v_args, Tree, Token
from parser_lexer_lark import result
import copy

class Interpreter():
    def __init__(self):
        self.vtable = {}
        self.ftable = {}

    # --- Run program ---
    def Eval_P(self, p):
        for line in p.children:
            if ((line.data == "func_def") or (line.data == "func_def_ret")):
                self.FEval(line, self.vtable)
            else:
                self.SEval(line, self.vtable)

        print("ftable:", self.ftable)
        print("vtable:", self.vtable)

    def FEval(self, declaration, env):
        method_name = f'FEval_{declaration.data}' # Accessing top node
        Eval_method = getattr(self, method_name, self.check_unknown)
        return Eval_method(declaration, env)
    
    def FEval_func_def(self, tree, env):
        param_items = tree.children[1]
        body = tree.children[2]
        def_env = copy.deepcopy(env)
        func_tuple = (body, param_items, def_env, self.ftable) # (S, x1...xn, env_v, env_p)
        self.ftable[tree.children[0].value] = func_tuple

    def FEval_func_def_ret(self, tree, env):
        pass

    def SEval(self, statement, env):

         # --- Tokens (leaf nodes) ---
        if isinstance(statement, Token):
            return self.read_token(statement, env)
        
        method_name = f'SEval_{statement.data}' # Accessing top node
        Eval_method = getattr(self, method_name, self.check_unknown)
        return Eval_method(statement, env)

    def SEval_assign(self, tree, env):
        v = self.Eval(tree.children[1], env)
        env[tree.children[0].value] = v

    def SEval_ret(self, tree, env):
        v = self.Eval(tree.children[0], env)
        return v

    def SEval_stop(self, tree, env):
        return self.SEval_stop(self,tree,env)
    
    def SEval_while(self, tree, env):
        v = self.Eval(tree.children[0], env)
        if v == True:
            env1 = self.SEval(tree.children[1], env)
            print("envi:", env1)
            print("hejsa", tree.children[1], env1)
            return self.SEval(tree, env1)
        elif v == False:
            return env
        else:
            raise Exception(f"variable not declared: '{tree}'")

    def SEval_if(self, tree, env):
        v = self.Eval(tree.children[0], env)
        if v == True:
            return self.SEval(tree.children[1],env)
        elif v == False:
            return env
        else:
            raise Exception(f"variable not declared: '{tree}'")

    def SEval_if_else(self, tree, env):
        v = self.Eval(tree.children[0], env)
        if v == True:
            return self.SEval(tree.children[1],env)
        elif v == False:
            return self.SEval(tree.children[2],env)
        else:
            raise Exception(f"variable not declared: '{tree}'")

    def SEval_comp(self, tree, env):
        env1 = self.SEval(tree.children[0],env)
        env2 = self.SEval(tree.children[1],env)
        v = self.env2          # raise Exceptio#variable not declared: '{tree}'")

    def SEval_call(self, tree, env):
        func = self.lookup(tree.children[0].value, self.ftable)
        body, params, def_env, ftable = func
        env_1 = self.bind(params, tree.children[1:], def_env)
        print("tis ", env_1)
        #return self.SEval(body, call_env)

    def bind(self, formal_params, actual_params, env):
        print(formal_params)
        for i in range(len(formal_params.children)):
            v = self.Eval(actual_params[i], env)
            env[formal_params.children[i].children[1].value] = v
        return env
        

    def lookup(self, token, env):
        if token in env:
            return env[token]
        else:
            raise Exception(f"variable not declared: '{token}'")

    def Eval(self, tree, env):
        # --- Tokens (leaf nodes) ---
        if isinstance(tree, Token):
            return self.read_token(tree, env)
        
        method_name = f'Eval_{tree.data}'
        Eval_method = getattr(self, method_name, self.check_unknown)
        return Eval_method(tree, env)
    
    def read_token(self, token, env):
        if token.type == 'IDENT':
            return self.lookup(token, env)
        if token.type == 'INT':
            return int(token.value)
        if token.type == 'FLOAT':
            return float(token)
        if token.type == 'STRING':
            return str(token)
        if token.type == 'FALSE':
            return False
        if token.type == 'TRUE':
            return True
        if token.type == 'tbl':
            return 'tbl'
        return 'unknown type shi'
    #  NEED TO ADD NA

    # Arithmetic evaluations
    def Eval_add(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 + v2
    
    def Eval_sub(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 - v2

    def Eval_mult(self, tree, env):
        v1 = self.Eval(tree.children[0], env) 
        v2 = self.Eval(tree.children[1], env)
        return v1 * v2
    
    def Eval_divide(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 / v2
    
    def Eval_mod(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 % v2
    
    def Eval_exp(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1**v2
    
    # Boolean evaluations
    def Eval_equal(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 == v2
    
    def Eval_not_equal(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 != v2
    
    def Eval_less(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 < v2
    
    def Eval_less_eq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 <= v2

    def Eval_greater(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 > v2
    
    def Eval_greater_eq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 >= v2
    
    def Eval_and(self, tree, env):
        print(tree.children[0].value)
        print(tree.children[1].value)
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 and v2
    
    def Eval_or(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        return v1 or v2
    
    def Eval_not(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        return not v1

    def Eval_neg(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        return -v1

    def Eval_array(self, tree, env):
        values = []
        for i in range(len(tree.children)):
            v = self.Eval(tree.children[i], env)
            values.append(v)
        return values
    
    def Eval_index(self, tree, env):
        x = self.Eval(tree.children[0], env)
        i = self.Eval(tree.children[1], env)

        if (i > 0 and i <= len(x)):
            return x[i-1] # Adjust for python zero indexing
        else:
            raise Exception(f"index out of bounds, must be between: '{1}'-'{len(x)}'")
    

    def check_unknown(self, node, env):
        raise Exception(f"No handler for node type: '{node.data}'")

Interpreter().Eval_P(result)