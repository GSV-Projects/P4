
from tadpole.grammar import grammar
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.interpreter import Interpreter
from tadpole.type_checker import Typechecker



code = """
a = 3;
"""

def transformtree(tree):
    return MyTrans().transform(tree)

parser = Lark(grammar, parser="lalr", strict=True)

parsetree = parser.parse(code)
ast = transformtree(parsetree)

print("Parse \n", parsetree.pretty())
print("AST \n", ast.pretty())

Typechecker().check_p(ast)
fortolker = Interpreter()
fortolker.PEval(ast)