from tadpole.parser_lexer_lark import parser


# Testing grammar if its parseable
def test_assign():
    input = '''
        b = 2+2;
    '''
    assert parser.parse(input)

def test_while():
    input = '''
        while ( 2 /= 4 ) do {x = x + 1;}
    '''
    assert parser.parse(input)

def test_tablecreation():
    input = '''
        mytab = {
        name: ["he", "Dave", 4, t+2];
        age: [5, "25", bob, 12.1]; 
        };
    '''
    assert parser.parse(input)
    
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

    
def test_func_call():
    input = '''
        function myfunc(){x = 1;}
        y = y.myfunc();
        myfunc();
    '''
    assert parser.parse(input)
    
    
def test_equal_expr():
    input = '''
        x = 5;
        y = 4;
        z = x /= y;
        zz = x == y;
    '''
    assert parser.parse(input)

def test_mult_expr():
    input = '''
        x = 3; y = 4;
        z = x * y;
        z = x / y;
        z = x mod y;
    '''
    assert parser.parse(input)

def test_unary_expr():
    input = '''
        x = -(2);
        y = ---2;
    '''
    assert parser.parse(input)
