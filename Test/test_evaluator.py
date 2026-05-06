from lark import Tree, Token
from tadpole.interpreter import Interpreter
from tadpole.utils.NAliteral import NA
import pytest


## Aritmetic test ##
# test normal integer addition
def test_add_int():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('add', [Tree('add', [Token('INT', '5'), Token('INT', '10')]), Token('INT', '7')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 5 + 10 + 7;
    '''

    # Expected output
    assert evaluator.env_v["a"] == 22

# test addition using both int and float
def test_add_mix():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('add', [Tree('add', [Token('FLOAT', '6.34'), Token('FLOAT', '7.5')]), Token('INT', '7')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 6.34 + 7.5 + 7;
    '''

    # Expected output
    assert evaluator.env_v["a"] == 20.84

# test that expressions follow the precidence rules for numbers
def test_precidence_num():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('div', [Tree('sub', [Tree('add', [Token('INT', '2'), Token('INT', '2')]), Tree('mult', [Token('INT', '5'), Token('INT', '4')])]), Token('INT', '2')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = ((2+2)-5*4)/2;
    '''

    # Expected output
    assert evaluator.env_v["a"] == -8

# test that expressions follow the precidence rules for booleans
def test_precidence_logic():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('or', [Tree('and', [Token('TRUE', 'true'), Tree('not', [Token('TRUE', 'true')])]), Token('TRUE', 'true')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = true and not true or true;
    '''

    # Expected output
    assert evaluator.env_v["a"] == True

# test that zero division raises an exception
def test_zerodivision():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('div', [Token('INT', '5'), Token('INT', '0')])])])
    evaluator = Interpreter()
    with pytest.raises(Exception) as excinfo:
        evaluator.PEval(syntax_tree)


    # What the syntax_tree represents
    '''
    a = 5/0;
    '''
    
    # Expected output
    assert "Division by zero not allowed!" in str(excinfo.value)

# test the zero modulo raises an exception
def test_zeromodulo():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('mod', [Token('INT', '5'), Token('INT', '0')])])])
    evaluator = Interpreter()
    with pytest.raises(Exception) as excinfo:
        evaluator.PEval(syntax_tree)


    # What the syntax_tree represents
    '''
    a = 5 mod 0;
    '''
    # Expected output
    assert "Modulo by zero is undefined" in str(excinfo.value)

