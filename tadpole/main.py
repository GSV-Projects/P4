from tadpole.grammar import grammar
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.evaluator import Evaluator
from tadpole.type_checker import Typechecker
from lark import UnexpectedToken
import sys
import os

def main():
    # --- The code to be executed ---

    # Takes the first argument when running the interpreter
    file_path = sys.argv[1]

    with open(file_path, 'r') as file:
        # Splits the file path after the last dot to check the extension
        split_tup = os.path.splitext(file_path)
        file_extension = split_tup[1]

        if file_extension != '.tad':
            #raise WrongFileType
            print("wrong file type, need .tad")
            exit()

        # Reads the .tad file as a string
        code = file.read()


    # --- Parsing and lexing ---

    # Transforms the parse tree into an AST using the class MyTrans and Larks transform method.
    # returns the transformed tree.
    def transformtree(tree):
        return MyTrans().transform(tree)

    # Defines the grammar as parser
    parser = Lark(grammar, parser="lalr", strict=True)
        

    # Parses the grammar through Larks parser and lexer
    try:
        parsetree = parser.parse(code)
    except UnexpectedToken as e:
        # Exception for syntax error in the source code
        print("Unexpected token on line:", e.line, "at position", e.pos_in_stream, "in token stream")
        print(e.get_context(code))
        exit()

    # Transforms the parse tree to an AST
    ast = transformtree(parsetree)


    # --- Typechecking and evaluation ---

    # Prints the AST
    #print("AST \n", ast.pretty())

    # AST is parsed through the typechecker
    Typechecker().check_p(ast)

    # Interpreter is defined as the class evaluator
    evaluator = Evaluator()

    # The AST is parsed through the interpreter
    evaluator.PEval(ast)