from lark import Tree, Token
from tadpole.table import Table
from tadpole.utils.returnClass import return_value
from tadpole.utils.stopClass import stop 
from tadpole.utils.NAliteral import NA
import copy, math

class Evaluator():
    def __init__(self):
        # Initial variable environment,
        #   Procedure/function and pre-defined function environment.
        self.env_v = {}
        self.env_p = {} 
        self.env_pd = self.init_ptable()

    # Initialize table of predefined functions (called with dot)
    def init_ptable(self):
        return {
            "read":         Table.read,
            "readfill":     Table.read_fill,
            "replaceNA":    Table.replace_na_values,
            "rename" :      Table.rename,
            "append":       Table.append,
            "remove":       Table.remove,
            "mutate":       Table.mutate,
            "filterall" :   Table.filter_all,
            "filtercol":    Table.filter_col,
            "firstrow":     Table.first_row,
            "getrow":       Table.get_row,
            "lastrow":      Table.last_row,
            "sort" :        Table.sort,
            "round":        Table.round_table,
            "cell":         Table.cell,
            "getcol":       Table.get_col,
            "firstcol":     Table.first_col,
            "lastcol":      Table.last_col,
            "roundcol":     Table.round_col,
            "keys":         Table.keys,
            "sortcol":      Table.sort_col,
            "length":       Table.len_col,
            "head" :        Table.head,
            "tail" :        Table.tail,
            "mean" :        Table.mean,
            "sum" :         Table.sum,
            "frequency" :   Table.frequency,
            "median" :      Table.median,
            "lowerq" :      Table.lowerq,
            "upperq" :      Table.upperq,
            "min" :         Table.min,
            "max" :         Table.max,
            "range" :       Table.range,
            "variance":     Table.variance,
            "stddev":       Table.std_dev,
        }

    # Evaluate the programs definition and statements
    def PEval(self, p):
        for line in p.children:
            if ((line.data == "func_def") or (line.data == "func_def_ret")):
                # Evaluation of declarations
                self.FEval(line, self.env_v, self.env_p)
            else:
                # Evaluation of statements
                self.SEval(line, self.env_v, self.env_p)

        #print("Evaluator Env_P:", self.env_p)
        #print("Evaluator Env_V:", self.env_v)

# Function evaluations
    # Function used to determine which evaluation method to be called
    def FEval(self, declaration, env_v, env_p):
        # Accessing an arbitrary node - allowing for recursive calls i.e. "FEval_func_def"
        method_name = f'FEval_{declaration.data}'
        # Uses the method name string to find the associated method in the current object to be called.
        #   Throws an error if it wasn't found.
        Eval_method = getattr(self, method_name, self.eval_unknown)
        # Calling the needed function
        Eval_method(declaration, env_v, env_p)
    
    # Evaluate the void function definition
    def FEval_func_def(self, tree, env_v, env_p):
        # Gather the list of formal parameters from the AST
        param_items = tree.children[1]
        # Gather the body of the function which holds the statement(s)
        body = tree.children[2]
        # Copying environments to place inside a tuple which is the closure of the function
        def_env_v = copy.deepcopy(env_v)
        def_env_p = copy.deepcopy(env_p) 
        # Initialize the tuple with body of function, formal parameters and definition time environments (env_V, env_P)
        func_tuple = (body, param_items, def_env_v, def_env_p)
        # Gather the name of the function to be used as a key in the current procedure environment (env_P). 
        #   The value for this key is the function closure above.
        func_ident = tree.children[0].value
        if (func_ident in self.env_p):
            raise Exception(f"Function '{func_ident}' already defined")
        else:
            self.env_p[func_ident] = func_tuple

    # Evaluate the non-void function definition
    def FEval_func_def_ret(self, tree, env_v, env_p):
        # Gather the list of formal parameters from the AST
        param_items = tree.children[1]
        # Gather the body of the function which holds the statement(s).
        body = tree.children[3]
        # Copying environments to place inside a tuple which is the closure of the function
        def_env_v = copy.deepcopy(env_v)
        def_env_p = copy.deepcopy(env_p)
        # Initialize the tuple with body of function, formal parameters and definition time environments (env_V, env_P)
        func_tuple = (body, param_items, def_env_v, def_env_p)
        # Gather the name of the function to be used as a key in the current procedure environment (env_P). 
        #   The value for this key is the function closure above.
        func_ident = tree.children[0].value
        if (func_ident in self.env_p):
            raise Exception(f"Function '{func_ident}' already defined")
        else:
            self.env_p[func_ident] = func_tuple

