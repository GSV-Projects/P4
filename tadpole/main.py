from tadpole.grammar import grammar
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.evaluator import Evaluator
from tadpole.type_checker import Typechecker

code = """
string1 = "test";
string2 = "test";
string3 = "test1";

isSame = string1 == string2;
notSame = string1 /= string3;
lessThan = string2 < string3;

"""

def transformtree(tree):
    return MyTrans().transform(tree)

parser = Lark(grammar, parser="lalr", strict=True)

parsetree = parser.parse(code)
ast = transformtree(parsetree)

print("Parse \n", parsetree.pretty())
print("AST \n", ast.pretty())

Typechecker().check_p(ast)
evaluator = Evaluator()
evaluator.PEval(ast)