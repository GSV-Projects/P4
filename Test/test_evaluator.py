from lark import Tree, Token
from tadpole.interpreter import Interpreter
from tadpole.utils.NAliteral import NA
import pytest


''' TODO:
        - Create test for aritmetiske operationer
            +,-,*,/
            Edge cases man kan checke om de opfører sig korrekt
            Kun integer operationer
            Mixed float/int
            Division med 0
            Exponenter med store tal
            mod med 0
'''
# Aritmetic test
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

'''
def test_zerodivision():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Tree('div', [Token('INT', '5'), Token('INT', '0')])])])
    evaluator = Interpreter()
    with pytest.raises(Exception) as excinfo:
        evaluator.PEval(syntax_tree)


    # What the syntax_tree represents

    # Expected output
    assert "Division by zero not allowed!" in str(excinfo.value)
'''

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


# Test with NA

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
'''
def test_napropagation_parameter_parsing():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('func_def', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_INT', 'int'), Token('IDENT', 'a')]), Tree('param_item', [Token('TYPE_FLOAT', 'float'), Token('IDENT', 'b')])]), Tree('assign', [Token('IDENT', 'c'), Tree('add', [Token('IDENT', 'a'), Token('IDENT', 'b')])])]), Tree('call', [Token('IDENT', 'myfunc'), Token('NA', 'NA'), Token('FLOAT', '5.5')])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)
    local_function_vtable = evaluator.env_p["myfunc"][3]

    # What the syntax_tree represents
    
    #function myfunc(int a, float b) {
    #    c = a + b;
    #}

    #myfunc(NA, 5.5);

    # Expected output
    assert local_function_vtable["a"] is NA
'''

# Test with functions

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

'''
def test_function_without_return():
    # Setup
    syntax_tree = Tree(Token('RULE', 'program'), [Tree('func_def', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_INT', 'int'), Token('IDENT', 'a')])]), Tree('assign', [Token('IDENT', 'b'), Tree('add', [Token('IDENT', 'a'), Token('INT', '2')])])]), Tree('call', [Token('IDENT', 'myfunc'), Token('INT', '5')])])
    evaluator = Interpreter()
    evaluator.PEval(syntax_tree)
    func_table = evaluator.env_p["myfunc"]
    local_function_vtable = func_table[3]
    print("hihihi", local_function_vtable)

    # What the syntax_tree represents

    #function myfunc(int a) {
    #b = a + 2;
    #}
    #myfunc(5);

    # Expected output
    assert local_function_vtable["b"] == 7 
'''
# Test with if statements

def if_statement_then():
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

def if_statement_else():
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

# Test with while loops

def while_true():
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

def while_false():
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