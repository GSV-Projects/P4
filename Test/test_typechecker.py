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
    pass

def test_array_indexing_value():
    # Value that is returned
    pass

def test_array_creation_exception():
    # Not all types are the same
    pass

def test_array_creation_correct_type():
    # Correct array creation
    pass

def func_assign_locally_globally():
    # assign varible local and global and assert the type both times
    pass

def func_return_values():
    # Test return values are correct
    pass

def if_not_bool():
    # if (5) for example
    pass