# test that exponentials still work even when the exponent is very large
def test_bigexponent():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('exp', [Token('INT', '2'), Token('INT', '200')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 2^200;
    '''

    # Expected output
    assert evaluator.env_v["a"] == 1606938044258990275541962092341162602522202993782792835301376


## Test with NA ##
# test that NA is properly propagated in "or" expressions
def test_na_propagation_boolean_or():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('or', [Token('NA', 'NA'), Token('TRUE', 'true')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = NA or true;
    '''

    # Expected output
    assert evaluator.env_v["a"] is NA

# test that NA is properly propagated in "and" expressions
def test_na_propagation_boolean_and():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('and', [Token('NA', 'NA'), Token('FALSE', 'false')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = NA and false;
    '''

    # Expected output
    assert evaluator.env_v["a"] is NA

# test that NA is properly propagated in aritmetic expressions
def test_napropagation_aritmetic():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('add', [Token('NA', 'NA'), Tree('div', [Tree('mult', [Token('INT', '5'), Token('INT', '2')]), Token('NA', 'NA')])])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = NA + 5 * 2 / NA;
    '''

    # Expected output
    assert evaluator.env_v["a"] is NA

# that that NA can be used as an actual parameter
def test_napropagation_parameter_parsing():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('func_def_ret', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_INT', 'int'), Token('IDENT', 'a')])]), Token('TYPE_INT', 'int'), Tree('return', [Token('IDENT', 'a')])]), Tree('assign', [Token('IDENT', 'a'), Tree('call', [Token('IDENT', 'myfunc'), Token('NA', 'NA')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    #What the syntax_tree represents
    ''' 
    function myfunc(int a) returns int {
        return a;
    }

    a = myfunc(NA);
    '''
    # Expected output
    assert evaluator.env_v["a"] is NA

## Test with functions ##
# test that functions return the excepted value
def test_function_with_return():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('func_def_ret', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_INT', 'int'), Token('IDENT', 'a')])]), Token('TYPE_INT', 'int'), Tree('return', [Token('IDENT', 'a')])]), Tree('assign', [Token('IDENT', 'val'), Tree('call', [Token('IDENT', 'myfunc'), Token('INT', '5')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    function myfunc(int a) returns int {
    return a;
    }

    val = myfunc(5);
    '''

    # Expected output
    assert evaluator.env_v["val"] == 5

# test that function create local scopes that doesn't affect global variables
def test_static_scoperule_function():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '0')]), Tree('func_def', [Token('IDENT', 'myfunc'), Tree('param', []), Tree('assign', [Token('IDENT', 'a'), Token('INT', '22')])]), Tree('call', [Token('IDENT', 'myfunc')])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 0;

    function myfunc() {
    a = 22;
    }
    myfunc();
    '''

    # Expected output
    assert evaluator.env_v["a"] == 0

# test for recursive calls, using a recursive implementation of factorial
def test_recursive_function():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('func_def_ret', [Token('IDENT', 'factorial'), Tree('param', [Tree('param_item', [Token('TYPE_INT', 'int'), Token('IDENT', 'n')])]), Token('TYPE_INT', 'int'), Tree('body', [Tree('if', [Tree('leq', [Token('IDENT', 'n'), Token('INT', '1')]), Tree('then', [Tree('return', [Token('INT', '1')])])]), Tree('return', [Tree('mult', [Token('IDENT', 'n'), Tree('call', [Token('IDENT', 'factorial'), Tree('sub', [Token('IDENT', 'n'), Token('INT', '1')])])])])])]), Tree('assign', [Token('IDENT', 'result'), Tree('call', [Token('IDENT', 'factorial'), Token('INT', '5')])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    function factorial(int n) returns int {
        if (n <= 1) then { return 1; }
        return n * factorial(n - 1);
    }

    result = factorial(5);
    '''

    # Expected output
    assert evaluator.env_v["result"] == 120

## Test with if statements ##
# test that true if-statements run then case
def test_if_statement_then():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '0')]), Tree('if', [Token('TRUE', 'true'), Tree('then', [Tree('assign', [Token('IDENT', 'a'), Token('INT', '1')])])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    if(true) then {
    a = 1;
    }
    '''

    # Expected output
    assert evaluator.env_v["a"] == 1

# test that flase if-statements run else case
def test_if_statement_else():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '0')]), Tree('if', [Token('FALSE', 'false'), Tree('then', [Tree('assign', [Token('IDENT', 'a'), Token('INT', '1')])]), Tree('else', [Tree('assign', [Token('IDENT', 'a'), Token('INT', '2')])])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 0;
    if (false) then {
        a = 1;
    }
    else {
        a = 2;
    }
    '''

    # Expected output
    assert evaluator.env_v["a"] == 2

## Test with while loops ##
# test that the body of a while loop executes the correct amount of times
def test_while_true():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '0')]), Tree('while', [Tree('less', [Token('IDENT', 'a'), Token('INT', '10')]), Tree('assign', [Token('IDENT', 'a'), Tree('add', [Token('IDENT', 'a'), Token('INT', '1')])])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 0;
    while (a < 10) do {
        a = a + 1;
    }
    '''

    # Expected output
    assert evaluator.env_v["a"] == 10

# test that a while loop with false condition doesn't run the body
def test_while_false():

    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '0')]), Tree('while', [Token('FALSE', 'false'), Tree('assign', [Token('IDENT', 'a'), Tree('add', [Token('IDENT', 'a'), Token('INT', '1')])])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 0;
    while (false) do {
        a = a + 1;
    }
    '''

    # Expected output
    assert evaluator.env_v["a"] == 0

# test that a stop statement correctly exits a loop
def test_stop_in_while():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '0')]), Tree('while', [Token('TRUE', 'true'), Tree('if', [Tree('equal', [Token('IDENT', 'a'), Token('INT', '5')]), Tree('then', [Tree('stop', [Token('STOP', 'stop')])])]), Tree('assign', [Token('IDENT', 'a'), Tree('add', [Token('IDENT', 'a'), Token('INT', '1')])])])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = 0;
    while (true) do {
        if (a == 5) then { stop; }
        a = a + 1;
    }
    '''

    # Expected output
    assert evaluator.env_v["a"] == 5

## Test for exceptions ##
# test that using an undeclared variable correctly raises an exception
def test_undeclared_variable():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('IDENT', 'b')])])
    evaluator = Interpreter()
    with pytest.raises(Exception) as excinfo:
        evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    a = b;
    '''

    # Expected output
    assert "variable not declared: 'b'" in str(excinfo.value)

# test that duplicating function names correctly raises an exception
def test_duplicate_function_definition():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [
        Tree('func_def', [Token('IDENT', 'myfunc'), Tree('param', []), Tree('assign', [Token('IDENT', 'a'), Token('INT', '1')])]),
        Tree('func_def', [Token('IDENT', 'myfunc'), Tree('param', []), Tree('assign', [Token('IDENT', 'a'), Token('INT', '2')])]),
    ])
    evaluator = Interpreter()
    with pytest.raises(Exception) as excinfo:
        evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    function myfunc() { a = 1; }
    function myfunc() { a = 2; }
    '''

    # Expected output
    assert "Function 'myfunc' already defined" in str(excinfo.value)

# test that na cant be used as a condition (if statement used as an example)
def test_if_na_condition():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('if', [Token('NA', 'NA'), Tree('then', [Tree('assign', [Token('IDENT', 'a'), Token('INT', '1')])])])])
    evaluator = Interpreter()
    with pytest.raises(Exception) as excinfo:
        evaluator.PEval(syntax_tree)

    # What the syntax_tree represents
    '''
    if (NA) then { a = 1; }
    '''

    # Expected output
    assert "If condition evaluated to NA" in str(excinfo.value)