import sys
from function import Type, Function,function_objects, function_table
from traversal import *

Grammar = """
    start : (decl)+
    decl : variable_decl 
        | function_decl 
        | class_decl   
        | interface_decl

    variable_decl : variable ";"
    variable : type IDENT 
    type : PRIMITIVE | IDENT | type "[]"
    function_decl : type IDENT "("formals")" stmt_block  | "void" IDENT "("formals")" stmt_block 
    formals : variable (","variable)* |  
    class_decl : "class" IDENT ("extends" IDENT)?  ("implements" IDENT (","IDENT)*)?  "{"( field)*"}" 
    field :  variable_decl | function_decl
    access : ACCESS | 
    ACCESS : "private" | "public" | "protected"
    interface_decl : "interface" IDENT "{"(prototype)*"}" 
    prototype : type IDENT "(" formals ")" ";" 
        | "void" IDENT "(" formals ")" ";" 
    stmt_block : "{" (variable_decl)*  (stmt)* "}" 
    stmt :  (expr)? ";" 
        | if_stmt 
        | while_stmt 
        | for_stmt 
        | break_stmt 
        | continue_stmt 
        | return_stmt 
        | print_stmt -> print 
        | stmt_block  
    if_stmt : "if" "(" expr ")" stmt ("else" stmt)? 
    while_stmt : "while" "(" expr ")" stmt 
    for_stmt : "for" "(" (expr)? ";" expr ";" (expr)? ")" stmt 
    return_stmt : "return" (expr)? ";" 
    break_stmt : "break" ";" 
    continue_stmt : "continue" ";"
    print_stmt : "Print" "(" expr (","expr)* ")" ";" -> print

    expr : l_value "=" expr -> assignment | expr1
    expr1 : expr1 "||" expr2 -> logical_or | expr2
    expr2 : expr2 "&&" expr3 -> logical_and | expr3
    expr3 : expr3 "==" expr4 -> equals | expr3 "!=" expr4 -> not_equals | expr4
    expr4 : expr4 "<" expr5 -> lt | expr4 "<=" expr5 -> lte | expr4 ">" expr5 -> gt | expr4 ">=" expr5 -> gte | expr5
    expr5 : expr5 "+" expr6 -> sum | expr5 "-" expr6 -> sub | expr6
    expr6 : expr6 "*" expr7 -> mul 
        | expr6 "/" expr7 -> div 
        | expr6 "%" expr7 -> mod 
        | expr7
    expr7 : "-" expr7 -> minus | "!" expr7 -> logical_not | expr8
    expr8 : constant 
        | "ReadInteger" "(" ")" -> read_int 
        | "ReadLine" "(" ")" -> read_line 
        | "new" IDENT -> new_class 
        | "NewArray" "(" expr "," type ")" -> new_array 
        | "(" expr ")" 
        | l_value -> val 
        | call

    l_value : IDENT -> ident_l_value 
        |  expr8 "." IDENT -> mem_access_l_value 
        | expr8 "[" expr "]" -> array_access_l_value

    call : IDENT  "(" actuals ")" 
        |  expr8  "."  IDENT  "(" actuals ")" -> method_call

    actuals :  expr (","expr)* | 

    constant : INT -> int_push 
        | DOUBLE -> double_push 
        | BOOL -> bool_push 
        | STRING -> string_push 
        | "null" -> null

    DOUBLE.2 :  /(\\d+\\.(\\d*)?((e|E)(\\+|-)?\\d+)?)/ 
        | /(\\d+(e|E)(\\+|-)?\\d+)/

    INT:  /(0[x|X][0-9a-fA-F]+)/ 
        | /(\\d+)/

    BOOL :  /(true)/ | /(false)/
    PRIMITIVE : "int" | "double" | "bool" | "string"
 
    STRING : /"[^"\\n]*"/
    IDENT :  /(?!((true)|(false)|(void)|(int)|(double)|(bool)|(string)|(class)|(interface)|(null)|(extends)|(implements)|(for)|(while)|(if)|(else)|(return)|(break)|(continue)|(new)|(NewArray)|(Print)|(ReadInteger)|(ReadLine)|(private)|(protected)|(public))([^_a-zA-Z0-9]|$))[a-zA-Z][_a-zA-Z0-9]*/
    INLINE_COMMENT : "//" /[^\\n]*/ "\\n"
    MULTILINE_COMMENT : "/*" /(\\n|.)*?/ "*/"
    %import common.WS -> WHITESPACE

    %ignore WHITESPACE
    WS : /(\\v|\\t|\\n|\\r|\\f| )/+
    %ignore WS
    %ignore INLINE_COMMENT
    %ignore MULTILINE_COMMENT
"""

sp = 'root'
stack = [sp]
st_objects = []
symbol_table = {}


class SymbolTableObject:
    def __init__(self, scope=None, name=None, parent_scope=None):
        self.scope = scope
        self.name = name
        self.parent_scope = parent_scope
        self.type = Type()

        st_objects.append(self)