# Statement evaluation
    # Function used to determine which evaluation method to be called
    def SEval(self, statement, env_v, env_p):
        # If the node is a Token, call read_token() to evaluate the leaf
        if isinstance(statement, Token):
            return self.read_token(statement, env_v)
        
        # Accessing an arbitrary node - allowing for recursive calls i.e. "SEval_assign"
        method_name = f'SEval_{statement.data}'
        # Uses the method name string to find the associated method in the current object to be called.
        #   Throws an error if it wasn't found.
        Eval_method = getattr(self, method_name, self.eval_unknown)
        # Calling the needed function
        return Eval_method(statement, env_v, env_p)

    # Assign and declaration of variables
    def SEval_assign(self, tree, env_v, env_p):
        # The identifier of the assignment i.e. "x" in "x = 5 + 5;"
        identifier = tree.children[0].value
        # The expression of the assignment i.e. "5 + 5" in "x = 5 + 5;
        value = tree.children[1]
        # Evaluate the expression
        v = self.Eval(value, env_v)

        # Guard to check if value being assinged is only NA. This is only allowed if i.e. "x = 5 + NA;"
        if v is NA and tree.children[1] is Token:
            raise Exception(f"Cannot assign NA to variable: '{identifier}'. Only possible if another type is in the expression such as: x = 5 + NA;")

        # Update the variable environment
        env_v[identifier] = v

    # Return statement using the implementation of return exception to surpass the call stack
    def SEval_return(self, tree, env_v, env_p):
        v = self.Eval(tree.children[0], env_v)
        # Raises an exception, as an alternative to a normal return, this is done to skip the stack of function calls.
        #   And return directly to Eval_call
        raise return_value(v)

    # Stop statement to be used in while loops
    def SEval_stop(self, tree, env_v, env_p):
        # Same logic as for the return exception. The exception is caught in SEval_while, making the function return,
        #   instead of evaluating the next statement in the while loop body
        raise stop
        
    # While loops
    def SEval_while(self, tree, env_v, env_p):
        # Evaluate the condition
        v = self.Eval(tree.children[0], env_v)
        # Gather the body statements of the loop
        body = tree.children[1:] # Takes 1 elements and up to n elements
        # If the condition is true evaluate the body, if not exit
        if v == True:
            for child in body:
                try: 
                    self.SEval(child, env_v, env_p)
                except stop: # If stop statement occurs, return
                    return    
            self.SEval(tree, env_v, env_p)
            
    # If statements
    def SEval_if(self, tree, env_v, env_p):
        v = self.Eval(tree.children[0], env_v)
        if v is NA:
            raise Exception("Condition evaluated to NA. Condition must evaluate to true or false")
        elif v == True:
            self.SEval(tree.children[1], env_v, env_p) # Will evaluate SEval_then
        elif v == False and len(tree.children) == 3:
            self.SEval(tree.children[2], env_v, env_p) # Will evaluate SEval_else
        
    # Then clause - evaluate the body
    def SEval_then(self, tree, env_v, env_p):
        for child in tree.children:
            self.SEval(child, env_v, env_p)

    # Else clause - evaluate the body
    def SEval_else(self, tree, env_v, env_p):
        for child in tree.children:
            self.SEval(child, env_v, env_p)

    # Assign indexing of arrays i.e. x[3] = 2;
    def SEval_assign_index(self, tree, env_v, env_p):
        # Identifier of array
        identifier = tree.children[0]
        
        # Lookup the array
        arr = self.Eval(identifier, env_v)

        # Evaluate the index
        i = self.Eval(tree.children[1], env_v)
        # Evaluate the expression being assigned
        v = self.Eval(tree.children[2], env_v)

        if (v is NA):
            raise Exception(f'Index must be an integer to index the array')

        # Check for out-of-bounds
        if (i > 0 and i <= len(arr)):
            arr[i-1] = v
            env_v[identifier] = arr
        else:
            raise Exception(f"Index out of bounds, must be between: '{1}'-'{len(arr)}'")

    # Statement for calling of void functions (not apart of an expression)
    def SEval_call(self, tree, caller_env_v, env_p):
        func_name = tree.children[0].value
        
        # Special case if the function name is print, then we will print the desired output to console
        if func_name == 'print':
            args = []
            for children in tree.children[1:]:
                v = self.Eval(children, caller_env_v)
                if(v == 'sus'):
                    self.amogus()
                    return
                if(v == "67"):
                    self.sixseven()
                args.append(v)
            print(*args)
            return
        
        # Lookup the desired function inside the procedure environment and gather tuple,
        #   containing declaration time environments, formal parameters and body of function.
        func_tuple = self.lookup(tree.children[0].value, env_p)
        body, params, def_env_v, def_env_p = func_tuple # Body, formal params, variable environment and procedure environment
        # Save a copy of this "old" function tuple, will be needed later to allow for correct restoring of the possibly changed function environments.
        old_func_tuple = copy.deepcopy(func_tuple)
        env_v_copy = copy.deepcopy(def_env_v)
        # Create a local function environment with actual parameters being passed to the formal parameters.
        #   The calling environment will be used to make sure the most updated actual parameters will be used - not the ones know at declaration time.
        local_env = self.bind(params, tree.children[1:], env_v_copy, caller_env_v)
        # Updating the function tuple with current local environment, such that it can be used in next possible recursive call
        func_tuple = (body, params, local_env, def_env_p)
        self.env_p[tree.children[0].value] = func_tuple # Replace function definition in procedure environment with new func tuple for possibility of recursion
        try:
            self.SEval(body, local_env, def_env_p) # Evaluate the body in local environment
            self.env_p[tree.children[0].value] = old_func_tuple # Restore procedure environment to old definition of func tuple
        except return_value as e:
            self.env_p[tree.children[0].value] = old_func_tuple # Restore procedure environment to old definition of func tuple
            return e.value

    # Evaluation of the body of a function
    def SEval_body(self, tree, env_v, env_p):
        for child in tree.children:
            result = self.SEval(child, env_v, env_p)
            if (child.data == "return") or isinstance(result, (int, str, float, bool)):
                return result

