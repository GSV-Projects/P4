from lark import Lark, Transformer, v_args, Tree, Token
from .utils.NAliteral import na_type
import copy

class Typechecker():
    def __init__(self):
        self.vtable = {}
        self.ftable = {}
        self.RL = {
            "R" : None,
            "L" : False
        }
        self.ptable = { 
            "read":         ('tbl'),    
            "readfill":     ('tbl'),
            "replaceNA":    ('tbl'),    
            "getcol":       ([]),       
            "getfirst":     ([]),       
            "getlast":      ([]),       
            "mean" :        (int),      
            "head" :        ((int, float, str, bool)),
            "tail" :        ((int, float, str, bool)),
            "sum" :         (float),    
            "frequency" :   (float),    
            "filter" :      ('tbl'),    
            "median" :      (float),    
            "lowerq" :      (float),    
            "upperq" :      (float),    
            "min" :         (float),    
            "max" :         (float),    
            "span" :        ('tbl'),    
            "rename" :      ('tbl'),    
            "sort" :        ('tbl'),    
            "sortcol":      ([]),       
            "round":        ('tbl'),    
            "roundcol":     ([]),       
            "keys":         ([]),       
            "length":       (int),      
            "append":       ('tbl'),    
            "remove":       ('tbl'),    
            "mutate":       ('tbl'),    
            "variance":     (float),    
            "stddev":       (float)
        }

    # For atomic terms, we identify the type of a standalone token, or a leaf in the tree
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
        if token.type == 'TYPE_TABLE' or token.type == 'tbl':
            return 'tbl'
        if token.type == 'NA':
            return na_type
        raise Exception(f"unknown type '{token.type}'")

 # --- Check program ---
    def check_p(self, c):
        print(c)
        # Build ftable
        self.build_ft(c, self.vtable, self.RL)

        for statement in c.children:
            self.check(statement, self.vtable, self.RL)

        print("type_checker ftable:", self.ftable)
        print("type_checker vtable:", self.vtable)

    def build_ft(self, c, env, RL):
        for child in c.children:
            if isinstance(child, Tree) and (child.data == 'func_def' or child.data == 'func_def_ret'):
                # TODO Tilføj child.data for returns og uden

                # Signature holds a list of elements: a tuple of input type, parameter types and the return type
                func_id, signature = self.get_fun(child, env, RL)
                
                if func_id in self.ftable:
                    raise Exception(f"Semantic Error: Definition '{func_id}' already exists")
                
                # Functions are added to the global ftable.
                self.ftable[func_id] = signature

    def build_vt(self, node, env, RL):
        #vtable = env.copy()
        vtable = copy.deepcopy(env)
    
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
        
    def check(self, node, env, RL):
        """
        Checks to see if...

        Args:
            one: does this

        Returns:
            
        """

        if isinstance(node, Token):
            return self.read_token(node, env)
        
        method_name = f'check_{node.data}'
        check_method = getattr(self, method_name, self.check_unknown)
        return check_method(node, env, RL)

    
    # check method to fall back on, if the given node is unknown
    def check_unknown(self, node, env, RL):
        raise Exception(f"No handler for node type: '{node.data}'")

    # --- directory --- # Rerouting, making similar checks re-use relevant methods
    def check_add(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_sub(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_mod(self, node, env, RL):     return self.check_additive(node, env, RL)
    def check_mult(self, node, env, RL):    return self.check_additive(node, env, RL)
    def check_exp(self, node, env, RL):     return self.check_additive(node, env, RL)

    def check_less(self, node, env, RL):    return self.check_comparison(node, env, RL)
    def check_greater(self, node, env, RL): return self.check_comparison(node, env, RL)
    def check_leq(self, node, env, RL):     return self.check_comparison(node, env, RL)
    def check_geq(self, node, env, RL):     return self.check_comparison(node, env, RL)
    def check_neq(self, node, env, RL):     return self.check_comparison(node, env, RL)
    def check_equal(self, node, env, RL):   return self.check_comparison(node, env, RL)

    def check_or(self, node, env, RL):      return self.check_logical(node, env, RL)
    def check_and(self, node, env, RL):     return self.check_logical(node, env, RL)

    def check_func_def(self, node, env, RL):     return self.check_f(node, env, RL)
    def check_func_def_ret(self, node, env, RL): return self.check_f(node, env, RL)

    def check_then(self, node, env, RL):    return self.check_if_cases(node, env, RL)
    def check_else(self, node, env, RL):    return self.check_if_cases(node, env, RL)
    
    # --- check implements ---
    def check_IDENT(self, node, env):
        print("Node:", node)
        print("Env", env)
        if (node.value not in env):
            raise Exception(f'{node.value} not defined')
        else: 
            return env[node.value]

    
    def check_assign(self, node, env, RL):
        # Validates assignment operations during type checking
        
        left = node.children[0]
        right = node.children[1]

        # When trying to assign a table to an identifier, we forego ll. 150 and on
        #   This is because TODO
        if isinstance(right, Tree) and right.data == "table":
            self.check_table(right, env, RL, table_id=left.value)
            return

        t1 = self.check(right, env, RL)
        
        # Do not assign an ident, that has no value and therefore no type
        if (t1 == None or t1 is na_type):
            raise Exception(f'Cannot assign variable {left.value} as void or NA')

        # If not already in global vtable, place it there
        if (left.value not in env):
           env[left.value] = t1
        # Else, check to see if it exists in some local vtable
        elif (env is self.vtable): # "is" and not "==" since we need to check if the object is different and not the values that is inside
            # Furthermore, if the existing type does not match the one presently attempted assigned, raise exception
            if not (isinstance(env[left.value], dict) and t1 == 'tbl') and env[left.value] != t1:
                raise Exception(f'{left.value} is of type {env[left.value]} and cannot be declared as type {t1}')
            #if (env[left.value] != t1): 
            #    raise Exception(f'{left.value} is of type {env[left.value]} and cannot be declared as type {t1}')  
        # Else, the variable already exists in the global environment, and the type is changed as given
        else:
            env[left.value] = t1
    
    def check_additive(self, node, env, RL):
        # Validated assignments classified as additive, all of which are treated the same
        
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        # Check if t1 and t2 are able to be processed in an additive expression (must be int or float)
        if self.numeric_compatible(t1,t2):
            return self.infer_numeric_type(t1,t2)
        # In case one or both are neither int nor float, raise exception
        else:
            raise Exception(f'Values {left.value} and {right.value} must both be of type int or float')

    def check_div(self, node, env, RL):
        # Validates division operations

        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        # If both arguments are of the number types, return float, as dvision with ints does not ensure int results
        if self.numeric_compatible(t1,t2):
            return float
        else: # Otherswise, raise exception
            raise Exception(f'Values {left.value} and {right.value} must both be of type int or float')
        
    def check_comparison(self, node, env, RL):
        # Validates statements classified as comparative, all of which are treated the same
        
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)

        # Check if t1 and t2 are comparison compatible meaning atleast one is either float, int or string. The other can optionally be NA
        if self.comparison_compatible(t1,t2):
            return bool
        else: # Otherwise, raise exception
            raise Exception(f'Values {left.value} and {right.value} must both be of type int or float, or only string')

    def check_logical(self, node, env, RL):
        # Validates logical statements, all of which are treated the same
        
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(left, env, RL)
        t2 = self.check(right, env, RL)
        
        # Ensure that both argumentss are of type bool, otherwise, raise exception
        if (t1 == bool and t2 == bool):
            return bool
        elif (t1 is na_type and t2 == bool):
            return bool
        elif (t1 == bool and t2 == t1 is na_type):
            return bool
        else:
            raise Exception(f'Values {left.value} and {right.value} must be of type bool')        

    def comparison_compatible(self, t1, t2):
        # Check if both expressions are NA. If so determining type is ambigious an NA doesn't have a real type
        if t1 is na_type and t2 is na_type:
            return False
        
        # Check that either both expressions are float/int, or at least one
        numeric = (int, float)
        return ((t1 in numeric and t2 in numeric) or 
                (t1 is str and t2 is str) or
                (t1 is str and t2 is na_type) or
                (t1 is na_type and t2 is str) or
                (t1 is na_type and t2 in numeric) or 
                (t2 is na_type and t1 in numeric))
    
    def check_not(self, node, env, RL):
        # Validates the use of the "not" operator

        t1 = self.check(node.children[0], env, RL)

        # The statements to be negated, must be a bool, otherwise, raise exception
        if (t1 != bool): 
            raise Exception(f'To use the "not"-operator, {node.children[0]} must be a bool')
        return bool

    def check_neg(self, node, env, RL):
        # Validates the use of "-" to negate some variable or value

        t1 = self.check(node.children[0], env, RL)

        # If t1 is a number, it remains the same number type, otherwise, raise exception
        if t1 == int:
            return int
        elif t1 == float:
            return float
        else:
            raise Exception(f'{node.children[0]} must be of type int or float to negate the value')

    def check_array(self, node, env, RL):
        # Validates an element of type array

        # If the array has no contents, raise exception, saying we cannot yet evaluate the type, as there is nothing to evaluate
        if len(node.children) == 0:
            raise Exception("No type for an empty array")

        # Otherwise, moving on, store the type of the very first element in the array
        type_of_array = self.first_valid_type(node.children, env, RL)
        array_check_count = 0

        # Compare the first element to the rest, ensuring they are all the same as the first or NA
        if (all((self.check(x, env, RL) == type_of_array) or (self.check(x, env, RL) == na_type) and (array_check_count := array_check_count + 1) for x in node.children)):
            return [type_of_array] # return as array of type T - [T], NOT simply T
        # Otherwise, raise exception
        else: 
            #raise Exception("Not all elems of array are of the same type")
            raise Exception(f'Not all elements of array are of the same type - Element {array_check_count} is not of type {type_of_array}')

    def check_array_type(self, node, env, RL):
        # Validates cases of using one of the datatypes as an array variant
        #   For example, an array of integers: [int]

        # Run check to find the type for the array, returning that type as an array type, [T]
        array_type = self.check(node.children[0], env, RL)
        return [array_type]
        
    def check_index(self, node, env, RL):
        # Validates to ensure, that indexing into an array is done using only integers

        type_id = self.check(node.children[0], env, RL) # find the type for the array itself
        type_idx = self.check(node.children[1], env, RL) # find the type for the indexing nr

        # If indexing was done using an int, proceed with the type of the array, otherwise, raise exception
        if type_idx == int:
            return type_id[0]
        else: 
            raise Exception(f'Did not parse an integer for array indexing')

    def check_column_sapling(self, node, env, RL):
        # This check method serves as a helper-check for check_table
        #   Enters a column, to return the array/children of that column
        return node.children
  
    def check_table(self, node, env, RL, table_id = None):
        # If the table name is not parsed on method call, find it through the node
        if table_id == None:
            table_id = node.data

        for col in node.children:
            c_id = col.children[0] # Get the name of the current column
            arr = col.children[1] # Get the array related to that same column name 
            
            check_arr = self.check(arr, env, RL) # Get the type of the array held in current column

            # Create a custom tree structure to assign a custom type to a custom variable in our environment
            col = Tree("column_sapling", check_arr)

            # Turn the use of dot-notation into an identifier that the array can be assigned to
            token = Token('IDENT', f'{table_id} {c_id.value}')
            stmt = Tree("assign", [token, col])
            self.check(stmt, env, RL)

        # Ending the check_function with setting the id == "tbl" since all tables would be of type "tbl"
        token = Token('IDENT', f'{table_id}')
        tbl_token = Token('TYPE_TABLE', 'tbl')
        S = Tree("assign", [token, tbl_token])
        self.check(S, env, RL)    
    
    def check_f(self, node, env, RL):
        # "check_f" is used to check the declaration of a function and its body
        paramsnode = node.children[1] # A node containing all the parameters of the function
        # If the amount of children of a function node is 4, that means it has a return type
        if len(node.children) == 4: 
            return_type = self.check(node.children[2], env, RL)
            RL["R"] = return_type # Save the return type in the functions "RL" enviroment
            body = node.children[3]
        else: # Goes through if the function does not have a return type
            return_type = None # RL["R"] is already "None" to begin with so no reason to change it here
            body = node.children[2]
        
        # Builds the local variable enviroment for the function with the formal parameters
        # Takes a copy of the current variable enviroment at the time of the declaration
        vtable_local = self.build_vt(paramsnode, env, RL)

        if len(body.children) == 0:
            raise Exception("function can't have an empty body")
            
        self.check(body, vtable_local, RL) # Checks the body of the function with the local variable enviroment
        RL["R"] = None
    

    def check_body(self, node, env, RL):
        # "check_body" is used for checking the body of a function
        # Simply check each child of the node "body"
        for child in node.children:
            self.check(child, env, RL)
        
    def check_return(self, node, env, RL):
        t1 = self.check(node.children[0], env, RL) # Check the type of the expression after "return"

        # Check if the return type matches with "R" in enviroment "RL"
        # This enviroment tracks if we are currently inside a function and what the function is supposed to return
        if (t1 != RL["R"] and t1 is not na_type):
            raise Exception(f'{t1} doesnt match with function return type')

        return t1
    
    def check_call(self, node, env, RL):
        f_id = node.children[0] # Name of the function called

        if(node.children[0] == 'print'):
            return

        if (f_id not in self.ftable):
            raise Exception(f'Function {f_id} not previously defined')


        formal_params, return_type = self.ftable[f_id] # Get info on current function
        actual_params = node.children[1:]

        if len(formal_params) != len(actual_params):
            raise Exception("Amount of formal parameters do not match actual parameters")

        # For every parameter, check if formal and actual are of the same type
        for i in range(len(formal_params)):
            t1 = self.check(actual_params[i], env, RL)
            t2 = formal_params[i]
            
            if t1 != t2 and t1 is not na_type:
                raise Exception(f'Formal and actual parameters of function {f_id} not of same type')
            
        return return_type
    
    def check_dot(self, node, env, RL):
        # The leftmost node of the children is the name of which variable the dot funtions is called upon
        #left = node.children[0]
        right = node.children[1].children[0]
        return_type = self.ptable[right] # Get formal info on current child
        return return_type # Return type if its an assignment
        # The rest of the children are the call node(s), that hold the predef. func. called and the params
        
#
    #    # Checking each predefined function
    #    for child in right:
    #        child_left = child.children[0] # Name of predefined function called
    #        actual_params = child.children[1:] # Actual parameters of predefined function
    #        if child_left not in self.ptable: # Check if the function is in the enviroment of predefined functions
    #            raise Exception(f'{child_left} is not a predefined function')
    #        
    #        input_type, formal_params, return_type = self.ptable[child_left] # Get formal info on current child
#
    #        if len(formal_params) != len(actual_params):
    #            raise Exception("Amount of formal parameters do not match actual parameters")
#
#
    #    return return_type # Return type if its an assignment  
#
    def check_stop(self, node, env, RL):
        # Raises an exception if we aren't in a loop currently
        # This can be seen using the key "L" in the enviroment "RL"
        if RL["L"] == False:
            raise Exception(f'Cannot stop, not in loop')

    def check_if(self, node, env, RL):
        # Checks the boolean condition in the if-statement
        t1 = self.check(node.children[0], env, RL)

        # Raise exception if the condition is not a boolean
        if t1 != bool:
            raise Exception(f'{node.children[0]} is not a boolean expression')

        # Set the body of the if-statement to be everything after the conditional statement
        body = node.children[1:]

        for child in body:
            self.check(child, env, RL)

    def check_if_cases(self, node, env, RL):

        # The children of the if-statement in the tree are just the statements to be executed when a then/else goes through
        body = node.children
        
        for child in body:
            self.check(child, env, RL)

    def check_while(self, node, env, RL):

        # Check the boolean expression in the while statement
        t1 = self.check(node.children[0], env, RL)

        if t1 != bool:
            raise Exception(f'{node.children[0]} is not a boolean expression')

        body = node.children[1:]

        # Creates a new "scope" for the RL enviroment so that we allow for loops inside loops
        RL_new = RL.copy()
        RL_new["L"] = True

        # Check every statement in the body of the while loop
        for child in body:
            self.check(child, env, RL_new)
            
    def check_assign_index(self, node, env, RL):

        type_id = self.check(node.children[0], env, RL) # find the type for the array itself
        type_idx = self.check(node.children[1], env, RL) # find the type for the indexing nr
        type_ass = self.check(node.children[2], env, RL) # find the type for the assignment

        if type_idx != int:
            raise Exception(f'Did not parse an integer for array indexing')

        if type_id[0] != type_ass and type_ass is not na_type:
            raise Exception (f'Trying to assign {type_ass} to an array of type{type_id[0]}')
        
    '''Helper functions, Should probably be moved to another folder and imported later, or maybe not'''
    def numeric_compatible(self, t1, t2):
        # Check if both expressions are NA. If so determining type is ambigious an NA doesn't have a real type
        if t1 is na_type and t2 is na_type:
            return False
        
        # Check that either both expressions are float/int, or at least one
        numeric = (int, float)
        return ((t1 in numeric and t2 in numeric) or 
                (t1 is na_type and t2 in numeric) or 
                (t2 is na_type and t1 in numeric))
    

    def infer_numeric_type(self, t1, t2):
        # If either t1 or t2 is NA, resulting type should be the others expressions type
        if t1 is na_type:
            return t2
        if t2 is na_type:
            return t1
        # If both are floats, resulting type should be float
        if t1 == float or t2 == float:
            return float
        # else t1 and t2 must both be int, and the resulting type is int
        return int
    
    def first_valid_type(self, node, env, RL):
        for child in node:
            x = self.check(child, env, RL)
            if x is not na_type:
                return x
        raise Exception("Array cannot consist of only NA")