from tadpole.grammar import grammar
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.evaluator import Evaluator
from tadpole.type_checker import Typechecker

code = """
mytab = {
col1 : [1,3,5,7];
col2 : [2.2, 4.4, 6.6, 8.8];
col3 : ["one", "two", "three", "four"];
col4 : [true, false, false, true];
};

test = mytab.frequency("col1", 1);

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