
from tadpole.grammar import grammar
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.interpreter import Interpreter
from tadpole.type_checker import Typechecker



code = """
    function factorial(int n) returns int {
        if (n <= 1) then { return 1; }
        return n * factorial(n - 1);
    }

    result = factorial(5);
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