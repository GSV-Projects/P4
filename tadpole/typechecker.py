from lark import Visitor, Lark, Tree, Transformer
from parser_lexer_lark import result

@dataclass(frozen=True)
class Type:
    name: str

# Primitives
INT   = Type("int")
FLOAT = Type("float")
BOOL  = Type("bool")
STRING   = Type("str")

class Typechecker:
    def direct(self, c) -> Type:
        self.vtable = {}
        self.ftabel = {}

    node_kind = node["kind"] # Finds the type read from the AST, stroed in the node
    match node_kind:
        case "int_lit":    return INT
        case "float_lit":  return FLOAT
        case "bool_lit":   return BOOL
        case "str_lit":    return STR
        case "var":        return self.check_var(node)
        case "assign":     return self.check_assign(node)
        case "binary":     return self.check_binary(node)   # <-- one function!
        case "unary":      return self.check_unary(node)
        case "if":         return self.check_if(node)
        case "call":       return self.check_call(node)
        case _:
            raise TypeError(f"Unknown node kind: {kind}")
