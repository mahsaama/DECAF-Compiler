from lark import Lark, Tree
from lark.visitors import Interpreter

from Compiler_Project.Include.SymbolTable import *
from Compiler_Project.Include.traversal import *
from Compiler_Project.Include.LibFunctionCodeGenerator import *


def POP(scope):
    scope = scope.split("/")
    scope.pop()
    return '/'.join(scope)



def labelCounter():
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
        super().__init__()
        self.expressionTypes = []
        self.stmtLabels = []
        self.loopLabels = []
        self.lastType = None

    def start(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def decl(self, parse_tree):
        #  decl : variable_decl | function_decl | class_decl | interface_decl
        mips_code = ''
        for decl in parse_tree.children:
                mips_code += self.visit(decl)
        return mips_code

    def variable_decl(self, parse_tree):
        ### variable : [0] : type ,[1] : name
        mips_code = ''
        variable  = parse_tree.children[0]
        variable_type = variable.children[0]
        default_size = 4
        if type(variable_type.children[0]) == lark.lexer.Token:
            var_type = variable_type.children[0].value
            variable_name = variable.children[1]

            if var_type == 'string':
                mips_code += '.data\n'
                mips_code += '.align 2\n'
                mips_code += self.current_scope.replace('/', '_') + '_' + variable.children[1] + ': .space ' + str(default_size) + '\n'
                mips_code += '.text\n'
                mips_code += '\tli $a0, 256\n'
                mips_code += '\tli $v0, 9\n'
                mips_code += '\tsyscall\n'
                mips_code += '\tsw $v0, ' + self.current_scope.replace('/', '_') + '_' + variable.children[1] + '\n'+'\n'
                return mips_code

            if var_type == 'double':
                default_size = 8

        mips_code += '.data\n'
        mips_code += '.align 2\n'

        mips_code += self.current_scope.replace('/', '_') + '_' + variable_name + ': .space ' + str(default_size) + '\n'+'\n'
        return mips_code


    def type(self, parse_tree):

        if type(parse_tree.children[0]) == lark.lexer.Token:
            self.last_type = Type(parse_tree.children[0])
        else:
            self.visit(parse_tree.children[0])
            self.last_type.size += 1

        return ' '



    def function_decl(self, parse_tree):

        mips_code = ' '
        ##### "void" IDENT "("formals")" stmt_block
        if len(parse_tree.children) == 3:
            ident = parse_tree.children[0]
            formals = parse_tree.children[1]
            stmt_block= parse_tree[2]


        ###### type IDENT "("formals")" stmt_block
        else:
            ident = parse_tree.children[1]
            formals = parse_tree.children[2]
            stmt_block= parse_tree[3]

        self.current_scope += "/" + ident.value


        if ident != "main":

            tree_children=[Tree(data='return_stmt', children=[])]
            return_stmt = Tree(data="stmt" , children=tree_children)
            stmt_block._meta = return_stmt



        # ident = main
        if ident == "main":
            mips_code += ('.text\n'
                '__strcmp__:\n'
                '\tlb $t0, 0($a0)\n'
                '\tlb $t1, 0($a1)\n'
                '\tbne $t0, $t1, __NE__\n'
                '\tbne $t0, $zero, __cont__\n'
                '\tli $v0, 1\n'
                '\tjr $ra\n'
                '__cont__:\n'
                '\taddi $a0, $a0, 1\n'
                '\taddi $a1, $a1, 1\n'
                '\tj __strcmp__\n'
                '__NE__:\n'
                '\tli $v0, 0\n'
                '\tjr $ra\n\n'
                '.data\n'
                '.align 2\n'
                '\ttrue: .asciiz "true"\n'
                '\tfalse: .asciiz "false"\n'
                '\tpconst10000: .double 10000.0\n'
                '\tnw: .asciiz "\\n"\n'
                '\tsign_double: .asciiz "-"\n'
                '\t__const_0_5__: .double 0.5\n')

          #TODO code += cast_cgen
            mips_code +=('.text\n'+'main:\n')

            for clas in range(len(class_counter)):
                mips_code += '\tjal __init__vtable_{}\n'.format(clas)

            mips_code += '\tla\t$ra,__end__\n'

        # formal
        mips_code += self.visit(formals)
        self.current_scope +="/_local"
        self.stack.append(0)

        # stmt_block
        mips_code += self.visit(stmt_block)


        locals_cnt = self.stack[-1]
        self.stack = self.stack[:-locals_cnt]
        self.stack.pop()
        # remove local from scope
        self.current_scope = POP(self.current_scope)
        # remove formals from scope
        self.current_scope = POP(self.current_scope)

        if ident == 'main':
            mips_code += '.text\n'+'__end__:\n'+'__end__:\n'+ '\tli $v0, 10\t\t\t#exit\n'+'\tsyscall\n'

        return mips_code

        return code

    def formals(self, parse_tree):
        #  formals : variable (","variable)*
        mips_code = ''
        for variable in parse_tree.children:

            name = variable.children[1].value
            type = SymbolTableObject[SymbolTable[(self.current_scope, name)]].type
            mips_code += '.data\n' + '.align 2\n'
            default_size = 4

            if type.name == 'double' and type.dimension == 0:
                default_size = 8

            mips_code += '{}: .space {}\n'.format((self.current_scope + "/" + name).replace("/", "_") , default_size)

        return mips_code


    def class_decl(self, parse_tree):

        # class_decl : "class" IDENT ("extends" IDENT)?  ("implements" IDENT (","IDENT)*)?  "{"(field)*"}"

        mips_code = ''
        ident = parse_tree.children[0]

        self.current_scope += "/__class__" + ident.value

        # TODO class_object = class_type_objects[class_table[ident.value]]

        mips_code += '.data\n' + '.align 2\n'
        mips_code += '{}: .space 4\n'.format(class_object.name + '_vtable')

        mips_code += '.text\n'
        mips_code += '__init__vtable_{}:\n'.format(self.class_cnt)

        mips_code += '\tli $a0, {}\n'.format(len(class_object.functions) * 4)
        mips_code += '\tli $v0, 9\n' + '\tsyscall\n'
        mips_code += '\tsw $v0, {}\n'.format(class_object.name + '_vtable')
        self.class_counter += 1

        func_counter = 0

        for func in class_object.functions:

            mips_code += '\tla $t0, {}\n\tsw $t0, {}($v0)\n'.format(func.exact_name.replace('/', '_') , func_counter)
            func_counter += 4

        mips_code += '\tjr $ra\n'

        # if current class extends or implements other class
        if len(parse_tree.children) > 1:

            if type(parse_tree.children[1]) == lark.lexer.Token:

                for field in parse_tree.children[2:]:
                    if field.children[0].data == 'function_decl':
                        mips_code += self.visit(field)
            else:
                for field in parse_tree.children[1:]:
                    if field.children[0].data == 'function_decl':
                        mips_code += self.visit(field)


        self.current_scope = POP(self.current_scope)
        return mips_code

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
        code = ''.join(self.visit_children(parse_tree))
        type = self.expressionTypes.pop()
        if type.name == 'int':
            code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tsle $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n"""
        elif type.name == 'double':
            c = labelCounter() # labels TODO
            code += """.text\n
                \tli $t0, 0\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tc.le.d $f2, $f0\n
                \tbc1f __double_le__{}\n
                \tli $t0, 1\n
                __double_le__{}:\tsw $t0, 8($sp)\n   
                \taddi $sp, $sp, 8\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return code

    def gt(self, parse_tree):
        return code

    def gte(self, parse_tree):
        return code

    def sum(self, parse_tree):
        return code

    def sub(self, parse_tree):
        code = ''.join(self.visit_children(parse_tree))
        type = self.expressionTypes.pop()
        if type.name == 'int':
            code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tsub $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n"""
        else:
            code += """.text\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tsub.d $f4, $f2, $f0\n
                \ts.d $f4, 8($sp)\n
                \taddi $sp, $sp, 8\n"""
        return code

    def mul(self, parse_tree):
        code = ''.join(self.visit_children(parse_tree))
        type = self.expressionTypes.pop()
        if type.name == 'int':
            code += """.text\n
                \tlw   $t0, 0($sp)\n
                \tlw   $t1, 8($sp)\n
                \tmul  $t2, $t1, $t0\n
                \tsw   $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n"""
        elif type.name == 'double':
            code += """.text\n
                \tl.d      $f0, 0($sp)\n
                \tl.d      $f2, 8($sp)\n
                \tmul.d    $f4, $f2, $f0\n
                \ts.d      $f4, 8($sp)\n
                \taddi     $sp, $sp, 8\n"""
        return code

    def div(self, parse_tree):
        code = ''.join(self.visit_children(parse_tree))
        type = self.expressionTypes.pop()
        if type.name == 'int':
            code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tdiv $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n"""
        elif type.name == 'double':
            code += """.text\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tdiv.d $f4, $f2, $f0\n
                \ts.d $f4, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        return code

    def mod(self, parse_tree):
        code = ''.join(self.visit_children(parse_tree))
        code += """.text\n
            \tlw $t0, 0($sp)\n
            \tlw $t1, 8($sp)\n
            \tdiv $t1, $t0\n
            \tmfhi $t2\n
            \tsw $t2, 8($sp)\n
            \taddi $sp, $sp, 8\n"""
        self.expressionTypes.pop()
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
