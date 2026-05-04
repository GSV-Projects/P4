from lark import Lark, Transformer, v_args, Tree, Token
from table import Table
from utils.returnClass import return_value
from utils.NAliteral import NA
import copy, math

class Interpreter():
    def __init__(self):
        self.env_v = {} # Global variable environment
        self.env_p = {} # Global procedure/function environment
        self.env_pd = self.init_ptable()

    # Initialize table of predefined functions (called with dot)
    def init_ptable(self):
        return {
            "read":         Table.read,
            "mean" :        Table.mean,
            "first" :       Table.first,
            "last" :        Table.last,
            "sum" :         Table.sum,
            "frequency" :   Table.frequency,
            "filter" :      Table.filter,
            "median" :      Table.median,
            "lowerq" :      Table.lowerq,
            "upperq" :      Table.upperq,
            "min" :         Table.min,
            "max" :         Table.max,
            "span" :        Table.span,
            "rename" :      Table.rename
        }

    # --- Run program ---
    def Eval_P(self, p):
        for line in p.children:
            if ((line.data == "func_def") or (line.data == "func_def_ret")):
                self.FEval(line, self.env_v, self.env_p)
            else:
                self.SEval(line, self.env_v, self.env_p)

        print("Elavator ftable:", self.env_p)
        print("Elavator vtable:", self.env_v)

# FUNCTION EVALUATION
    def FEval(self, declaration, env_v, env_p):
        method_name = f'FEval_{declaration.data}' # Accessing top node
        Eval_method = getattr(self, method_name, self.check_unknown)
        Eval_method(declaration, env_v, env_p)
    
    def FEval_func_def(self, tree, env_v, env_p):
        param_items = tree.children[1]
        body = tree.children[2]
        def_env_v = copy.deepcopy(env_v) # copy of vtable at declaration time
        def_env_p = copy.deepcopy(env_p) # copy of ftable at declaration time
        func_tuple = (body, param_items, def_env_v, def_env_p)
        func_ident = tree.children[0].value
        if (func_ident in self.env_p):
            raise Exception(f"Function '{func_ident}' already defined")
        else:
            self.env_p[func_ident] = func_tuple # Update global ftable

    def FEval_func_def_ret(self, tree, env_v, env_p):
        param_items = tree.children[1]
        body = tree.children[3] # third argument since the second argument in return functions is the return type
        def_env_v = copy.deepcopy(env_v)
        def_env_p = copy.deepcopy(env_p)
        func_tuple = (body, param_items, def_env_v, def_env_p)
        func_ident = tree.children[0].value
        if (func_ident in self.env_p):
            raise Exception(f"Function '{func_ident}' already defined")
        else:
            self.env_p[func_ident] = func_tuple # Update global ftable

# STATEMENTS EVALUATION
    def SEval(self, statement, env_v, env_p):
         # --- Tokens (leaf nodes) ---
        if isinstance(statement, Token):
            return self.read_token(statement, env_v) # Return is needed
        
        method_name = f'SEval_{statement.data}' # Accessing top node
        Eval_method = getattr(self, method_name, self.check_unknown)
        return Eval_method(statement, env_v, env_p)

    def SEval_assign(self, tree, env_v, env_p):
        name = tree.children[0].value
        type = tree.children[1]

        # Check if the rvalue is a table node
        if isinstance(type, Tree) and type.data == "table":
            env_v[name] = self.Eval_table(type, env_v)
            return
        
        v = self.Eval(tree.children[1], env_v)
        env_v[tree.children[0].value] = v

    def SEval_return(self, tree, env):
        v = self.Eval(tree.children[0], env)
        raise return_value(v)

    def SEval_stop(self, tree, env_v, env_p):
        return self.SEval_stop(self, tree, env_v)
    
    def SEval_while(self, tree, env_v, env_p):
        v = self.Eval(tree.children[0], env_v)
        if v == True:
            env1 = self.SEval(tree.children[1], env_v, env_p)
            return self.SEval(tree, env1, env_p)
        elif v == False:
            return env_v
        else:
            raise Exception(f"variable not declared: '{tree}'")

    def SEval_if(self, tree, env_v, env_p):
        v = self.Eval(tree.children[0], env_v)
        if v == True:
            return self.SEval(tree.children[1], env_v, env_p)
        elif v == False and len(tree.children) == 3:
            return self.SEval(tree.children[2], env_v, env_p)
        
    # TODO: prollyy wrong at return hvert eneste child?, men skal måske return hvis der er et "return i if statement"
    def SEval_then(self, tree, env_v, env_p):
        for child in tree.children:
            result = self.SEval(child, env_v, env_p)
            if (child.data == "return") or isinstance(result, (int, str, float, bool)):
                return result

    # TODO: prollyy wrong at return hvert eneste child?, men skal måske return hvis der er et "return i if statement
    def SEval_else(self, tree, env_v, env_p):
        for child in tree.children:
            result = self.SEval(child, env_v, env_p)
            if (child.data == "return") or isinstance(result, (int, str, float, bool)):
                return result

    def SEval_assign_index(self, tree, env_v, env_p):
        name = tree.children[0].value
        arr = self.lookup(name, env_v) 
        i = self.Eval(tree.children[1], env_v)
        v = self.Eval(tree.children[2], env_v)
        if (i > 0 and i <= len(arr)):
            arr[i-1] = v
            env_v[name] = arr
        else:
            raise Exception(f"index out of bounds, must be between: '{1}'-'{len(arr)}'")

    def SEval_call(self, tree, caller_env_v, env_p):
        func_tuple = self.lookup(tree.children[0].value, env_p)
        body, params, def_env_v, def_env_p = func_tuple
        old_func_tuple = copy.deepcopy(func_tuple)
        env_v_copy = copy.deepcopy(def_env_v)
        local_env = self.bind(params, tree.children[1:], env_v_copy, caller_env_v)
        func_tuple = (body, params, local_env, def_env_p)
        self.env_p[tree.children[0].value] = func_tuple # Replace global env_p definition with new func tuple for possibility of recursion
        result = self.SEval(body, local_env, def_env_p)
        self.env_p[tree.children[0].value] = old_func_tuple # Restore global env_p to old definition of func tuple
        return result

    def SEval_body(self, tree, env_v, env_p):
        for child in tree.children:
            result = self.SEval(child, env_v, env_p)
            if (child.data == "return") or isinstance(result, (int, str, float, bool)):
                return result
        
