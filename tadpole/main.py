from tadpole.grammar import grammar
from lark import Lark
from tadpole.utils.exceptions import *
from tadpole.evaluator import Evaluator
from tadpole.type_checker import Typechecker
from tadpole.utils.mainUtils import *
import sys


def run():
    # --- The code to be executed ---

    # Takes the first argument when running the interpreter
    file_path = sys.argv[1]

    # Reads source code file and returns it as a string
    code = readfile(file_path)


    # --- Parsing and lexing ---


    # Defines the grammar as parser
    parser = Lark(grammar, parser="lalr", strict=True)
        
    # Parses the grammar through Larks parser and lexer
    parsetree = parse(parser, code)


    # Transforms the parse tree to an AST
    ast = transformtree(parsetree)

    # --- Typechecking and evaluation ---

    # Prints the AST
    print("AST: \n", ast.pretty())
    print("output: \n")

    # AST is parsed through the typechecker
    Typechecker().check_p(ast)

    # evaluator is defined as the class Evaluator
    evaluator = Evaluator()

    # The AST is parsed through the evaluator
    evaluator.PEval(ast)


# Entrypoint to the program when running the interpreter with the toml config
def main():
    try:
        run()

    # Catching syntax errors
    except TadpoleSyntaxError as e:
        print(e)
        sys.exit(1)

    # Catching exception if file can't be found
    except TadpoleFileError as e:
        print(e)
        sys.exit(1)

    # Catching exception if file is not of type .tad
    except WrongFileTypeError as e:
        print(e)
        sys.exit(1)

    # Catching other Tadpole exceptions
    except TadpoleException as e:
        print(f"Tadpole Error\n{e}")
        sys.exit(1)

    # Catching other exceptions, should never run
    except Exception as e:
        print(f"python exception\n{e}")
        sys.exit(1)


# Entrypoint to the program when running the interpreter with python or the tasks.json config
if __name__=="__main__":
    main()