# Expression evaluation
    def Eval(self, tree, env):
        # If the node is a Token, call read_token() to evaluate the leaf
        if isinstance(tree, Token):
            return self.read_token(tree, env)
        
        # Accessing an arbitrary node - allowing for recursive calls i.e. "Eval_add"
        method_name = f'Eval_{tree.data}'
        # Uses the method name string to find the associated method in the current object to be called.
        #   Throws an error if it wasn't found.
        Eval_method = getattr(self, method_name, self.eval_unknown)
        # Calling the needed function
        return Eval_method(tree, env)

    # Addition
    def Eval_add(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 + v2
    
    # Subtraction
    def Eval_sub(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 - v2

    # Multiplication
    def Eval_mult(self, tree, env):
        v1 = self.Eval(tree.children[0], env) 
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 * v2
    
    # Division (added a guard for zero-division)
    def Eval_div(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            if (v2 == 0):
                raise Exception(f"Division by zero not allowed")
            return v1 / v2

    # Modulo (with zero guard)
    def Eval_mod(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            if (v2 == 0):
                raise Exception("Modulo by zero is undefined")
            else:
                return v1 % v2
    
    # Exponent
    def Eval_exp(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 ** v2
    
    # Equality
    def Eval_equal(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 == v2
    
    # Not equal
    def Eval_neq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 != v2
    
    # Less
    def Eval_less(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 < v2
    
    # Less or equal
    def Eval_leq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 <= v2

    # Greater
    def Eval_greater(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 > v2
    
    # Greater or equal
    def Eval_geq(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 >= v2
    
    # Logical AND
    def Eval_and(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 and v2
    
    # Logical OR
    def Eval_or(self, tree, env):
        v1 = self.Eval(tree.children[0], env)
        v2 = self.Eval(tree.children[1], env)
        if (v1 is NA or v2 is NA):
            return NA
        else:
            return v1 or v2
    
    # Logical NOT
    def Eval_not(self, tree, env):
        v = self.Eval(tree.children[0], env)
        if (v is NA):
            return NA
        else:
            return not v

    # Negation
    def Eval_neg(self, tree, env):
        v = self.Eval(tree.children[0], env)
        if (v is NA):
            return NA
        else:
            return -v

    # Arrays
    def Eval_array(self, tree, env):
        values = []
        for child in tree.children:
            v = self.Eval(child, env)
            values.append(v)
        return values
    
    # Array indexing i.e. value = arr[2];
    def Eval_index(self, tree, env):
        # Identifier of array
        identifier = tree.children[0]
        
        # Lookup the array
        arr = self.Eval(identifier, env)
        # Evaluate the index
        i = self.Eval(tree.children[1], env)

        if (i is NA):
            raise Exception(f"Index cannot be NA, must be an integer between: '{1}'-'{len(arr)}'")
        elif (i > 0 and i <= len(arr)):
            return arr[math.floor(i-1)] # Gather element while adjusting for python zero indexing
        else:
            raise Exception(f"Index out of bounds, must be between: '{1}'-'{len(arr)}'")
        
    # Calling of functions with returns (apart of an expression i.e. x = foo();)
    def Eval_call(self, tree, caller_env_v):
        # Lookup the desired function inside the procedure environment and gather tuple,
        #   containing declaration time environments, formal parameters and body of function.
        func_tuple = self.lookup(tree.children[0].value, self.env_p)
        body, params, def_env_v, def_env_p = func_tuple # Body, formal params, variable environment and procedure environment
        # Save a copy of this "old" function tuple, will be needed later to allow for correct restoring of the possibly changed function environments.
        old_func_tuple = copy.deepcopy(func_tuple)
        env_v_copy = copy.deepcopy(def_env_v)
        # Create a local function environment with actual parameters being passed to the formal parameters.
        #   The calling environment will be used to make sure the most updated actual parameters will be used - not the ones know at declaration time.
        local_env = self.bind(params, tree.children[1:], env_v_copy, caller_env_v)
        # Updating the function tuple with current local environment, such that it can be used in next possible recursive call
        func_tuple = (body, params, local_env, def_env_p)
        self.env_p[tree.children[0].value] = func_tuple # Replace function definition in procedure environment with new func tuple for possibility of recursion
        try:
            self.SEval(body, local_env, def_env_p) # Evaluate the body in local environment
            self.env_p[tree.children[0].value] = old_func_tuple # Restore procedure environment to old definition of func tuple
        except return_value as e:
            self.env_p[tree.children[0].value] = old_func_tuple # Restore procedure environment to old definition of func tuple
            return e.value

    # Handles the call of predefined dot functions
    def Eval_dot(self, tree, env):
        # Looks up the table in environment and the name of the function
        table = self.lookup(tree.children[0].value, env) # Gets the table from variable environment
        method_name = tree.children[1].children[0].value # Gets the name of the method called

        parameters = [] # Will hold all params for the called method

        if (method_name not in self.env_pd):
            raise Exception(f'Tried to call function {method_name}, which does not exist')
        
        # Set of possible operations that can be read when passing expressinos as parameters
        expressions = {"equal", "neq", "less", "leq", "greater", "geq", "and", "or", "not", 
                       "add", "sub", "mult", "divide", "mod", "exp"}

        for actual_params in tree.children[1].children[1:]:
            # If the argument is a boolean expression, consider the tree data, 
            #   and ensure the expression is constructed using the operators in expressions
            if isinstance(actual_params, Tree) and actual_params.data in expressions:
                # Trivially a closure, to ensure new references to actual params for row_expr
                mutate_col = actual_params.children[0]
                def make_lambda(expr_tree, env):
                    # Make a closure function, meaning it only works with the params given for the current iteration,
                    #   thus working on a new scope each iteration, where the expr_tree and env vary.
                    def row_expr(row):
                        # Merge (** operator) program's variables with row's columns, making a combined environment.
                        #   Eval will operationally evaluate the exprression in the combined env. 
                        return self.Eval(expr_tree, {**env, **row}) 
                    return row_expr
                # Calling make_lambda to pass actual_params at this moment for current iteration
                parameters.append(make_lambda(actual_params, env))
            else:
                parameters.append(self.Eval(actual_params, env))
        
        # If method called is 'mutate', we send the name of the column as a parameter,
        #   meaning the user does not have to type it themselves
        if method_name == 'mutate':
            execute = self.env_pd[method_name](table, mutate_col, *parameters)
        else: 
            # Execute the function with the corresponding parameters and table
            execute = self.env_pd[method_name](table, *parameters)
        return execute

        
    # Tables
    def Eval_table(self, tree, env):
        columns = {}
        for column in tree.children:
            col_name = column.children[0].value # column name
            col_values = self.Eval(column.children[1], env) # column value which is an array
            columns[col_name] = col_values # Building table using Python dictionary data structure

        # Guard to make sure all lenghts of the columns in the table are equal
        lengths = [len(v) for v in columns.values()]
        if len(set(lengths)) > 1: # set() convers the array into a set, thus not containing duplicates
            raise Exception("Table columns must all have the same length")
    
        # Creates an instance of our Table structure using the class Table and returns it
        return Table(columns)
    
# Helper functions for evaluation
    # Lookup method, first looking up in the current environment (local or declaration env),
    #   then if it's not found, lookup in the outermost environment (global)
    def lookup(self, token, env):
        if token in env:
            return env[token]
        elif token in self.env_v: # Fallback to the outermost environment
            return self.env_v[token]
        else:
            raise Exception(f"Variable not declared: '{token}'")
        
    # Binding method for binding actual parameters to formal parameters
    def bind(self, formal_params, actual_params, local_env, caller_env):
        actual_param_values = []

        # For loop to loop over the actual parameters. Evaluates them in the environment known at call time
        for child in actual_params:
            v = self.Eval(child, caller_env)
            actual_param_values.append(v)

        # Update the local environment (function body) with the new values for the formal parameters that will be used during execution
        for i in range(len(actual_param_values)):
            # Updating the environment with formal parameter variables only and ignoring the types of the formal parameters, 
            #   i.e. (int a, int b): Only a and b gets assigned.
            local_env[formal_params.children[i].children[1].value] = actual_param_values[i]
        return local_env
        
    # Method for reading the leaf nodes of a tree and evaluating them accordingly
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
        if token.type == 'NA':
            # The NA literal is a singleton instance of the NAliteral class
            #   This means we can use "is" NA to check if a value is NA, as all NA values point to the same object in memory
            return NA
        raise Exception(f"Unknown type '{token.type}', must be either INT, FLOAT, STRING, FALSE, TRUE, NA or tbl")

    # Error function: if the method name taken from the AST doesn't correspond to an actual function in the evaluator
    def eval_unknown(self, node, env):
        raise Exception(f'Unknown language construct "{node.data}"')
    
    def amogus(self):
        a = '''
              ⠀⠀⠀⠀ ⣠⣤⣤⣤⣤⣤⣤⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠛⠉⠙⠛⠛⠛⠛⠻⢿⣿⣷⣤⡀⠀⠀⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠋⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠈⢻⣿⣿⡄⠀⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⣸⣿⡏⠀⠀⠀⣠⣶⣾⣿⣿⣿⠿⠿⠿⢿⣿⣿⣿⣄⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⣿⣿⠁⠀⠀⢰⣿⣿⣯⠁⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀ 
        ⠀⠀⣀⣤⣴⣶⣶⣿⡟⠀⠀⠀⢸⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⠀ 
        ⠀⢰⣿⡟⠋⠉⣹⣿⡇⠀⠀⠀⠘⣿⣿⣿⣿⣷⣦⣤⣤⣤⣶⣶⣶⣶⣿⣿⣿⠀ 
        ⠀⢸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀ 
        ⠀⣸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠉⠻⠿⣿⣿⣿⣿⡿⠿⠿⠛⢻⣿⡇⠀⠀ 
        ⠀⣿⣿⠁⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣧⠀⠀ 
        ⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀ 
        ⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀ 
        ⠀⢿⣿⡆⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀ 
        ⠀⠸⣿⣧⡀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠃⠀⠀ 
        ⠀⠀⠛⢿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⣰⣿⣿⣷⣶⣶⣶⣶⠶⠀⢠⣿⣿⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⣽⣿⡏⠁⠀⠀⢸⣿⡇⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⢹⣿⡆⠀⠀⠀⣸⣿⠇⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⢿⣿⣦⣄⣀⣠⣴⣿⣿⠁⠀⠈⠻⣿⣿⣿⣿⡿⠏⠀⠀⠀⠀ 
        ⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠿⠿⠿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        '''
        print(a)

    def sixseven(self):
        a = '''
⠀⠀⢀⠤⣂⣤⣬⣭⣭⣭⣔⡠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠔⣵⣾⣿⣿⣿⢿⣿⣿⣿⣿⣎⢂⠀⢲⣤⣤⣤⣤⣀⣒⣒⣒⣒⣂⡠⠤⠤⣄
⠐⣾⣿⣿⣿⡏⣾⡿⢎⣛⣫⣭⣴⣾⠆⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢼
⡇⣿⣿⣿⣿⣟⡿⢀⣐⣻⣛⡩⢁⠀⠀⣘⣛⣛⡛⠿⠿⠿⢿⣿⣿⣿⣿⣿⢟⣾
⡇⣿⣿⣿⣿⣷⣾⣿⣿⣿⣿⣿⣶⡕⠄⠉⠛⠛⠛⠛⡻⣣⣾⣿⣿⣿⢟⣵⣿⠛
⠃⣿⣿⣿⣿⣿⢋⣥⠭⡻⣿⣿⣿⣿⡌⡄⠀⠀⠀⡐⣼⣿⣿⣿⡿⣣⣾⠏⠀⠀
⠨⢻⣿⣿⣿⣧⢻⠁⠀⠘⢸⣿⣿⣿⡇⣿⠀⠀⠌⣼⣿⣿⣿⡿⢱⣿⠃⠀⠀⠀
⠀⢦⢻⣿⣿⣿⣦⣐⣀⣊⣼⣿⣿⡿⢱⡿⠀⠰⣸⣿⣿⣿⣿⢣⣿⠃⠀⠀⠀⠀
⠀⠀⠣⣙⠿⣿⣿⣿⣿⣿⣿⠿⢛⣵⡿⠃⢀⢃⣿⣿⣿⣿⡟⣾⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠛⠶⣮⣭⣭⣴⣶⡿⠿⠋⠀⠀⢨⣘⣿⡻⠿⠿⢇⣿⠀⠀⠀⠀⠀⠀
⠀⠀⢀⠔⠒⠂⠠⠤⠭⡀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠛⠛⠛⠻⠃⠀⠀⠀⠀⠀⠀
⢀⠆⠁⠀⡄⠀⠀⠀⠀⠈⢂⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠒⠁⠀⠀⠒⢤⡀⠀⠀
⠣⠤⢤⠞⠂⠀⣀⠰⠃⠀⠘⣆⢀⣀⠀⠀⠀⠀⢀⠎⠀⢠⡀⠀⠀⠀⢀⠀⠙⡀
⠀⠀⢸⠀⠈⠭⡀⢈⣡⠔⢶⠁⣹⢩⠃⠀⢀⠀⢸⠀⠀⠀⣑⣠⣤⠀⠙⡦⣀⠜
⠀⠀⠀⠣⠀⢂⠞⠱⠴⣈⡸⠰⢇⠘⠀⠰⡭⠷⢝⡤⣂⣄⠒⢤⡐⠀⠀⡇⠀⠀
⠀⠀⠀⠀⠱⠄⣀⢜⢁⡠⠥⠊⠀⠀⠀⠀⠡⡘⡄⠐⡂⠘⢌⡀⠉⠂⡸⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠄⠹⢅⣀⠹⠒⠊⠀⠀⠀⠠
        '''
        print(a)