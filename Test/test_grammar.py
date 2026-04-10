from tadpole.parser_lexer_lark import parser


def test_assign():
    input = '''
        b = 2+2;
            '''
    assert parser.parse(input)

def test_while():
    input = x

def test_tablecreation():
    input = '''
        mytab = {
        name: ["he", "Dave", 4, t+2];
        age: [5, "25", bob, 12.1]; 
        };
'''
    assert parser.parse(input)
    
def test_func_def():
    input = x
    
def test_func_call():
    input = x
    
def test_equal_expr():
    input = x

def test_mod_expr():
    input = x

def test_unary_expr():
    input = x