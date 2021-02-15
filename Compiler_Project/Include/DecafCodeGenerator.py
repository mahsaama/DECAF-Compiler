from lark import Lark, Tree
from lark.visitors import Interpreter

from Compiler_Project.Include.SymbolTable import *
from Compiler_Project.Include.traversal import *
from Compiler_Project.Include.LibFunctionCodeGenerator import *
from Compiler_Project.Include.function import make_indentation

from copy import deepcopy


def POP(scope):
    scope = scope.split("/")
    scope.pop()
    return '/'.join(scope)


def labelCounter():
    CodeGenerator.label_counter += 1
    return CodeGenerator.label_counter


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
        variable = parse_tree.children[0]
        variable_type = variable.children[0]
        default_size = 4
        if type(variable_type.children[0]) == lark.lexer.Token:
            var_type = variable_type.children[0].value
            variable_name = variable.children[1]

            if var_type == 'string':
                mips_code += '.data\n'
                mips_code += '.align 2\n'
                mips_code += self.current_scope.replace('/', '_') + '_' + variable.children[1] + ': .space ' + str(
                    default_size) + '\n'
                mips_code += '.text\n'
                mips_code += '\tli $a0, 256\n'
                mips_code += '\tli $v0, 9\n'
                mips_code += '\tsyscall\n'
                mips_code += '\tsw $v0, ' + self.current_scope.replace('/', '_') + '_' + variable.children[
                    1] + '\n' + '\n'
                return mips_code

            if var_type == 'double':
                default_size = 8

        mips_code += '.data\n'
        mips_code += '.align 2\n'

        mips_code += self.current_scope.replace('/', '_') + '_' + variable_name + ': .space ' + str(
            default_size) + '\n' + '\n'
        return mips_code

    def type(self, parse_tree):

        if type(parse_tree.children[0]) == lark.lexer.Token:
            self.lastType = Type(parse_tree.children[0])
        else:
            self.visit(parse_tree.children[0])
            self.lastType.size += 1

        return ' '

    def function_decl(self, parse_tree):

        mips_code = ' '
        ##### "void" IDENT "("formals")" stmt_block
        if len(parse_tree.children) == 3:
            ident = parse_tree.children[0]
            formals = parse_tree.children[1]
            stmt_block = parse_tree.children[2]


        ###### type IDENT "("formals")" stmt_block
        else:
            ident = parse_tree.children[1]
            formals = parse_tree.children[2]
            stmt_block = parse_tree.children[3]

        self.current_scope += "/" + ident.value

        if ident != "main":
            tree_children = [Tree(data='return_stmt', children=[])]
            return_stmt = Tree(data="stmt", children=tree_children)
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

            # TODO code += cast_cgen
            mips_code += ('.text\n' + 'main:\n')

            for clas in range(len(class_table)):
                mips_code += '\tjal __init__vtable_{}\n'.format(clas)

            mips_code += '\tla\t$ra,__end__\n'

        # formal
        mips_code += self.visit(formals)
        self.current_scope += "/_local"
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
            mips_code += '.text\n' + '__end__:\n' + '__end__:\n' + '\tli $v0, 10\t\t\t#exit\n' + '\tsyscall\n'

        return mips_code

        return code

    def formals(self, parse_tree):
        #  formals : variable (","variable)*
        mips_code = ''
        for variable in parse_tree.children:
            name = variable.children[1].value
            print(name)
            f_type = SymbolTableObject[symbol_table[(self.current_scope, name)]].type
            mips_code += '.data\n' + '.align 2\n'
            default_size = 4

            if f_type.name == 'double' and f_type.dimension == 0:
                default_size = 8

            mips_code += '{}: .space {}\n'.format((self.current_scope + "/" + name).replace("/", "_"), default_size)

        return mips_code

    def class_decl(self, parse_tree):

        # class_decl : "class" IDENT ("extends" IDENT)?  ("implements" IDENT (","IDENT)*)?  "{"(field)*"}"

        mips_code = ''
        ident = parse_tree.children[0]

        self.current_scope += "/__class__" + ident.value

        class_object = class_type_objects[class_table[ident.value]]

        mips_code += '.data\n' + '.align 2\n'
        mips_code += '{}: .space 4\n'.format(class_object.name + '_vtable')

        mips_code += '.text\n'
        mips_code += '__init__vtable_{}:\n'.format(self.class_counter)

        mips_code += '\tli $a0, {}\n'.format(len(class_object.functions) * 4)
        mips_code += '\tli $v0, 9\n' + '\tsyscall\n'
        mips_code += '\tsw $v0, {}\n'.format(class_object.name + '_vtable')
        self.class_counter += 1

        func_counter = 0

        for func in class_object.functions:
            mips_code += '\tla $t0, {}\n\tsw $t0, {}($v0)\n'.format(func.name.replace('/', '_'), func_counter)
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

        mips_code = ''
        for ch in parse_tree.children:
            if ch.data == "function_decl":
                mips_code += self.visit(ch)
                pass
        return mips_code


    def interface_decl(self, parse_tree):
        return code

    def stmt_block(self, parse_tree):

        mips_code = ' '
        self.current_scope +="/" + str(self.block_stmt_counter)
        self.block_stmt_counter+=1
        stmt_num = labelCounter()
        mips_code +=  '.text\nstart_stmt_{}:\n'.format(stmt_num)


        if type(parse_tree._meta) == lark.tree.Tree:
            return_stmt = parse_tree._meta
            parse_tree.children.append(return_stmt)

        for child in parse_tree.children:
            if child.data == 'variable_decl':

                mips_code += self.visit(child)
                self.stack_local_params_count[-1] += 1

                name = child.children[0].children[1].value
                type = SymbolTableObject[
                    symbol_table[(self.current_scope, name)]].type

                self.stack.append(
                    [self.current_scope + "/" + name, type])
                mips_code += '.text\n'

                if type.name == 'double' and type.dimension == 0:
                    mips_code += '\tl.d  $f0, {}\n'.format((self.current_scope + "/" + name).replace("/", "_")) + \
                                 '\taddi $sp, $sp, -8\n' + \
                                 '\ts.d  $f0, 0($sp)\n\n'
                else:
                    mips_code += '\tla   $t0, {}\n'.format((self.current_scope + "/" + name).replace("/", "_")) + \
                                 '\tlw   $t1, 0($t0)\n' + \
                                 '\taddi $sp, $sp, -8\n' + '\tsw   $t1, 0($sp)\n\n'

            else:
                mips_code += self.visit(child)

         # remove  variables

        for node in reversed(parse_tree.children):
            if node.data == 'variable_decl':

                self.stack_local_params_count[-1] -= 1
                variable_name = child.children[0].children[1].value
                variable_type = SymbolTableObject[symbol_table[(self.current_scope, variable_name)]].type
                self.stack_local_params.pop()

                mips_code += '.text\n'

                if variable_type.name == 'double' and variable_type.dimension == 0:
                    mips_code += '\tl.d  $f0, 0($sp)\n' + '\taddi $sp, $sp, 8\n' + \
                                 '\ts.d  $f0, {}\n\n'.format((self.current_scope + "/" + variable_name).replace("/", "_"))

                else:
                    mips_code += '\tlw   $t1, 0($sp)\n'+\
                            '\taddi $sp, $sp, 8\n' + \
                            '\tla   $t0, {}\n'.format((self.current_scope + "/" + variable_name).replace("/", "_")) + '\tsw   $t1, 0($t0)\n\n'


        mips_code += 'end_stmt_{}:\n'.format(stmt_num)


        self.stmt_labels = self.stmt_labels[:len(self.stmtLabels)]
        self.stmt_labels.append(stmt_num)
        self.current_scope = POP(self.current_scope)
        return mips_code





    def stmt(self, parse_tree):

        #stmt : (expr)? ";"
        # | if_stmt
        # | while_stmt
        # | for_stmt
        # | break_stmt
        # | continue_stmt
        # | return_stmt
        # | print_stmt
        # | stmt_block

        mips_code = ''

        node = parse_tree.children[0]

        if node.data == 'for_stmt':
            if node.children[0].data == 'assignment':
                mips_code += self.visit(node.children[0])
                mips_code += '\taddi $sp, $sp, 8\n'

        stmt_num  = labelCounter()
        mips_code += ('start_stmt_{}:\n'.format(stmt_num))

        node._meta = stmt_num

        if node.data == 'if_stmt':
            mips_code += self.visit(node)

        elif mips_code.data == 'while_stmt':
            mips_code += self.visit(node)

        elif node.data == 'for_stmt':
            mips_code += self.visit(node)

        elif node.data == 'stmt_block':
            mips_code += self.visit(node)

        elif node.data == 'break_stmt':  # there is a problem with it !
            mips_code += self.visit(node)

        elif node.data == 'return_stmt':
            mips_code += self.visit(node)
            func_name = ''

            if '__class__' in self.current_scope:
                func_name = self.current_scope.split('/')[2]
                class_name = self.current_scope.split('/')[1][9:]
                funct = class_type_objects[class_table[class_name]].find_function(func_name)
            else:
                func_name = self.current_scope.split('/')[1]
                funct = function_objects[function_table[func_name]]


            if funct.return_type.name == 'double' and funct.return_type.dimension == 0:
                mips_code += '\tl.d   $f30, 0($sp)\n' + '\taddi $sp, $sp, 8\n'

            elif funct.return_type.name != 'void':
                mips_code += '\tlw   $t8, 0($sp)\n' + '\taddi $sp, $sp, 8\n'


            for local_var in reversed(self.stack_local_params[-self.stack[-1]:]):
                name = local_var[0]
                type = local_var[1]
                mips_code += '.text\n'
                if type.name == 'double' and type.dimension == 0:
                   mips_code = '\tl.d  $f0, 0($sp)\n' + \
                            '\taddi $sp, $sp, 8\n'+ \
                            '\ts.d  $f0, {}\n\n'.format(name.replace("/", "_"))
                else:
                    mips_code += '\tlw   $t0, 0($sp)\n'
                    mips_code += '\taddi $sp, $sp, 8\n'
                    mips_code += '\tsw   $t0, {}\n\n'.format(name.replace("/", "_"))

            if funct.return_type.name != 'void':
                mips_code += '\taddi $sp, $sp, -8\n'
                mips_code += '\tsw   $t8, 0($sp)\n'

            elif funct.return_type.name == 'double' and funct.return_type.dimension == 0:
                 mips_code += '\taddi $sp, $sp, -8\n'
                 mips_code += '\ts.d   $f30, 0($sp)\n'

            mips_code += '\tjr   $ra\n\n'

        elif node.data == 'expr' or node.data == 'assignment':
            mips_code += self.visit(node)
            expr_type = self.expressionTypes[-1]

            if expr_type.name != 'void':
                mips_code += '.text\n' + '\taddi\t$sp, $sp, 8\n\n'
            self.expr_types.pop()

        elif node.data == 'print_stmt':
            mips_code += self.visit(node)

        else:
            mips_code += self.visit(node)


        mips_code += 'end_stmt_{}:\n'.format(stmt_num)
        self.stmtLabels = self.stmt_labels[:len(self.stmtLabels)]
        self.stmtLabels.append(stmt_num)
        return mips_code

    def if_stmt(self, parse_tree):

        mips_code = ' '
        mips_code += self.visit(parse_tree.children[0])

        then_label = labelCounter()
        else_label = labelCounter()

        """
        if (true)
            a = b;
        """

        then_mipscode = self.visit(parse_tree.children[1])
        else_mipscode = '' if len(parse_tree.children) == 2 else self.visit(parse_tree.children[2])
        if len(parse_tree.children) == 2:
            mips_code += make_indentation(
                """
                .text\t\t\t\t#If
                    lw $a0, 0($sp)
                    addi $sp, $sp, 8
                    beq $a0, 0, end_stmt_{then}
                    j  start_stmt_{then}
                """.format(then=then_label)
            )
            mips_code += '\tstart_stmt_{}:\n'.format(then_label)
            mips_code += then_mipscode
            mips_code += '\tend_stmt_{}:\n'.format(then_label)
        else:
            mips_code += make_indentation("""
                .text\t\t\t\t# IfElse
                    lw $a0, 0($sp)
                    addi $sp, $sp, 8
                    beq $a0, 0, start_stmt_{els}
                """.format(els=else_label))

            mips_code += '\tstart_stmt_{}:\n'.format(then_label)
            mips_code += then_mipscode
            mips_code += '\tend_stmt_{}:\n'.format(then_label)
            mips_code += make_indentation("j end_stmt_{els}".format(els=else_label))
            mips_code += '\tstart_stmt_{}:\n'.format(else_label)
            mips_code += else_mipscode
            mips_code += '\tend_stmt_{}:\n'.format(else_label)
        return mips_code

    def while_stmt(self, parse_tree):
        mips_code = ''
        #while count= parse_tree._meta
        self.loopLabels.append(parse_tree._meta)

        mips_code += '.text\t\t\t\t# While\n'

        mips_code += self.visit(parse_tree.children[0])
        stmt_code = self.visit(parse_tree.children[1])

        mips_code += make_indentation("""
            lw $a0, 0($sp)
            addi $sp, $sp, 8
            beq $a0, 0, end_stmt_{while_end}
        """.format(while_end=parse_tree._meta))
        mips_code += stmt_code
        mips_code += make_indentation("j start_stmt_{while_start}".format(while_start=parse_tree._meta))

        self.stmt_labels = self.stmt_labels[:len(self.stmtLabels)]
        self.loopLabels.pop()
        return mips_code

    def for_stmt(self, parse_tree):
        mips_code = ''
        mips_code += '.text\t\t\t\t# For\n'  # todo check this comment
        #for_count = parse_tree._meta

        self.loopLabels.append(parse_tree._meta)

        children = parse_tree.children
        next = ''
        if children[0].data == 'assignment':
            mips_code += self.visit(children[1])
        else:
            mips_code += self.visit(children[0])
        if children[-2].data == 'assignment':
            next += self.visit(children[-2])
            next += '\taddi $sp, $sp, 8\n'
        mips_code += make_indentation("""
            lw $a0, 0($sp)
            addi $sp, $sp, 8
            beq $a0, $zero, end_stmt_{}
        """.format(parse_tree._meta))


        mips_code += self.visit(children[-1])
        mips_code += next
        mips_code += "\tj start_stmt_{}\n".format(parse_tree._meta)
        self.loopLabels.pop()
        return mips_code


    def return_stmt(self, parse_tree):
        return ''.join(self.visit_children(parse_tree))

    def break_stmt(self):
        mips_code = make_indentation("""
        
            .text\t\t\t\t# break
                j end_stmt_{}
            ##             
        """.format(self.loopLabels[-1]))
        return mips_code

    def continue_stmt(self, parse_tree):
        return code

    def print(self, parse_tree):
        mips_code = ''
        for ch in parse_tree.children[0].children:
            mips_code += self.visit(ch)
            t = self.expr_types[-1]
            self.expr_types.pop()
            mips_code += '.text\n'

            ###### double
            if t.name == 'double':

                mips_code += make_indentation("""
                    l.d $f12, 0($sp)
                    addi $sp, $sp, 8
                    cvt.s.d $f12, $f12
                    li $v0, 2
                    syscall
                """)


            ###### int
            elif t.name == 'int':
                mips_code += make_indentation("""
                    # Print int
                        li $v0, 1
                        lw $a0, 0($sp)
                        addi $sp, $sp, 8
                        syscall             #Print int
                    ##
                """)

            ###### string

            elif t.name == 'string':
                mips_code += make_indentation(
                    """
                    # Print string
                        li $v0, 4
                        lw $a0, 0($sp)
                        addi $sp, $sp, 8
                        syscall             #Print string
                    ##
                    """)
             ###### bool

            elif t.name == 'bool' and t.dimension == 0:
                mips_code += make_indentation(
                    """
                    # Print bool
                        lw $a0, 0($sp)
                        addi $sp, $sp, 8
                        beq $a0, 0, zero_{cnt}
                        li $v0, 4
                        la $a0, true
                        syscall
                        j ezero_{cnt}
                        zero_{cnt}:
                        li $v0, 4
                        la $a0, false
                        syscall             #Print bool
                        ezero_{cnt}:
                    ##
                    """.format(cnt=labelCounter())
                )
            # '\n' at the end of print

        mips_code += make_indentation(
            """
            # Print new line
                li $v0, 4
                la $a0, nw
                syscall\t\t\t\t#Print new line\n
            ##
            """)
        return mips_code

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
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes[-1]
        if t.name == 'double' and t.dimension == 0:
            mips_code += """.text\n
                \tlw $t0, 8($sp)\n
                \tl.d $f0, 0($sp)\n
                \ts.d $f0, 0($t0)\n
                \ts.d $f0, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        else:
            mips_code += """.text\n
                \tlw $t0, 8($sp)\n
                \tlw $t1, 0($sp)\n
                \tsw $t1, 0($t0)\n
                \tsw $t1, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        self.expressionTypes.pop()
        return mips_code

    def logical_or(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        self.expressionTypes.pop()
        self.expressionTypes.pop()
        mips_code += """.text\n
            \tlw $t0, 0($sp)\n
            \tlw $t1, 8($sp)\n
            \tor $t2, $t1, $t0\n
            \tsw $t2, 8($sp)\n
            \taddi $sp, $sp, 8\n\n"""
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def logical_and(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        self.expressionTypes.pop()
        self.expressionTypes.pop()
        mips_code += """.text\n
            \tlw $t0, 0($sp)\n
            \tlw $t1, 8($sp)\n
            \tand $t2, $t1, $t0\n
            \tsw $t2, 8($sp)\n
            \taddi $sp, $sp, 8\n\n"""
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def equals(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'double' and t.dimension == 0:
            c = labelCounter()
            mips_code += """.text\n
                \tli $t0, 0\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tc.eq.d $f0, $f2\n
                \tbc1f _eq.d.{}\n
                \tli $t0, 1\n'
                _eq.d.{}:\tsw $t0, 8($sp)\n
                \taddi $sp, $sp, 8\n\n""".format(c, c)
        elif t.name == 'string' and t.dimension == 0:
            mips_code += """.text\n
                \tsw $t0, -8($sp)\n
                \tsw $t1, -8($sp)\n
                \tsw $a0, -12($sp)\n
                \tsw $a1, -16($sp)\n
                \tsw $v0, -20($sp)\n
                \tsw $ra, -24($sp)\n
                \tlw $a0, 0($sp)\n
                \tlw $a1, 8($sp)\n
                \tjal __strcmp__\n
                \tsw $v0, 8($sp)\n
                \tlw $t0, -4($sp)\n
                \tlw $t1, -8($sp)\n
                \tlw $a0, -12($sp)\n
                \tlw $a1, -16($sp)\n
                \tlw $v0, -20($sp)\n
                \tlw $ra, -24($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        elif self:
            mips_code += """.text\n'
                \tlw $t0, 0($sp)\n'
                \tlw $t1, 8($sp)\n'
                \tseq $t2, $t1, $t0\n'
                \tsw $t2, 8($sp)\n'
                \taddi $sp, $sp, 8\n\n"""
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def not_equals(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'double' and t.dimension == 0:
            c = labelCounter()
            mips_code += """.text\n
                \tli $t0, 0\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tc.eq.d $f0, $f2\n
                \tbc1t _neq.d.{}\n
                \tli $t0, 1\n'
                _neq.d.{}:\tsw $t0, 8($sp)\n
                \taddi $sp, $sp, 8\n\n""".format(c, c)
        elif t.name == 'string' and t.dimension == 0:
            mips_code += """.text\n
                \tsw $t0, -8($sp)\n
                \tsw $t1, -8($sp)\n
                \tsw $a0, -12($sp)\n
                \tsw $a1, -16($sp)\n
                \tsw $v0, -20($sp)\n
                \tsw $ra, -24($sp)\n
                \tlw $a0, 0($sp)\n
                \tlw $a1, 8($sp)\n
                \tjal __strcmp__\n
                \tli $t0, 1\n
                \tsub $v0, $t0, $v0\n
                \tsw $v0, 8($sp)\n
                \tlw $t0, -4($sp)\n
                \tlw $t1, -8($sp)\n
                \tlw $a0, -12($sp)\n
                \tlw $a1, -16($sp)\n
                \tlw $v0, -20($sp)\n
                \tlw $ra, -24($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        elif self:
            mips_code += """.text\n'
                \tlw $t0, 0($sp)\n'
                \tlw $t1, 8($sp)\n'
                \tsne $t2, $t1, $t0\n'
                \tsw $t2, 8($sp)\n'
                \taddi $sp, $sp, 8\n\n"""
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def lt(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tslt $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text\n
                \tli $t0, 0\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tc.lt.d $f2, $f0\n
                \tbc1f _lt.d.{}\n
                \tli $t0, 1\n
                _lt.d.{}:\tsw $t0, 8($sp)\n
                \taddi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def lte(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tsle $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text\n
                \tli $t0, 0\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tc.le.d $f2, $f0\n
                \tbc1f _lte.d.{}\n
                \tli $t0, 1\n
                _lte.d.{}:\tsw $t0, 8($sp)\n   
                \taddi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def gt(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tsgt $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text\n
                \tli $t0, 0\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tc.le.d $f2, $f0\n
                \tbc1t _gt.d.{}\n
                \tli $t0, 1\n
                _gt.d.{}:\tsw $t0, 8($sp)\n
                \taddi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def gte(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\n
                        \tlw $t0, 0($sp)\n
                        \tlw $t1, 8($sp)\n
                        \tsge $t2, $t1, $t0\n
                        \tsw $t2, 8($sp)\n
                        \taddi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text\n
                        \tli $t0, 0\n
                        \tl.d $f0, 0($sp)\n
                        \tl.d $f2, 8($sp)\n
                        \tc.lt.d $f2, $f0\n
                        \tbc1t _gte.d.{}\n
                        \tli $t0, 1\n
                        _gte.d.{}:\tsw $t0, 8($sp)\n
                        \taddi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def sum(self, parse_tree):
        pass

    def sub(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tsub $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        else:
            mips_code += """.text\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tsub.d $f4, $f2, $f0\n
                \ts.d $f4, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        return mips_code

    def mul(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\n
                \tlw   $t0, 0($sp)\n
                \tlw   $t1, 8($sp)\n
                \tmul  $t2, $t1, $t0\n
                \tsw   $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            mips_code += """.text\n
                \tl.d      $f0, 0($sp)\n
                \tl.d      $f2, 8($sp)\n
                \tmul.d    $f4, $f2, $f0\n
                \ts.d      $f4, 8($sp)\n
                \taddi     $sp, $sp, 8\n\n"""
        return mips_code

    def div(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tdiv $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            mips_code += """.text\n
                \tl.d $f0, 0($sp)\n
                \tl.d $f2, 8($sp)\n
                \tdiv.d $f4, $f2, $f0\n
                \ts.d $f4, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        return mips_code

    def mod(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        mips_code += """.text\n
            \tlw $t0, 0($sp)\n
            \tlw $t1, 8($sp)\n
            \tdiv $t1, $t0\n
            \tmfhi $t2\n
            \tsw $t2, 8($sp)\n
            \taddi $sp, $sp, 8\n"""
        self.expressionTypes.pop()
        return mips_code

    def minus(self, parse_tree):
        mips_code = ''

        mips_code += ''.join(self.visit_children(parse_tree))
        typ = self.expressionTypes.pop()
        if typ.name == 'int':
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t1, 8($sp)\n
                \tsub $t2, $t1, $t0\n
                \tsw $t2, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        else:
            mips_code += """.text\n
            \tl.d $f0, 0($sp)\n
            \tl.d $f2, 8($sp)\n
            \tsub.d $f4, $f2, $f0\n
            \ts.d $f4, 8($sp)\n
            \taddi $sp, $sp, 8\n\n"""

        return mips_code


    def logical_not(self, parse_tree):

        mips_code = ''.join(self.visit_children(parse_tree))

        mips_code += make_indentation("""
            .text\t\t\t\t # Not
                lw $t0, 0($sp)
                addi $sp, $sp, 8
                li $t1, 1
                beq $t0, 0, not_{0}
                    li $t1, 0
                not_{0}:
                    sub  $sp, $sp, 8
                    sw $t1, 0($sp)
            ##
        """.format(labelCounter()))

        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code


    def read_char(self):
        mips_code = ''

        mips_code += make_indentation(
            """
             .text\t\t\t\t # Read Integer
                 li $v0, 12           #read_char
                 syscall             #ReadChar
                 sub $sp, $sp, 8
                 sw $v0, 0($sp)
             ##
             """)
        self.expressionTypes.append(Type('int'))
        return mips_code


    def read_int(self):
        mips_code = ''

        mips_code += make_indentation(
            """
        	addi $sp, $sp, -8
            sw   $ra, 0($sp)
            jal root_ReadInteger__
            lw   $t8, 0($sp)
            addi $sp, $sp, 8
            lw   $ra, 0($sp)
            addi $sp, $sp, 8
        
            addi $sp, $sp, -8
            sw   $t8, 0($sp)
        """)
        self.expressionTypes.append(Type('int'))
        return mips_code


    def read_line(self):

        mips_code =''
        mips_code += make_indentation(
             """
        .text\t\t\t\t # Read Line
            li $a0, 256         #Maximum string length
            li $v0, 9           #sbrk
            syscall
            sub $sp, $sp, 8
            sw $v0, 0($sp)
            move $a0, $v0
            li $a1, 256         #Maximum string length (incl. null)
            li $v0, 8           #read_string
            syscall             #ReadLine()
            
            lw $a0, 0($sp)      #Replace \\n to \\r(?)
            lb $t1, nw
            
            # li $v0, 1
            # addi $a0, $t1, 0
            # syscall
            
            # li $v0, 10
            # syscall
            
            
            read_{label_id}:
                lb $t0, 0($a0)
                
                # addi $a3, $a0, 0
                # 
                # li $a0, '$'
                # li $v0, 11
                # syscall
                # 
                # 
                # addi $a0, $t0, 0
                # li $v0, 1
                # syscall
                # 
                # li $a0, ' '
                # li $v0, 11
                # syscall
                # 
                # li $a0, '$'
                # li $v0, 11
                # syscall
                # 
                # 
                # addi $a0, 0
                # addi $a0, $a3, 0
                beq $t0, 0, e_read_{label_id}
                bne $t0, 10, ten_{ten}
                li $t2, 0
                sb $t2, 0($a0)
                ten_{ten}:
                
                bne $t0, 13, thirt_{thirt}
                li $t2, 0
                sb $t2, 0($a0)
                thirt_{thirt}:
                
                
                addi $a0, $a0, 1
                j read_{label_id}
            e_read_{label_id}:
                # # lb $t2, 1($a0)
                # li $t2, 0
                # sb $t2, -1($a0)
            
            # li $v0, 10
            # lw $a0, 0($sp)
            # syscall
        ##
        """.format(label_id=labelCounter(), ten=labelCounter(), thirt=labelCounter()))

        self.expressionTypes.append(Type('string'))
        return mips_code


    def new_class(self, parse_tree):
        pass

    def new_array(self, parse_tree):
        mips_code = ''
        mips_code += ''.join(self.visit_children(parse_tree))
        shamt = 2
        if type(parse_tree.children[1].children[0]) == lark.lexer.Token:
            if parse_tree.children[1].children[0].value == 'bool':
                shamt = 3

        ## we store size of array in 8 bytes before start pointer of array

        mips_code += make_indentation("""
            .text\t\t\t\t # New array
                lw $a0, 0($sp)
                addi $sp, $sp, 8
                addi $t6, $a0, 0 # t6 is length of array
                sll $a0, $a0, {shamt}
                addi $a0, $a0, 8 # extra 8 bytes for length
                li $v0, 9           #rsbrk
                syscall
                sw $t6 0($v0)
                addi $v0, $v0, 8
                sub $sp, $sp, 8
                sw $v0, 0($sp)\n
            ##
        """.format(shamt=shamt))

        self.expressionTypes.append(Type(name=self.lastType.name, dimension= self.lastType.size + 1))
        return mips_code


    def val(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes[-1]
        if t.name == 'double' and t.dimension == 0:
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tl.d $f0, 0($t0)\n
                \ts.d $f0, 0($sp)\n\n"""
        else:
            mips_code += """.text\n
                \tlw $t0, 0($sp)\n
                \tlw $t0, 0($t0)\n
                \tsw $t0, 0($sp)\n\n"""
        return mips_code

    def ident_l_value(self, parse_tree):
        name = parse_tree.children[0].value
        scope = self.current_scope
        while (scope, name) not in symbol_table:
            if '__class__' in scope.split('/')[-1]:
                class_name = scope.split('/')[-1][9:]
                if class_type_objects[class_table[class_name]].find_var_index(name) >= 0:
                    break
            scope = POP(scope)
        if '__class__' in scope.split('/')[-1]:
            classObject = class_type_objects[class_table[scope.split('/')[-1][9:]]]
            index = classObject.find_var_index(name)
            if index >= 0:
                function_name = deepcopy(self.current_scope).split('/')
                while function_name[-1] != '_local':
                    function_name.pop()
                function_name.pop()
                mips_code = """.text\n
                    \tlw $t0, 0($fp)\n
                    \taddi $t1, $t0, {}\n
                    \tsub $sp, $sp, 8\n
                    \tsw $t1, 0($sp)\n""".format(index * 8 + 8)
                self.expressionTypes.append(deepcopy(classObject.find_var_type(name)))
                return mips_code
        if len(scope.split('/')) == 3 and '__class__' in scope.split('/')[1]:
            class_name = scope.split('/')[1][9:]
            function = class_type_objects[class_table[class_name]].find_function(scope.split('/')[-1])
            formal_type, index = function.find_formal(name)
            mips_code = """.text\n
                \taddi $t0, $fp, -{}\n
                \tsub $sp, $sp, 8\n
                \tsw $t0, 0($sp)\n""".format(index * 8)
            self.expressionTypes.append(deepcopy(formal_type[1]))
            return mips_code
        label_name = scope.replace('/', '_') + '_' + name
        mips_code = """.text\n
            \tla $t0, {}\n
            \tsub $sp, $sp, 8\n
            \tsw $t0, 0($sp)\n\n""".format(label_name)
        t = st_objects[symbol_table[scope, name]].type
        self.expressionTypes.append(deepcopy(t))
        return mips_code

    def mem_access_l_value(self, parse_tree):
        mips_code = self.visit(parse_tree.children[0])
        id = parse_tree.children[1].value
        mips_code += """.text\n
            \tlw $t0, 0($sp)\n"""
        class_type = self.expressionTypes[-1]
        index = class_type_objects[class_table[class_type.name]].find_var_index(id)
        t = class_type_objects[class_table[class_type.name]].find_var_type(id)
        mips_code += """\taddi $t1, $t0, {}\n
            \tsw $t1, 0($sp)\n""".format((1 + index) * 8)
        self.expressionTypes.pop()
        self.expressionTypes.append(t)
        return mips_code

    def array_access_l_value(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        self.expressionTypes.pop()
        t = self.expressionTypes[-1]
        if t.name == 'double' and t.dimension == 1:
            mips_code += """.text\n
                \tlw $t7, 8($sp)\n
                \tlw $t0, 0($sp)\n
                \tli $t1, 8\n
                \tmul $t0, $t0, $t1\n
                \tadd $t1, $t0, $t7\n
                \tsw $t1, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        else:
            mips_code += """.text\n
                \tlw $t7, 8($sp)\n
                \tlw $t0, 0($sp)\n
                \tli $t1, 4\n
                \tmul $t0, $t0, $t1\n
                \tadd $t1, $t0, $t7\n
                \tsw $t1, 8($sp)\n
                \taddi $sp, $sp, 8\n\n"""
        self.expressionTypes[-1].dimension -= 1
        return mips_code

    def method_call(self, parse_tree):
        pass

    def l_value(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        return mips_code

    def call(self, parse_tree):
        mips_code = ''
         # self.expr_types
        if len(parse_tree.children) == 3:
            code = self.visit(parse_tree.children[0])
            if self.expr_types[-1].dimension > 0:
                mips_code += """
                .text\n
                \tlw $t0, 0($sp)\n'
                \tlw $t0, -8($t0)\n'
                \tsw $t0, 0($sp)\n\n"""

                self.expressionTypes.pop()
                self.expressionTypes.append(Type('int'))
                return code
            else:
                self.expressionTypes.pop()
                expr_class_inst = parse_tree.children[0]
                ident = parse_tree.children[1]
                actuals = parse_tree.children[2]
                name = ident.value

                actuals._meta = [name, expr_class_inst]
                return self.visit(actuals)
            # for class
        if len(parse_tree.children) == 2:
            ident = parse_tree.children[0]
            actuals = parse_tree.children[1]
            name = ident.value

            actuals._meta = [name, None]
            return self.visit(actuals)

    def actuals(self, parse_tree):
        mips_code = ''
        mips_code += '.text\n'

        func_name = parse_tree._meta[0]
        if parse_tree._meta[1]:
            expr = parse_tree._meta[1]
            tmp = self.visit(expr)
            class_type = self.expressionTypes[-1]
            self.expressionTypes.pop()
            function_scope = 'root/__class__' + class_type.name + '/' + func_name
            function = class_type_objects[class_table[class_type.name]].find_function(name=func_name)
        else:
            function_scope = 'root/' + func_name
            function = function_objects[function_table[func_name]]

        # push formal parameter
        for formal in function.formals:
            exact_name = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expressionTypes[-1]
                self.expressionTypes.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == parse_tree:
                        exact_name = funct.exact_name
            formal_name = (exact_name + "/" + formal[0]).replace("/", "_")
            formal_type = formal[1]
            if formal_type.name == 'double' and formal_type.dimension == 0:
                mips_code += '\tl.d  $f0, {}\n'.format(formal_name)
                mips_code += """
                \taddi $sp, $sp, -8\n
                \ts.d  $f0, 0($sp)\n\n"""
            else:
                mips_code += '\tlw   $t1, {}\n'.format(formal_name)
                mips_code += """
                \taddi $sp, $sp, -8\n
                \tsw   $t1, 0($sp)\n\n"""


        # set actual parameters to formal parameters

        if parse_tree._meta[1]:
            exact_name = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expressionTypes[-1]
                self.expressionTypes.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == func_name:
                        exact_name = funct.exact_name
            formal_name = (exact_name + "/" + function.formals[0][0]).replace("/", "_")
            # todo is it really a pointer or it's just a name?
            expr = parse_tree._meta[1]
            mips_code += self.visit(expr)
            mips_code += '.text\n'
            mips_code += '\tlw $v0, 0($sp)\n'  # we don't use type because we are sure that it's class
            mips_code += '\tsw $v0, {}\n'.format(formal_name)
            mips_code += '\taddi $sp, $sp, 8\n'
            self.expr_types.pop()
            actual_counter = 1
        else:
            actual_counter = 0

        for expr in parse_tree.children:
            exact_name = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expressionTypes[-1]
                self.expressionTypes.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == func_name:
                        exact_name = funct.exact_name
            mips_code += self.visit(expr)
            formal_name = (exact_name + "/" + function.formals[actual_counter][0]).replace("/", "_")
            mips_code += '.text\n'
            formal_type = function.formals[actual_counter][1]
            if formal_type.name == 'double' and formal_type.dimension == 0:
                mips_code += '\tl.d  $f0, 0($sp)\n'
                mips_code += '\ts.d  $f0, {}\n'.format(formal_name)
                mips_code += '\taddi $sp, $sp, 8\n\n'
            else:
                mips_code += '\tlw   $v0, 0($sp)\n'
                mips_code += '\tsw   $v0, {}\n'.format(formal_name)  # herererere
                mips_code += '\taddi $sp, $sp, 8\n\n'
            actual_counter += 1
            self.expr_types.pop()  # todo check f(double, double) + g(double, double) f: int g: int

        mips_code += '.text\n'
        mips_code += '\taddi $sp, $sp, -8\n'
        mips_code += '\tsw   $ra, 0($sp)\n'

        if parse_tree._meta[1]:  # E1.ident(E1, expr, expr, ...)
            expr = parse_tree._meta[1]
            mips_code += self.visit(expr)
            class_type = self.expr_types[-1]
            self.expr_types.pop()
            index = class_type_objects[class_table[class_type.name]].find_function_index(func_name)
            mips_code += """.text\n
            \tlw $t0, 0($sp)\n
            \taddi $sp, $sp, 8\n
            \tlw $t0, 0($t0)\n"""

            mips_code += '\taddi $t0, $t0, {}\n'.format(4 * index)
            mips_code += """ 
            \tlw $t0, 0($t0)\n
            \tjalr $t0\n"""
        else:
            label_name = function.exact_name
            mips_code += '\tjal {}\n'.format(label_name.replace('/', '_'))

        if function.return_type.name == 'double' and function.return_type.dimension == 0:
            mips_code += """
             \tl.d   $f30, 0($sp)\n
             \taddi $sp, $sp, 8\n"""

        elif function.return_type.name != 'void':
            mips_code += '\tlw   $t8, 0($sp)\n'
            mips_code += '\taddi $sp, $sp, 8\n'

        mips_code += '\tlw   $ra, 0($sp)\n'
        mips_code += '\taddi $sp, $sp, 8\n\n'

        # pop formal parameters
        for formal in reversed(function.formals):
            exact_name = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expr_types[-1]
                self.expr_types.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == func_name:
                        exact_name = funct.exact_name
            formal_name = (exact_name + "/" + formal[0]).replace("/", "_")
            formal_type = formal[1]
            if formal_type.name == 'double' and formal_type.dimension == 0:
                mips_code += """
                \tl.d  $f0, 0($sp)\n
                \taddi $sp, $sp, 8\n"""
                mips_code += '\ts.d  $f0, {}\n\n'.format(formal_name)
            else:
                mips_code += '\tlw   $t0, 0($sp)\n'
                mips_code += '\taddi $sp, $sp, 8\n'
                mips_code += '\tsw   $t0, {}\n\n'.format(formal_name)
        if function.return_type.name == 'double' and function.return_type.dimension == 0:
            mips_code += '\taddi $sp, $sp, -8\n'
            mips_code += '\ts.d   $f30, 0($sp)\n'
        elif function.return_type.name != 'void':
            mips_code += '\taddi $sp, $sp, -8\n'
            mips_code += '\tsw   $t8, 0($sp)\n'
        mips_code += '# return type is ' + function.return_type.name + ' ' + str(function.return_type.dimension)
        mips_code += '\n'
        self.expressionTypes.append(deepcopy(function.return_type))
        return mips_code



    def int_push(self, parse_tree):

        mips_code = ''
        val = parse_tree.children[0].value.lower()
        mips_code += '.text\n'
        mips_code += '\tli $t0, {}\n'.format(val)
        mips_code += '\tsub $sp, $sp, 8\n'
        mips_code += '\tsw $t0, 0($sp)\n\n'

        self.expressionTypes.append(Type('int'))
        return mips_code



    def double_push(self, parse_tree):
        mips_code = ''
        val = parse_tree.children[0].value.lower()
        if val[-1] == '.':
            val += '0'
        if '.e' in val:
            index = val.find('.e') + 1
            dval = val[:index] + '0' + val[index:]
        mips_code += '.text\n'
        mips_code += '\tli.d $f0, {}\n'.format(val)
        mips_code += '\tsub $sp, $sp, 8\n'
        mips_code += '\ts.d $f0, 0($sp)\n\n'
        self.expressionTypes.append(Type('double'))
        return mips_code


    def bool_push(self, parse_tree):
        mips_code = ''
        val = 0
        if int(parse_tree.children[0].value == 'true'):
            val = 1

        mips_code += '.text\n'
        mips_code += '\tli $t0, {}\n'.format(val)
        mips_code += '\tsub $sp, $sp, 8\n'
        mips_code += '\tsw $t0, 0($sp)\n'
        self.expressionTypes.append(Type('bool'))
        return mips_code


    def string_push(self, parse_tree):
        mips_code = ''
        mips_code += '.data\n'
        mips_code += '.align 2\n'
        mips_code += '__const_str__{}: .asciiz {}\n'.format(self.string_counter, parse_tree.children[0].value)
        mips_code += '.text\n'
        mips_code += '\tla $t0, __const_str__{}\n'.format(self.string_counter)
        mips_code += '\tsub $sp, $sp, 8\n'
        mips_code += '\tsw $t0, 0($sp)\n\n'
        self.string_counter += 1
        self.expressionTypes.append(Type('string'))
        return mips_code

    def null(self):
        mips_code = """.text\n
            \tsub $sp, $sp, 8\n
            \tsw $zero, 0($sp)\n\n"""
        self.expressionTypes.append(Type('null'))
        return mips_code

    def get_type(self, typ):

        if type(typ) == lark.lexer.Token:
            return Type(typ)

        ret = self.get_type(typ.children[0])
        ret.dimension += 1
        return ret



def decafCGEN(code):
    parser = Lark(Grammar, parser="lalr")
    parse_tree = parser.parse(code)
    SymbolTable().visit(parse_tree)
    ParentTree().visit(parse_tree)
    set_parents()
    Traversal().visit(parse_tree)
    mips_code = CodeGenerator().visit(parse_tree)
    return mips_code


if __name__ == '__main__':
    print(decafCGEN(code))