# EXPRESSION EVALUATION
    def Eval(self, tree, env):
        # --- Tokens (leaf nodes) ---
        if isinstance(tree, Token):
            return self.read_token(tree, env)
        
        if isinstance(tree, Token):
                return self.read_token(tree, env)
        
        method_name = f'Eval_{tree.data}'
        Eval_method = getattr(self, method_name, self.check_unknown)
        return Eval_method(tree, env)

    # Arithmetic evaluations
    def Eval_add(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 + v2
    
    def Eval_sub(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 - v2

    def Eval_mult(self, tree, env):
        v1 = self.Eval(tree.children[0], env) 
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 * v2
    
    def Eval_div(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 / v2

    def Eval_mod(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 % v2
    
    def Eval_exp(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 ** v2
    
    # Boolean evaluations
    def Eval_equal(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 == v2
    
    def Eval_neq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 != v2
    
    def Eval_less(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 < v2
    
    def Eval_less_eq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 <= v2

    def Eval_greater(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 > v2
    
    def Eval_greater_eq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 >= v2
    
    def Eval_and(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 and v2
    
    def Eval_or(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 or v2
    
    def Eval_not(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        if (v1 is NA):
            return NA
        else:
            return not v1

    def Eval_neg(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        if (v1 is NA):
            return NA
        else:
            return -v1

    def Eval_array(self, tree, env):
        values = []
        for child in tree.children:
            v = self.Eval(child, env)
            values.append(v)
        return values
    
    def Eval_index(self, tree, env):
        x = self.Eval(tree.children[0], env)
        i = self.Eval(tree.children[1], env)

        if (i is NA):
            raise Exception(f"Index cannot be NA, must be an integer between: '{1}'-'{len(x)}'")
        elif (i > 0 and i <= len(x)):
            return x[math.floor(i-1)] # Adjust for python zero indexing
        else:
            raise Exception(f"index out of bounds, must be between: '{1}'-'{len(x)}'")
        
    def Eval_call(self, tree, caller_env_v):
        func_tuple = self.lookup(tree.children[0].value, self.env_p)
        body, params, def_env_v, def_env_p = func_tuple
        old_func_tuple = copy.deepcopy(func_tuple)
        env_v_copy = copy.deepcopy(def_env_v)
        local_env = self.bind(params, tree.children[1:], env_v_copy, caller_env_v)
        func_tuple = (body, params, local_env, def_env_p)
        self.env_p[tree.children[0].value] = func_tuple # Replace global env_p definition with new func tuple
        result = self.SEval(body, local_env, def_env_p)
        self.env_p[tree.children[0].value] = old_func_tuple # Restore global env_p to old definition of func tuple
        return result

    # Handles the call of predefined dot functions
    def Eval_dot(self, tree, env):
        # Looks up the table in environment and the name of the function
        table = self.lookup(tree.children[0].value, env) # Gets the table from vtable
        method_name = tree.children[1].children[0].value # Gets the name of the method called

        parameters = [] # Will hold all params for the called method

        if (method_name not in self.env_pd):
            raise Exception(f'Tried to call function {method_name}, which does not exist')
        
        for actual_params in tree.children[1].children[1:]:
            parameters.append(self.Eval(actual_params, env))
        execute = self.env_pd[method_name](table, *parameters)
        return execute
        
    def Eval_table(self, tree, env):
        columns = {}
        for column in tree.children:
            col_name = column.children[0].value
            col_values = self.Eval(column.children[1], env)
            columns[col_name] = col_values
        return Table(columns)
    
# MISC EVALUATION
    def lookup(self, token, env):
        if token in env:
            return env[token]
        elif token in self.env_v: # Fallback to the global environment
            return self.env_v[token]
        else:
            raise Exception(f"variable not declared: '{token}'")
        
    def bind(self, formal_params, actual_params, local_env, caller_env):
        actual_param_values = []
        for child in actual_params:
            v = self.Eval(child, caller_env)
            actual_param_values.append(v)

        for i in range(len(actual_param_values)):
            local_env[formal_params.children[i].children[1].value] = actual_param_values[i]
        return local_env
        
    def read_token(self, token, env):
        if token.type == 'IDENT':
            return self.lookup(token, env)
        if token.type == 'INT':
            return int(token.value)
        if token.type == 'FLOAT':
            return float(token)
        if token.type == 'STRING':
            return str(token)[1:-1]
        if token.type == 'FALSE':
            return False
        if token.type == 'TRUE':
            return True
        if token.type == 'tbl':
            return 'tbl'
        return 'unknown type shi'

    def check_unknown(self, node, env):
        raise Exception(f"No handler for node type: '{node.data}'")