from tadpole.grammar import grammar
import pytest
from lark import Lark
from tadpole.parsertransformer import MyTrans
from tadpole.evaluator import Evaluator
from tadpole.type_checker import Typechecker
from tadpole.table import Table

# The integration test are meant to test that all the larger units which make up the interpreter work together as excepted.
#   These larger unit can be seens as
#       * The parse generator and lexor
#       * The AST transformer
#       * The type checker
#       * The evaluator
#   The integration test are designed to test a larger piece of code, using a variety of different statements

parser = Lark(grammar, parser="lalr", strict=True)

def transformtree(tree):
        return MyTrans().transform(tree)


def parse_to_ast(code):
    parsetree = parser.parse(code)
    return transformtree(parsetree)

# A longer program using most of the statement possible in the language
def test_long_program():
    # Setup
    code = '''
    a = 200.0;
    function divide(float a, int i) returns float{
        if (a < 10) then {
            return a;
        }

        return divide(a / i ,i);
    }

    b = divide(a, 2);
    
    while (true) do {
        if (b < 0) then { stop; }
    b = b - 4;
    a = a^b;
    }

    '''
    ast = parse_to_ast(code)
    typechecker = Typechecker()
    typechecker.check_p(ast)
    evaluator = Evaluator()
    evaluator.PEval(ast)


    # Assert 
    a_result = evaluator.env_v["a"] == pytest.approx(0.000000000870350918695717)
    b_result = evaluator.env_v["b"] == -1.75

    assert (a_result and b_result)
    
# An integration test, that tests a recursive program executes with the expected result
def test_recursion():
    # Setup
    code = '''
    function isEven(int n) returns bool {
        if (n == 0) then { return true; }
        return isOdd(n - 1);
    }

    function isOdd(int n) returns bool {
        if (n == 0) then { return false; }
        return isEven(n - 1);
    }

    ans = isEven(10);
    '''
    ast = parse_to_ast(code)
    typechecker = Typechecker()
    typechecker.check_p(ast)
    evaluator = Evaluator()
    evaluator.PEval(ast)


    # Assert 
    a_result = typechecker.vtable["ans"] == bool 
    b_result = evaluator.env_v["ans"] == True

    assert (a_result and b_result)


def test_functions_and_tables():
    code = '''
    function myfunc() returns tbl {
                mytab = {
                col1 : [1,2,3];
                col2 : ["one", "two", "three"];
                };
                return mytab;
            }

            a = myfunc();
'''

    ast = parse_to_ast(code)
    typechecker = Typechecker()
    typechecker.check_p(ast)
    evaluator = Evaluator()
    evaluator.PEval(ast)

    type_result = typechecker.vtable["a"] == 'tbl'
    value_result = evaluator.env_v["a"].columns == {'col1': [1, 2, 3], 'col2': ['one', 'two', 'three']}

    assert (type_result and value_result)