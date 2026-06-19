from lark import Tree, Token
from .utils.NAliteral import na_type
from .utils.exceptions import TypecheckerException
import copy



# Typechecker class which has the purpose of checking through a AST to make sure the typing is correct.
#   Should catch all compile time errors.
class Typechecker():
    # Initializing different environments to save variables in
    def __init__(self):
        self.vtable = {}
        self.ftable = {}
        self.RL = {
            "R" : None,
            "L" : False
        }
        # ptable is the table for predefined functions and consists of their return type
        self.ptable = { 
            "read":         ('tbl'),    
            "readfill":     ('tbl'),
            "replaceNA":    ('tbl'),    
            "rename" :      ('tbl'),    
            "append":       ('tbl'),    
            "remove":       ('tbl'),    
            "mutate":       ('tbl'),    
            "filterall" :   ('tbl'),
            "filtercol":    ('tbl'),
            "firstrow":     ('tbl'),
            "lastrow":      ('tbl'),
            "getrow":       ('tbl'),
            "sort" :        ('tbl'),    
            "round":        ('tbl'),    
            "sortcol":      ([]),     
            "roundcol":     ([]),       
            "getcol":       ([]),       
            "getfirst":     ([]),       
            "getlast":      ([]),       
            "keys":         ([]),       
            "length":       (int),      
            "head" :        ((int, float, str, bool)),
            "tail" :        ((int, float, str, bool)),
            "cell":        ((int, float, str, bool)),
            "mean" :        (float),      
            "sum" :         (float),    
            "frequency" :   (int),    
            "median" :      (float),    
            "lowerq" :      (float),    
            "upperq" :      (float),    
            "min" :         (float),    
            "max" :         (float),    
            "span" :        (float),    
            "variance":     (float),    
            "stddev":       (float)
        }

    # Auxiliary function to get line number in case of exception
    def get_pos(self, node):
        # Token has the attribute "line" - See Lark token documentation
        if isinstance(node, Token):
            return node.line

        # If its not a token but tree, go through tree until a token is found to get line
        if hasattr(node, "children"):
            for child in node.children:
                line = self.get_pos(child)
                if line is not None:
                    return line

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
        if token.type == 'TYPE_TABLE':
            return 'tbl'
        if token.type == 'NA':
            return na_type
        line = self.get_pos(token)
        raise TypecheckerException(f"Error on line {line} - Unknown type '{token.type}', must be either INT, FLOAT, STRING, FALSE, TRUE, NA or tbl")

 # --- Check program ---
    def check_p(self, c):
    
        # Go through program to build the ftable
        self.build_ft(c, self.vtable, self.RL)

        for statement in c.children:
            self.check(statement, self.vtable, self.RL)

        #print("type_checker ftable:", self.ftable)
        #print("type_checker vtable:", self.vtable)

    # To build the ftable we loop through the program to check for function declarations
    def build_ft(self, c, env, RL):
        for child in c.children:
            if isinstance(child, Tree) and (child.data == 'func_def' or child.data == 'func_def_ret'):

                # Signature holds a list of elements: a tuple of input type, parameter types and the return type
                func_id, signature = self.get_fun(child, env, RL)
                
                if func_id in self.ftable:
                    line = self.get_pos(child)
                    raise TypecheckerException(f"Error on line {line} - Definition '{func_id}' already exists")
                
                # Functions are added to the global ftable.
                self.ftable[func_id] = signature

    # build_vt creates a local environment for variables
    def build_vt(self, node, env, RL):
        vtable = copy.deepcopy(env)
    
        # Parameters are added to the local vtable.
        for child in node.children:
            vtable[child.children[1].value] = self.check(child.children[0],env, RL)
        return vtable

    # Function for extracting formel parameters, return type and function name
    def get_fun(self, node, env, RL):
        func_name = node.children[0].value
        paramsnode = node.children[1]
        # If the length of the AST node is four, there is a return type
        if len(node.children) == 4:
            return_type = self.check(node.children[2], env, RL)
        else:
            return_type = None

        params = []
        for x in paramsnode.children:
            params.append(self.check(x.children[0], env, RL))

        # Returns a function signature: (id, (t1, ..., tn), t)
        return func_name, (tuple(params), return_type)
        
    # check is a recursive function that delegates the typechecking of a node to its appropriate function
    def check(self, node, env, RL):
        # If the node is a token, we handle it seperatly
        if isinstance(node, Token):
            return self.read_token(node, env)
        
        # Accessing an arbitrary node
        method_name = f'check_{node.data}'
        # Uses the method name string to find the associated method in the current object to be called.
        #   Throws an error if it wasn't found.
        check_method = getattr(self, method_name, self.check_unknown)
        # Calling the needed function
        return check_method(node, env, RL)

    
    # check method to fall back on, if the given node is unknown
    def check_unknown(self, node, env, RL):
        line = self.get_pos(node)
        raise TypecheckerException(f'Error on line {line} - Unknown language construct "{node.data}"')

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
    
    # --- check implementations ---

    # Checking if an identifier exists in the specified environment
    def check_IDENT(self, node, env):
        if (node.value not in env):
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - {node.value} not defined')
        else: 
            return env[node.value]

    
    def check_assign(self, node, env, RL):
        # Validates assignment operations during type checking
        
        left = node.children[0]
        right = node.children[1]

        t1 = self.check(right, env, RL)
        
        # Do not assign an ident, that has no value and therefore no type
        if (t1 == None or t1 is na_type):
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Cannot assign variable {left.value} as void or NA. Only possible if another type is in the expression such as: x = 5 + NA;')

        # If not already in the local vtable, place it there (can be global)
        if (left.value not in env):
           env[left.value] = t1
        # Check if the environment is the global environment.
        #   If it is we can't reassign a variable to a new type.
        elif (env is self.vtable): 
            # M.I.S.
            #if not (isinstance(env[left.value], dict) and t1 == 'tbl') and env[left.value] != t1:
            #    raise Exception(f'{left.value} is of type {env[left.value]} and cannot be declared as type {t1}')
            if (env[left.value] != t1): 
                line = self.get_pos(node)
                raise TypecheckerException(f'Error on line {line} - {left.value} is of type {env[left.value]} and cannot be declared as type {t1}')  
        # Else, the environment is local and the reassignment of a type is approved
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
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Values {left.value} and {right.value} must both be of type int or float')

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
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Values {left.value} and {right.value} must both be of type int or float')
        
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
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Values {left.value} and {right.value} must both be of type int or float, or only string')

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
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Values {left.value} and {right.value} must be of type bool')        

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
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - To use the "not"-operator, {node.children[0]} must be a bool')
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
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - {node.children[0]} must be of type int or float to negate the value')

    def check_array(self, node, env, RL):
        # Validates an element of type array

        # If the array has no contents, raise exception, saying we cannot yet evaluate the type, as there is nothing to evaluate
        if len(node.children) == 0:  
            raise TypecheckerException(f"No type for an empty array")

        # Otherwise, moving on, store the type of the very first element in the array
        type_of_array = self.first_valid_type(node.children, env, RL)
        array_check_count = 0

        # Compare the first element to the rest, ensuring they are all the same as the first or NA
        result = True
        for x in node.children:
            t = self.check(x, env, RL)
            if t == type_of_array or t == na_type:
                array_check_count += 1
            else:
                array_check_count += 1
                result = False
        if result:
            # return as array of type [T], NOT simply T
            return [type_of_array] 
        # Otherwise, raise exception
        else: 
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Not all elements of array are of the same type! Element {node.children[array_check_count-1]} is not of type {type_of_array}')

    def check_array_type(self, node, env, RL):
        # Validates cases of using one of the datatypes as an array variant.
        #   For example, an array of integers: [int].

        # Run check to find the type for the array, returning that type as an array type, [T]
        array_type = self.check(node.children[0], env, RL)
        return [array_type]
        
    def check_index(self, node, env, RL):
        # Validates to ensure, that indexing into an array is done using only integers

        # Find the type for the array itself
        type_id = self.check(node.children[0], env, RL) 

        # Find the type for the indexing nr
        type_idx = self.check(node.children[1], env, RL) 

        # If indexing was done using an int, proceed with the type of the array, otherwise, raise exception
        if type_idx == int:
            return type_id[0]
        else: 
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Index must be an integer to index the array')

  
    def check_table(self, node, env, RL):
        # Check_table is used to check that each column only contains a single type

        # Loops through each column node, and checks the array of each column
        #   If no exceptions are thrown it means all arrays were typed correctly, and we can return 'tbl' as the type
        for child in node.children:
            self.check(child.children[1], env, RL)
        
        return 'tbl'

    
    def check_f(self, node, env, RL):
        # "check_f" is used to check the declaration of a function and its body

        # A node containing all the parameters of the function
        paramsnode = node.children[1]

        # If the amount of children of a function node is 4, that means it has a return type
        if len(node.children) == 4: 
            return_type = self.check(node.children[2], env, RL)
            # Save the return type in the functions "RL" enviroment
            RL["R"] = return_type 
            body = node.children[3]
        # Goes through if the function does not have a return type
        else: 
            # RL["R"] is already "None" to begin with so no reason to change it here
            return_type = None 
            body = node.children[2]
        
        # Builds the local variable enviroment for the function with the formal parameters
        # Takes a copy of the current variable enviroment at the time of the declaration
        vtable_local = self.build_vt(paramsnode, env, RL)

        if len(body.children) == 0:
            line = self.get_pos(node)
            raise TypecheckerException(f"Error on line {line} - Function can't have an empty body")
            
        self.check(body, vtable_local, RL) # Checks the body of the function with the local variable enviroment
        RL["R"] = None
    

    def check_body(self, node, env, RL):
        # "check_body" is used for checking the body of a function
        # Simply check each child of the node "body"
        for child in node.children:
            self.check(child, env, RL)
        
    def check_return(self, node, env, RL):
        # Check the type of the expression after "return"
        t1 = self.check(node.children[0], env, RL) 

        # This check makes sure that we are inside a non-void function before trying to return
        if (RL["R"] == None):
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Not possible to use return outside of a function or inside of a void function')

        # Check if the return type matches with "R" in enviroment "RL".
        #   This enviroment tracks if we are currently inside a function and what the function is supposed to return.
        if (t1 != RL["R"] and t1 is not na_type):
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - The return statement returns value of type {t1.__name__}, but the function expects to return value of type {RL["R"].__name__}')
        return t1
    
    def check_call(self, node, env, RL):
        f_id = node.children[0] 

        # print is a reserved function name so we just return if we call print
        if(node.children[0] == 'print'):
            return

        if (f_id not in self.ftable):
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Function {f_id} is not declared')

        # Get info on current function
        formal_params, return_type = self.ftable[f_id] 
        actual_params = node.children[1:]

        if len(formal_params) != len(actual_params):
            line = self.get_pos(node)
            raise TypecheckerException(f"Error on line {line} - Amount of function parameters do not match the amount of passed parameters to the function")

        # For every parameter, check if formal and actual are of the same type
        for i in range(len(formal_params)):
            t1 = self.check(actual_params[i], env, RL)
            t2 = formal_params[i]
            
            if t1 != t2 and t1 is not na_type:
                line = self.get_pos(node)
                raise TypecheckerException(f'Error on line {line} - Formal and actual parameters of function "{f_id}" not of same type. Actual: {t1.__name__}, Formal: {t2.__name__}')
            
        return return_type
    
    # For predefined functions we only want the return type of said function so we can store it in a variable
    def check_dot(self, node, env, RL):
        # We want to extract the name of the called function so we can find the return type in the ptable
        right = node.children[1].children[0]
        left = node.children[0]

        if env[left.value] != 'tbl':
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - "{left.value}" is of type {self.vtable[left.value]}, must be a table of type: tbl')

        # Get formal info on current child and return it
        return_type = self.ptable[right] 
        return return_type 
 

    def check_stop(self, node, env, RL):
        # Raises an exception if we aren't in a loop currently
        # This can be seen using the key "L" in the enviroment "RL"
        if RL["L"] == False:
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Cannot use stop outside a loop')

    def check_if(self, node, env, RL):
        # Checks the boolean condition in the if-statement
        t1 = self.check(node.children[0], env, RL)

        # Raise exception if the condition is not a boolean
        if t1 != bool:
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - {node.children[0]} must be a boolean expression')

        # Set the body of the if-statement to be everything after the conditional statement
        body = node.children[1:]

        for child in body:
            self.check(child, env, RL)

    # If cases handle both then and else since we just need to check every statement anyways
    def check_if_cases(self, node, env, RL):

        # The children of the if-statement in the tree are just the statements to be executed when a then/else goes through
        body = node.children
        
        for child in body:
            self.check(child, env, RL)

    def check_while(self, node, env, RL):

        # Check the boolean expression in the while statement
        t1 = self.check(node.children[0], env, RL)

        if t1 != bool:
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - {node.children[0]} must be a boolean expression')

        body = node.children[1:]

        # Creates a new "scope" for the RL enviroment so that we allow for loops inside loops
        RL_new = RL.copy()
        RL_new["L"] = True

        # Check every statement in the body of the while loop
        for child in body:
            self.check(child, env, RL_new)
            
    # When doing assignment to a position in an array we need to handle it separately
    def check_assign_index(self, node, env, RL):

        # find the type for the array itself
        type_id = self.check(node.children[0], env, RL) 
        # find the type for the indexing nr
        type_idx = self.check(node.children[1], env, RL) 
        # find the type for the assignment
        type_ass = self.check(node.children[2], env, RL) 

        if type_idx != int:
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Index must be an integer to index the array')

        if type_id[0] != type_ass and type_ass is not na_type:
            line = self.get_pos(node)
            raise TypecheckerException(f'Error on line {line} - Trying to assign {type_ass} to an array of type {type_id[0]}')
        
    # Helper functions for NA values
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
    
    # For an array, we need to find the first non-NA type
    def first_valid_type(self, node, env, RL):
        for child in node:
            x = self.check(child, env, RL)
            if x is not na_type:
                return x
        raise TypecheckerException("Array cannot consist of only NA values")
