from tadpole.parsertransformer import MyTrans
from tadpole.utils.exceptions import *
from lark import UnexpectedToken
import os



# Transforms the parse tree into an AST using the class MyTrans and Larks transform method.
# returns the transformed tree.
def transformtree(tree):
    return MyTrans().transform(tree)

def readfile(file_path):

    # Splits the file path after the last dot to check the extension
    split_up = os.path.splitext(file_path)
    file_extension = split_up[1]

    if file_extension != '.tad':
        raise WrongFileTypeError(f"Passed a {file_extension} file, ""expected a .tad file")
    
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError as e:
        raise TadpoleFileError(f"File not found: {file_path}")


def parse(parser, code):

    try:
        return parser.parse(code)
    except UnexpectedToken as e:
        raise TadpoleSyntaxError(
            f"Syntax error on line {e.line}\n"
            f"{e.get_context(code)}"
        ) 

