from tadpole.grammar import grammar
from lark import Lark

parser = Lark(grammar, parser="lalr", strict=True)

## Testing grammar if its parseable ##

# Testing grammar for assign
def test_assign():
    input = '''
        b = 2+2;
    '''
    assert parser.parse(input)

# Testing grammar for while loops
def test_while():
    input = '''
        while ( 2 /= 4 ) do {x = x + 1;}
    '''
    assert parser.parse(input)

# Testing grammar for creation of tables
def test_tablecreation():
    input = '''
        mytab = {
        name: ["he", "Dave", 4, t+2];
        age: [5, "25", bob, 12.1]; 
        };
    '''
    assert parser.parse(input)
    
# Testing grammar for defining functions    
def test_func_def():
    input = '''
        function myfunc (int eq, float mads) {
        e = 3;
        }

        function myfunco (int hej) returns bool {
        b = 2+2;
        }
    '''
    assert parser.parse(input)

# Testing grammar for function calls    
def test_func_call():
    input = '''
        function myfunc(){x = 1;}
        y = y.myfunc();
        myfunc();
    '''
    assert parser.parse(input)
    
# Testing grammar for equal expressions    
def test_equal_expr():
    input = '''
        x = 5;
        y = 4;
        z = x /= y;
        zz = x == y;
    '''
    assert parser.parse(input)

# Testing grammar for arimetic expressions
def test_mult_expr():
    input = '''
        x = 3; y = 4;
        z = x * y;
        z = x / y;
        z = x mod y;
    '''
    assert parser.parse(input)

# Testing grammar for unary expressions
def test_unary_expr():
    input = '''
        x = -(2);
        y = ---2;
    '''
    assert parser.parse(input)
