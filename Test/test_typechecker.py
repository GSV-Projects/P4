from lark import Tree, Token
from tadpole.type_checker import Typechecker
import pytest



def test_assign():
    # Testing assignment of a variable

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '5')])])
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 5:
    '''

    # Expected output
    assert typechecker.vtable['a'] == int


def test_typechange():
    # Testing resassignment of a variable to another type

    # Setup
    tree = Tree('program', [
        Tree('assign', [Token('IDENT', 'a'), Token('INT', '5')]),
        Tree('assign', [Token('IDENT', 'a'), Token('STRING', 'string')])
    ])

    typechecker = Typechecker()
    
    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 5;
    a = "string"
    '''

    # Expected output
    assert "cannot be declared as type" in str(excinfo.value)


def test_not_in_loop():
    # Testing 'stop' while not being in a loop

    # Setup
    tree = Tree('program', [
    Tree('stop', [])
    ])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    stop;
    '''

    # Expected output
    assert "Cannot stop, not in loop" in str(excinfo.value)

def test_nested_loops():
    # Testing nested while loops with stop inside

    # Setup 
    tree = Tree(Token('RULE', 'program'), [
        Tree('while', [Token('TRUE', 'true'), Tree('while', [Token('TRUE', 'true'), Tree('stop', [Token('STOP', 'stop')])]), Tree('stop', [Token('STOP', 'stop')])])])
    typechecker = Typechecker()

    # What the syntax_tree represents
    '''
    while (true) do {
        while (true) do {
            stop;
        }
        stop;
    }
    '''

    # Expected output
    assert typechecker.check_p(tree) is None


def test_add_int_float():
    # Testing addition between int and float

    # Setup
    tree = Tree('program', [
        Tree('assign', [Token('IDENT', 'a'), Tree('add', [Token('INT', '5'), Token('FLOAT', '5.5')])]),
    ])    
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 5 + 5.5;
    '''

    # Expected output
    assert typechecker.vtable['a'] == float

def test_add_int_NA():
    # Testing addition of int and NA

    # Setup
    tree = Tree('program', [
        Tree('assign', [Token('IDENT', 'a'), Tree('add', [Token('INT', '5'), Token('NA', 'NA')])]),
    ])    
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 5 + NA;
    '''

    # Expected output
    assert typechecker.vtable['a'] == int


def test_array_indexing_with_float():
    # Index with a float

    # Setup
    tree = Tree(Token('RULE', 'program'), [
        Tree('assign', [Token('IDENT', 'a'), Tree('array', [Token('INT', '1'), Token('INT', '2'), Token('INT', '3')])]), Tree('assign_index', [Token('IDENT', 'a'), Token('FLOAT', '2.2'), Token('INT', '5')])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = [1,2,3];
    a[2.2] = 5;
    '''

    # Expected output
    assert "Did not parse an integer for array indexing" in str(excinfo.value)

def test_array_indexing_value():
    # Testing value that is returned and type of array

    # Setup
    tree = Tree(Token('RULE', 'program'), [
        Tree('assign', [Token('IDENT', 'a'), Tree('array', [Token('INT', '1'), Token('INT', '2'), Token('INT', '3')])]), Tree('assign', [Token('IDENT', 'b'), Tree('index', [Token('IDENT', 'a'), Token('INT', '2')])])])
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = [1,2,3];
    b = a[2];
    '''

    # Expected output
    assert (typechecker.vtable['b'] == int and typechecker.vtable['a'] == [int])

def test_array_creation_exception():
    # Testing array wher not all types are the same

    # Setup
    tree = Tree(Token('RULE', 'program'), [
        Tree('assign', [Token('IDENT', 'a'), Tree('array', [Token('INT', '1'), Token('INT', '2'), Token('FLOAT', '3.4')])])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = [1,2,3.4];
    '''

    # Expected output
    assert "Not all elements of array are of the same type" in str(excinfo.value)

def test_array_creation_correct_type():
    # Testing correct array creation

    # Setup
    tree = Tree(Token('RULE', 'program'), [
        Tree('assign', [Token('IDENT', 'a'), Tree('array', [Token('INT', '1'), Token('INT', '2'), Token('INT', '3')])])])
    typechecker = Typechecker()

    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = [1,2,3];
    '''

    # Expected output   
    assert typechecker.vtable['a'] == [int]

def test_func_assign_locally_globally():
    # Testing assignment of varible local and global

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '5')]), Tree('func_def_ret', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_FLOAT', 'float'), Token('IDENT', 'a')])]), Token('TYPE_FLOAT', 'float'), Tree('return', [Token('IDENT', 'a')])]), Tree('assign', [Token('IDENT', 'b'), Tree('call', [Token('IDENT', 'myfunc'), Token('FLOAT', '2.5')])])])
    typechecker = Typechecker()

    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 5;

    function myfunc(float a) returns float{
    return a;
    }

    b = myfunc(2.5);
    '''

    # Expected output
    assert (typechecker.vtable['a'] == int and typechecker.vtable['b'] == float)

def test_func_return_out_of_scope():
    # Testing return out of a function 

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('return', [Token('INT', '3')])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    return 3;
    '''

    # Expected output
    assert "doesnt match with function return type" in str(excinfo.value)

def test_func_return_wrong_type():
    # Testing return with wrong type 

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('func_def_ret', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_FLOAT', 'float'), Token('IDENT', 'a')])]), Token('TYPE_FLOAT', 'float'), Tree('body', [Tree('assign', [Token('IDENT', 'a'), Token('INT', '5')]), Tree('return', [Token('IDENT', 'a')])])]), Tree('assign', [Token('IDENT', 'b'), Tree('call', [Token('IDENT', 'myfunc'), Token('FLOAT', '2.5')])])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    function myfunc(float a) returns float{
        a = 5;
        return a;
    }

    b = myfunc(2.5);
    '''

    # Expected output
    assert "doesnt match with function return type" in str(excinfo.value)

def test_if_not_bool():
    # Testing if its possible to use a non bool in the if stmt

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '3')]), Tree('if', [Token('IDENT', 'a'), Tree('then', [Tree('assign', [Token('IDENT', 'b'), Token('INT', '5')])])])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 3;

    if (a) then {
        b = 5;
    }
    '''

    # Expected output
    assert "is not a boolean expression" in str(excinfo.value)

def test_func_multiple_params():
    # Testing if we get an error is amont of actual and formal doesnt match
    pass

def test_func_scope_isolation():
    # function f() { x = 10; } x = 5; f(); x should still be 5
    pass

def test_NA_array():
    pass

def test_check_logical():
    pass

def test_while_not_bool():
    pass

def test_table_type():
    pass

def test_column_types():
    pass