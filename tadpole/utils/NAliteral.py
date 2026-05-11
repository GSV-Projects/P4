class NA_literal():
    # __repr__ makes it so that an instance of this class is printet as NA in the terminal, rather than object#02...
    def __repr__(self): 
        return "NA"

# The singleton instance of the class, which is imported, and used as the NA literal
NA = NA_literal()

# The NA type is used to create a psuedo type for NA literals. Which is useful when we need to distinguish between other
#   literals and the NA literal in the type_checker. We say it's a psuedo type, since no variables actually get this type.
class NA_type():
    pass
na_type = NA_type()