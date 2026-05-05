from lark import Tree, Token
from tadpole.type_checker import Typechecker


assign_tree = Tree(Token('RULE', 'program'), [Tree('assign', [Token('IDENT', 'a'), Token('INT', '5')])])
typechecker = Typechecker()
typechecker.check_p(assign_tree)

def test_vtable():
    assert typechecker.vtable['a'] == int