from tadpole.parsertransformer import MyTrans
from tadpole.utils.exceptions import *
from lark import UnexpectedToken
import os



# Transforms the parse tree into an AST using the class MyTrans and Larks transform method.
# Returns the transformed tree.
def transformtree(tree):
    return MyTrans().transform(tree)


# Function for opening a .tad file and returning the content as a string
def readfile(file_path):

    # Splits the file path after the last dot to check the extension
    split_up = os.path.splitext(file_path)
    file_extension = split_up[1]

    if file_extension != '.tad':
        raise WrongFileTypeError(f"Passed a {file_extension} file, ""expected a .tad file")
    
    # Tries to open a file and return the content as a string.
    # If the file doesn't exist, raise exception to be handled in main
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError as e:
        raise TadpoleFileError(f"File not found: {file_path}") 


# Function for lexing and parsing a string of code and returns a concrete parsetree.
# Raises syntax exception if code isn't written according to the grammar
def parse(parser, code):

    try:
        return parser.parse(code)
    except UnexpectedToken as e:
        raise TadpoleSyntaxError(
            f"Syntax error on line {e.line}\n"
            f"{e.get_context(code)}"
        ) 

