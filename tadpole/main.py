from tadpole.grammar import grammar
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.evaluator import Evaluator
from tadpole.type_checker import Typechecker


# The code to be executed:
code = """
mytab = {};

mytab = mytab.read("https://github.com/GSV-Projects/P4/blob/tabletest/tadpole/Simple_example/read_test.csv");


tab = {col : ["a","b"];};


"""


# Transforms the parse tree into an AST using the class MyTrans and Larks transform method.
# returns the transformed tree.
def transformtree(tree):
    return MyTrans().transform(tree)

# Defines the grammar as parser
parser = Lark(grammar, parser="lalr", strict=True)

# Parses the grammar through Larks parser and lexer
parsetree = parser.parse(code)

# Transforms the parse tree to an AST
ast = transformtree(parsetree)

# Prints the AST
print("AST \n", ast.pretty())

# AST is parsed through the typechecker
Typechecker().check_p(ast)

# Interpreter is defined as the class evaluator
evaluator = Evaluator()

# The AST is parsed through the interpreter
evaluator.PEval(ast)