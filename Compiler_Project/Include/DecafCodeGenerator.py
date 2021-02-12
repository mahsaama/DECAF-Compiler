from lark import Lark, Tree
from lark.visitors import Interpreter

from Compiler_Project.Include.SymbolTable import *
from Compiler_Project.Include.traversal import *
from Compiler_Project.Include.LibFunctionCodeGenerator import *


def POP():
    pass


class CodeGenerator(Interpreter):  # TODO : Add access modes
    current_scope = 'root'
    stack = []
    stack_counter = [0]
    block_stmt_counter = 0
    string_counter = 0
    label_counter = 0
    class_counter = 0


    def __init__(self):
        pass

    def start(self, parse_tree):
        pass

    def decl(self, parse_tree):
        return code

    def variable_decl(self, parse_tree):
        pass

    def type(self, parse_tree):
        pass

    def function_decl(self, parse_tree):
        return code

    def formals(self, parse_tree):
        return code

    def class_decl(self, parse_tree):
        return code

    def field(self, parse_tree):
        return code

    def interface_decl(self, parse_tree):
        return code

    def stmt_block(self, parse_tree):
        return code

    def stmt(self, parse_tree):
        return code

    def if_stmt(self, parse_tree):
        return code

    def while_stmt(self, parse_tree):
        return code

    def for_stmt(self, parse_tree):
        return code

    def return_stmt(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def break_stmt(self, parse_tree):
        return code

    def continue_stmt(self, parse_tree):
        return code

    def print(self, parse_tree):
        return code

    def expr(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr1(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr2(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr3(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr4(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr5(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr6(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr7(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def expr8(self, parse_tree):
        child_codes = self.visit_children(parse_tree)
        if len(child_codes) == 0:
            return ''
        return ''.join(child_codes)

    def assignment(self, parse_tree):
        return code

    def logical_or(self, parse_tree):
        return code

    def logical_and(self, parse_tree):
        return code

    def equals(self, parse_tree):
        return code

    def not_equals(self, parse_tree):
        return code

    def lt(self, parse_tree):
        return code

    def lte(self, parse_tree):
        return code

    def gt(self, parse_tree):
        return code

    def gte(self, parse_tree):
        return code

    def sum(self, parse_tree):
        return code

    def sub(self, parse_tree):
        return code

    def mul(self, parse_tree):
        return code

    def div(self, parse_tree):
        return code

    def mod(self, parse_tree):
        return code

    def minus(self, parse_tree):
        return code

    def logical_not(self, parse_tree):
        return code

    def read_char(self, parse_tree):
        return code

    def read_int(self, parse_tree):
        return code

    def read_line(self, parse_tree):
        return code

    def new_class(self, parse_tree):
        return code

    def new_array(self, parse_tree):
        return code

    def val(self, parse_tree):
        return code

    def ident_l_value(self, parse_tree):
        return code

    def mem_access_l_value(self, parse_tree):
        return code

    def array_access_l_value(self, parse_tree):
        return code

    def method_call(self, parse_tree):
        return code

    def l_value(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def call(self, parse_tree):
        pass

    def actuals(self, parse_tree):
        return code

    def int_push(self, parse_tree):
        return code

    def double_push(self, parse_tree):
        return code

    def bool_push(self, parse_tree):
        return code

    def string_push(self, parse_tree):
        return code

    def null(self, parse_tree):
        return code

    def get_type(self, typ):
        pass

def decafCGEN(code):
    parser = Lark(Grammar, parser="lalr")
    parse_tree = parser.parse(code)
    SymbolTable().visit(parse_tree)
    ParentTree().visit(parse_tree)
    set_parents()
    Traversal().visit(parse_tree)
    MIPS_code = CodeGenerator().visit(parse_tree)
    return MIPS_code

if __name__ == '__main__':
    print(decafCGEN(code))
