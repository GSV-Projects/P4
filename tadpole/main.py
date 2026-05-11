from tadpole.grammar import grammar
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.evaluator import Evaluator
from tadpole.type_checker import Typechecker

code = """
function foo(int a, int b) returns int {
    return 1;
}
x = 10;

y = [1, 2, 3];
h = y[2];

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