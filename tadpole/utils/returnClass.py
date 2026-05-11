# Custom exception for a "super return" which purpose it is to skip a stack of function calls, 
#   and return directly to anywhere in the call stack.
#   The value that is passed is the value that would normally be returned
class return_value(Exception):
    def __init__(self, value):
        self.value = value