from lark import Tree, Token
from tadpole.type_checker import Typechecker
import pytest

# The test for the type_checker are designed as unit tests, for each test we create an AST for a specific operation.
#   This ensues that there is no risk a fault is caused by the parsegenerator or parsertransformer
#   Each test consists of tree parts, 
#       a setup where is AST is run though the typechecker class
#       a comment that shows the code which is being tested
#       an assert that compares the result from the typechecker with what we know it should be

# Testing assignment of a variable
def test_assign():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '5')])])
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 5;
    '''

    # Expected output
    assert typechecker.vtable['a'] == int

# Testing resassignment of a variable to another type
def test_typechange():

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

# Testing 'stop' while not being in a loop
def test_not_in_loop():

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
    assert "Cannot use stop outside a loop" in str(excinfo.value)

# Testing nested while loops with stop inside
def test_nested_loops():

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

# Testing addition between int and float
def test_add_int_float():

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

# Testing addition of int and NA
def test_add_int_NA():

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

# Index with a float
def test_array_indexing_with_float():

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
    assert "Index must be an integer to index the array" in str(excinfo.value)

# Testing value that is returned and type of array
def test_array_indexing_value():

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

# Testing array wher not all types are the same
def test_array_creation_exception():

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

# Testing correct array creation
def test_array_creation_correct_type():

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

# Testing assignment of varible local and global
def test_func_assign_locally_globally():

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

# Testing return out of a function 
def test_func_return_out_of_scope():

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
    assert "Not possible to use return outside of a function or inside of a void function" in str(excinfo.value)

# Testing return inside a void function
def test_func_return_in_void_function():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('func_def', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_FLOAT', 'float'), Token('IDENT', 'a')])]), Tree('body', [Tree('assign', [Token('IDENT', 'a'), Token('FLOAT', '5.5')]), Tree('return', [Token('IDENT', 'a')])])])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    function myfunc(float a) {
        a = 5.5;
        return a;
    }
    '''

    # Expected output
    assert "Not possible to use return outside of a function or inside of a void function" in str(excinfo.value)

# Testing return with wrong type 
def test_func_return_wrong_type():

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
    assert "The return statement returns value of type" in str(excinfo.value)

# Testing if its possible to use a non bool in the if stmt
def test_if_not_bool():

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
    assert "must be a boolean expression" in str(excinfo.value)

# Testing if we get an error is amont of actual and formal doesnt match
def test_func_multiple_params():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('func_def_ret', [Token('IDENT', 'myfunc'), Tree('param', [Tree('param_item', [Token('TYPE_INT', 'int'), Token('IDENT', 'a')])]), Token('TYPE_INT', 'int'), Tree('return', [Token('IDENT', 'a')])]), Tree('assign', [Token('IDENT', 'b'), Tree('call', [Token('IDENT', 'myfunc'), Token('INT', '4'), Token('INT', '5')])])]) 
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    function myfunc(int a) returns int {
    return a;
    }

    b = myfunc(4,5);
    '''

    # Expected output
    assert "Amount of function parameters do not match the amount of passed parameters to the function" in str(excinfo.value)

# function f() { x = 10; } x = 5; f(); x should still be 5
def test_func_scope_isolation():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('func_def', [Token('IDENT', 'f'), Tree('param', []), Tree('assign', [Token('IDENT', 'x'), Token('INT', '10')])]), Tree('assign', [Token('IDENT', 'x'), Token('INT', '5')]), Tree('call', [Token('IDENT', 'f')])])    
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    function f() { 
        x = 10.4; 
    } 
    x = 5; 
    f();
    '''

    # Expected output
    assert typechecker.vtable['x'] == int

# Testing is its possible to create an array only with NA values
def test_NA_array():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'arr'), Tree('array', [Token('NA', 'NA'), Token('NA', 'NA'), Token('NA', 'NA')])])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    arr = [NA, NA, NA];
    '''

    # Expected output
    assert "Array cannot consist of only NA" in str(excinfo.value)

# Testing the logical operators
def test_check_logical():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'b'), Tree('and', [Token('TRUE', 'true'), Tree('less', [Token('INT', '5'), Token('INT', '3')])])])])
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    b = true and 5 < 3;
    '''

    # Expected output
    assert typechecker.vtable['b'] == bool

# Testing the boolean expression in a while loop
def test_while_not_bool():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '3')]), Tree('while', [Token('IDENT', 'a'), Tree('assign', [Token('IDENT', 'b'), Token('INT', '5')])])])
    typechecker = Typechecker()

    with pytest.raises(Exception) as excinfo:
        typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    a = 3;

    while (a) do {
        b = 5;
    }
    '''

    # Expected output
    assert "must be a boolean expression" in str(excinfo.value)

# Testing tbl type
def test_table_type():

    # Setup
    tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'mytab'), Tree('table', [Tree('column', [Token('COLUMN', 'name'), Tree('array', [Token('STRING', '"David"'), Token('STRING', '"Mads"'), Token('STRING', '"Bo"')])]), Tree('column', [Token('COLUMN', 'rank'), Tree('array', [Token('INT', '1'), Token('INT', '67'), Token('INT', '2')])])])])])    
    typechecker = Typechecker()
    typechecker.check_p(tree)

    # What the syntax_tree represents
    '''
    mytab = {
    name : ["David","Mads","Bo"];
    rank : [1,67,2];
    };
    '''

    # Expected output
    assert typechecker.vtable['mytab'] == 'tbl'
