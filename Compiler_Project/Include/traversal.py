import lark
from lark import Lark, Tree
from lark.lexer import Token
from lark.visitors import Interpreter
from Compiler_Project.Include.function import class_type_objects, class_table, Class


class ParentTree(Interpreter):
    def decl(self, tree):
        for declaration in tree.children:
            if declaration.data == 'class_decl':
                self.visit(declaration)

    def class_decl(self, tree):
        ident = tree.children[0]

        if type(tree.children[1]) == lark.lexer.Token:
            parent_name = tree.children[1].value
            parent = class_type_objects[class_table[parent_name]]
            parent.children.append(ident.value)
        else:
            parent_classes.append(ident.value)


parent_classes = []


def tree_traversal(parent_class: Class):
    if parent_class.children:
        for child in parent_class.children:
            child_class = class_type_objects[class_table[child]]
            child_class.variables = parent_class.variables + child_class.variables

            child_functions = child_class.functions.copy()
            child_class.functions = parent_class.functions.copy()
            parent_class_function_names = set()
            for func in parent_class.functions:
                parent_class_function_names.add(func.name)

            for func in child_functions:
                for i in range(len(child_class.functions)):
                    if child_class.functions[i].name == func.name:
                        child_class.functions[i] = func

            for func in child_functions:
                if func.name not in parent_class_function_names:
                    child_class.functions.append(func)

            tree_traversal(child_class)


def set_parents():
    for class_name in parent_classes:
        class_object = class_type_objects[class_table[class_name]]
        tree_traversal(class_object)


class Traversal(Interpreter):
    def decl(self, tree):
        for child in tree.children:
            if child.data == 'class_decl':
                self.visit(child)

    def class_decl(self, tree):
        for child in tree.children:
            if type(child) != lark.lexer.Token:
                child._meta = tree.children[0].value
                self.visit(child)

    def field(self, tree):
        if tree.children[0].data == 'function_decl':
            tree.children[0]._meta = tree._meta
            self.visit(tree.children[0])

    def access(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def function_decl(self, tree):
        tree.children[-1]._meta = tree._meta
        self.visit(tree.children[-1])

    def stmt_block(self, tree):
        for child in tree.children:
            if child.data != 'variable_decl':
                child._meta = tree._meta
                self.visit(child)

    def stmt(self, tree):
        for child in tree.children:
            if child.data != 'break_stmt' and child.data != 'continue_stmt':
                child._meta = tree._meta
                self.visit(child)

    def if_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def while_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def for_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def return_stmt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def print(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr(self, tree):
        tree.children[-1]._meta = tree._meta
        self.visit(tree.children[-1])

    def expr2(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr3(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr4(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr5(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr6(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr7(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr8(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def expr1(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def call(self, tree):
        if len(tree.children) == 2:
            name = tree._meta
            fun_name = tree.children[0].value
            exists = False
            for fun in class_type_objects[class_table[name]].functions:
                if fun.name == fun_name:
                    exists = True
            if exists:
                copy = tree.children.copy()
                this = Tree(data='val',
                            children=[Tree(data='ident_l_value', children=[Token(type_='IDENT', value='this')])])
                tree.children = [this] + copy
                tree.data = 'method_call'

    def assignment(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def logical_or(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def logical_and(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def equals(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def not_equals(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def lt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def lte(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def gt(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def gte(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def sum(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def sub(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def mul(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def div(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def mod(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def minus(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def logical_not(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def new_array(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def l_value(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def val(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)

    def mem_access_l_value(self, tree):
        tree.children[0]._meta = tree._meta
        self.visit(tree.children[0])

    def array_access_l_value(self, tree):
        for child in tree.children:
            child._meta = tree._meta
            self.visit(child)