class SymbolTable(Interpreter):
    counter = 0
    class_counter = 0
    static_function_counter = len(function_table)
    block_stmt_counter = 0

    def decl(self, tree):

        for declaration in tree.children:
            if declaration.data == 'variable_decl':
                self.visit(declaration)
            elif declaration.data == 'function_decl':
                self.visit(declaration)
                pass
            elif declaration.data == 'class_decl':
                self.visit(declaration)
                pass
            elif declaration.data == 'interface_decl':
                self.visit(declaration)
                pass

    def class_decl(self, tree):
        ident = tree.children[0]
        class_type_object = Class(name=ident)
        class_table[ident.value] = self.class_counter
        self.class_counter += 1
        symbol_table_object = SymbolTableObject(scope=stack[-1], name=ident)
        symbol_table[(stack[-1], ident.value,)] = self.counter
        self.counter += 1
        if len(tree.children) > 1:
            if type(tree.children[1]) == lark.lexer.Token:
                stack.append(stack[-1] + "/__class__" + ident)
                for field in tree.children[2:]:
                    field._meta = class_type_object
                    self.visit(field)
                stack.pop()
            else:
                stack.append(stack[-1] + "/__class__" + ident)
                for field in tree.children[1:]:
                    field._meta = class_type_object
                    self.visit(field)
                stack.pop()

    def function_decl(self, tree):
        class_type_object = tree._meta
        if len(tree.children) == 4:
            ident = tree.children[1]
            formals = tree.children[2]
            stmt_block = tree.children[3]
        else:
            ident = tree.children[0]
            formals = tree.children[1]
            stmt_block = tree.children[2]

        symbol_table_object = SymbolTableObject(scope=stack[-1], name=ident)
        symbol_table[(stack[-1], ident.value,)] = self.counter
        self.counter += 1
        function = Function(name=ident.value, label=stack[-1] + "/" + ident.value)

        if type(tree.children[0]) == lark.tree.Tree:
            object_type = tree.children[0]
            object_type._meta = symbol_table_object
            self.visit(object_type)
            function.return_type = symbol_table_object.type
        else:
            symbol_table_object.type.name = 'void'
            function.return_type.name = 'void'

        if class_type_object:
            this = Tree(data='variable',
                        children=[Tree(data='type', children=[Token(type_='PRIMITIVE', value=class_type_object.name)]),
                                  Token(type_='IDENT', value='this')])
            temp = formals.children.copy()
            formals.children = [this] + temp

        stack.append(stack[-1] + "/" + ident)
        formals._meta = function
        self.visit(formals)
        stack.append(stack[-1] + "/_local")
        self.visit(stmt_block)
        stack.pop()  # pop _local
        stack.pop()  # pop formals

        if class_type_object:
            class_type_object.functions.append(function)
            pass
        else:
            function_table[function.name] = self.static_function_counter
            function_objects.append(function)
            self.static_function_counter += 1

    def formals(self, tree):
        function = tree._meta
        if tree.children:
            for variable in tree.children:
                variable._meta = function
                self.visit(variable)

    def stmt_block(self, tree):
        stack.append(stack[-1] + "/" + str(self.block_stmt_counter))
        self.block_stmt_counter += 1
        for child in tree.children:
            if child.data == 'variable_decl':
                self.visit(child)
            else:
                self.visit(child)
        stack.pop()

    def stmt(self, tree):
        child = tree.children[0]
        if child.data == 'if_stmt':
            self.visit(child)
        if child.data == 'while_stmt':
            self.visit(child)
        if child.data == 'for_stmt':
            self.visit(child)
        if child.data == 'stmt_block':
            self.visit(child)

    def if_stmt(self, tree):
        stmt = tree.children[1]
        self.visit(stmt)
        if len(tree.children) == 3:
            else_stmt = tree.children[2]
            self.visit(else_stmt)

    def while_stmt(self, tree):
        stmt = tree.children[1]
        self.visit(stmt)

    def for_stmt(self, tree):
        stmt = tree.children[-1]
        self.visit(stmt)

    def field(self, tree):
        tree.children[0]._meta = tree._meta
        self.visit(tree.children[0])

    def variable_decl(self, tree):
        tree.children[0]._meta = tree._meta
        self.visit(tree.children[0])

    def variable(self, tree):
        object_type = tree.children[0]
        name = tree.children[1].value

        symbol_table_object = SymbolTableObject(scope=stack[-1], name=name)
        symbol_table[(stack[-1], name,)] = self.counter
        self.counter += 1

        object_type._meta = symbol_table_object
        self.visit(object_type)
        if type(tree._meta) == Class:
            class_type_object = tree._meta
            class_type_object.variables.append([name, symbol_table_object.type])
        if type(tree._meta) == Function:
            function = tree._meta
            function.formals.append([name, symbol_table_object.type])

    def type(self, tree):
        if type(tree.children[0]) == lark.lexer.Token:
            symbol_table_object = tree._meta
            symbol_table_object.type.name = tree.children[0].value
        else:
            symbol_table_object = tree._meta
            symbol_table_object.type.size += 1
            tree.children[0]._meta = tree._meta
            self.visit(tree.children[0])


code = """
class Binky {
  void Method1() {
    Print(1);
  }

  void Method2() {
    this.Method1();
    Print(2);
    Method1();
  }

  void Method3(Binky b)
  {
     b.Method1();
     Print(2);
     this.Method2();
  }
}

int main() {
  Binky b;
  Binky c;
  b = new Binky;
  c = new Binky;
  b.Method3(c);
}
"""

if __name__ == '__main__':

    parser = Lark(Grammar, parser="lalr")
    try:
        parse_tree = parser.parse(code)
    except:
        sys.exit("Syntax Error")

    SymbolTable().visit(parse_tree)
    print(symbol_table)
    print(class_table)
    print(function_table)
    print(parent_classes)
    print(class_type_objects)
    print(function_objects)
