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
    #print("AST \n", ast.pretty())

    # AST is parsed through the typechecker
    Typechecker().check_p(ast)

    # Interpreter is defined as the class evaluator
    evaluator = Evaluator()

    # The AST is parsed through the interpreter
    evaluator.PEval(ast)


# This function is both called from the toml build config and when running it using python
def main():
    try:
        run()

    except TadpoleSyntaxError as e:
        print(e)
        sys.exit(1)

    except TadpoleFileError as e:
        print(e)
        sys.exit(1)

    except WrongFileTypeError as e:
        print(e)
        sys.exit(1)

    except TadpoleException as e:
        print(f"Tadpole Error\n{e}")
        sys.exit(1)

    except Exception as e:
        print(f"python exception\n{e}")
        sys.exit(1)


# When running the program using python
if __name__=="__main__":
    main()