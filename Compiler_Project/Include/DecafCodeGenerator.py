from SymbolTable import *
from traversal import *
from function import make_indentation
from LibFunctionCodeGenerator import primitve_inst
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
            if decl.data == 'variable_decl' or decl.data == 'function_decl' or decl.data=='class_decl':
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
                mips_code += self.current_scope.replace('/', '_') + '_' + variable.children[1] + ': .space' + str(
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

        return ''

    def function_decl(self, parse_tree):

        mips_code = ''
        ##### "void" IDENT "("formals")" stmt_block
        if len(parse_tree.children) == 4:
            ident = parse_tree.children[1]
            formals = parse_tree.children[2]
            stmt_block = parse_tree.children[3]


        ###### type IDENT "("formals")" stmt_block
        else:
            ident = parse_tree.children[0]
            formals = parse_tree.children[1]
            stmt_block = parse_tree.children[2]



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

            mips_code += primitve_inst()
            mips_code += ('.text\n'
                          'main:\n')

            for clas in range(len(class_table)):
                mips_code += '\tjal __init__vtable_{}\n'.format(clas)

            mips_code += '\tla\t$ra,__end__\n'

        else:
            mips_code += '.text\n{}:\n'.format((self.current_scope + '/' + ident).replace('/', '_'))



        self.current_scope += "/" + ident.value

        ####### formal

        mips_code += self.visit(formals)
        self.current_scope += "/_local"
        self.stack_counter.append(0)


        if ident != "main":
            tree_children = [Tree(data='return_stmt', children=[])]
            return_stmt = Tree(data="stmt", children=tree_children)
            stmt_block._meta = return_stmt



        ####### stmt_block
        mips_code += self.visit(stmt_block)



        locals_cnt = self.stack_counter[-1]
        self.stack = self.stack[:-locals_cnt]
        self.stack_counter.pop()
        # remove local from scope
        self.current_scope = POP(self.current_scope)
        # remove formals from scope
        self.current_scope = POP(self.current_scope)

        if ident == 'main':
            mips_code += '.text\n'
            mips_code +='__end__:\n'
            mips_code +='\tli $v0, 10\t\t\t#exit\n'
            mips_code +='\tsyscall\n'

        return mips_code

    def formals(self, parse_tree):
        #  formals : variable (","variable)*
        mips_code = ''
        for variable in parse_tree.children:
            name = variable.children[1].value


            f_type = st_objects[symbol_table[(self.current_scope, name)]].type



            mips_code += '.data\n'
            mips_code +='.align 2\n'
            default_size = 4

            if f_type.name == 'double' and f_type.size == 0:
                mips_code += '{}: .space 8\n'.format((self.current_scope + "/" + name).replace("/", "_"))
            else:
                mips_code += '{}: .space 4\n'.format((self.current_scope + "/" + name).replace("/", "_"))
            # if f_type.name == 'double' and f_type.size == 0:
            #     default_size = 8

            # mips_code += '{}: .space {}\n'.format((self.current_scope + "/" + name).replace("/", "_"), default_size)

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

        mips_code = ''
        self.current_scope += "/" + str(self.block_stmt_counter)
        self.block_stmt_counter += 1
        stmt_num = labelCounter()
        mips_code += '.text\nstart_stmt_{}:\n'.format(stmt_num)

        if type(parse_tree._meta) == lark.tree.Tree:
            return_stmt = parse_tree._meta
            parse_tree.children.append(return_stmt)

        for child in parse_tree.children:
            if child.data == 'variable_decl':

                mips_code += self.visit(child)
                self.stack_counter[-1] += 1

                var_name = child.children[0].children[1].value
                var_type = st_objects[symbol_table[(self.current_scope, var_name)]].type


                self.stack.append(
                    [self.current_scope + "/" + var_name, var_type])
                mips_code += '.text\n'

                if var_type.name == 'double' and var_type.size == 0:
                    mips_code += '\tl.d  $f0, {}\n'.format((self.current_scope + "/" + var_name).replace("/", "_"))
                    mips_code += '\taddi $sp, $sp, -8\n'
                    mips_code += '\ts.d  $f0, 0($sp)\n\n'
                else:
                    mips_code += '\tla   $t0, {}\n'.format((self.current_scope + "/" + var_name).replace("/", "_"))
                    mips_code += '\tlw   $t1, 0($t0)\n'
                    mips_code += '\taddi $sp, $sp, -8\n'
                    mips_code += '\tsw   $t1, 0($sp)\n\n'

            else:
                mips_code += self.visit(child)

        # remove  variables

        for node in reversed(parse_tree.children):
            if node.data == 'variable_decl':

                self.stack_counter[-1] -= 1
                var_name = node.children[0].children[1].value
                var_type = st_objects[symbol_table[(self.current_scope, var_name)]].type
                self.stack.pop()

                mips_code += '.text\n'

                if var_type.name == 'double' and var_type.size == 0:
                    mips_code += '\tl.d  $f0, 0($sp)\n'
                    mips_code += '\taddi $sp, $sp, 8\n'
                    mips_code += '\ts.d  $f0, {}\n\n'.format((self.current_scope + "/" + var_name).replace("/", "_"))
                else:
                    mips_code += '\tlw   $t1, 0($sp)\n'
                    mips_code += '\taddi $sp, $sp, 8\n'
                    mips_code += '\tla   $t0, {}\n'.format((self.current_scope + "/" + var_name).replace("/", "_"))
                    mips_code += '\tsw   $t1, 0($t0)\n\n'

        mips_code += 'end_stmt_{}:\n'.format(stmt_num)

        self.stmtLabels = self.stmtLabels[:len(self.stmtLabels)]
        self.stmtLabels.append(stmt_num)
        self.current_scope = POP(self.current_scope)
        return mips_code

    def stmt(self, parse_tree):

        # stmt : (expr)? ";"
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

        stmt_num = labelCounter()
        mips_code += ('start_stmt_{}:\n'.format(stmt_num))

        node._meta = stmt_num

        if node.data == 'if_stmt':
            mips_code += self.visit(node)

        elif node.data == 'while_stmt':
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
                funct , funct_count = class_type_objects[class_table[class_name]].find_function(func_name)
            else:
                func_name = self.current_scope.split('/')[1]
                funct = function_objects[function_table[func_name]]

            if funct.return_type.name == 'double' and funct_count.return_type.size == 0:
                mips_code += '\tl.d   $f30, 0($sp)\n' + '\taddi $sp, $sp, 8\n'

            elif funct.return_type.name != 'void':
                mips_code += '\tlw   $t8, 0($sp)\n' + '\taddi $sp, $sp, 8\n'


            c = self.stack_counter[-1]
            for local_var in reversed(self.stack[-c:]):
                var_name = local_var[0]
                var_type = local_var[1]
                mips_code += '.text\n'
                if var_type.name == 'double' and var_type.size == 0:
                    mips_code = '\tl.d  $f0, 0($sp)\n' + \
                                '\taddi $sp, $sp, 8\n' + \
                                '\ts.d  $f0, {}\n\n'.format(var_name.replace("/", "_"))
                else:
                    mips_code += '\tlw   $t0, 0($sp)\n'
                    mips_code += '\taddi $sp, $sp, 8\n'
                    mips_code += '\tsw   $t0, {}\n\n'.format(var_name.replace("/", "_"))

            if funct.return_type.name != 'void':
                mips_code += '\taddi $sp, $sp, -8\n'
                mips_code += '\tsw   $t8, 0($sp)\n'

            elif funct.return_type.name == 'double' and funct[1].return_type.size == 0:
                mips_code += '\taddi $sp, $sp, -8\n'
                mips_code += '\ts.d   $f30, 0($sp)\n'

            mips_code += '\tjr   $ra\n\n'

        elif node.data == 'expr' or node.data == 'assignment':
            mips_code += self.visit(node)
            expr_type = self.expressionTypes[-1]

            if expr_type.name != 'void':
                mips_code += '.text\n' + '\taddi\t$sp, $sp, 8\n\n'
            self.expressionTypes.pop()

        elif node.data == 'print_stmt':
            mips_code += self.visit(node)

        else:
            mips_code += self.visit(node)

        mips_code += 'end_stmt_{}:\n'.format(stmt_num)
        self.stmtLabels = self.stmtLabels[:len(self.stmtLabels)]
        self.stmtLabels.append(stmt_num)
        return mips_code

    def if_stmt(self, parse_tree):

        mips_code = ''
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
        # while count= parse_tree._meta
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

        self.stmtLabels = self.stmtLabels[:len(self.stmtLabels)]
        self.loopLabels.pop()
        return mips_code

    def for_stmt(self, parse_tree):
        mips_code = ''
        mips_code += '.text\t\t\t\t# For\n'  # todo check this comment
        # for_count = parse_tree._meta

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

    def break_stmt(self , parse_tree):
        mips_code = make_indentation(""".text\t\t\t\t# break
    j end_stmt_{}            
        """.format(self.loopLabels[-1]))
        return mips_code

    def continue_stmt(self, parse_tree):
        return code

    def print(self, parse_tree):
        mips_code = ''
        for ch in parse_tree.children[0].children:
            mips_code += self.visit(ch)
            t = self.expressionTypes[-1]
            self.expressionTypes.pop()
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

            elif t.name == 'bool' and t.size == 0:
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
        if t.name == 'double' and t.size == 0:
            mips_code += """.text
    lw $t0, 8($sp)
    l.d $f0, 0($sp)
    s.d $f0, 0($t0)
    s.d $f0, 8($sp)
    addi $sp, $sp, 8\n\n"""
        else:
            mips_code += """.text
    lw $t0, 8($sp)
    lw $t1, 0($sp)
    sw $t1, 0($t0)
    sw $t1, 8($sp)
    addi $sp, $sp, 8\n\n"""
        self.expressionTypes.pop()
        return mips_code

    def logical_or(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        self.expressionTypes.pop()
        self.expressionTypes.pop()
        mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    or $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def logical_and(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        self.expressionTypes.pop()
        self.expressionTypes.pop()
        mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    and $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def equals(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'double' and t.size == 0:
            c = labelCounter()
            mips_code += """.text
    li $t0, 0
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    c.eq.d $f0, $f2
    bc1f __eq.d__{}
    li $t0, 1
    __eq.d__{}:\tsw $t0, 8($sp)
    addi $sp, $sp, 8\n\n""".format(c, c)
        elif t.name == 'string' and t.size == 0:
            mips_code += """.text
    sw $t0, -8($sp)
    sw $t1, -8($sp)
    sw $a0, -12($sp)
    sw $a1, -16($sp)
    sw $v0, -20($sp)
    sw $ra, -24($sp)
    lw $a0, 0($sp)
    lw $a1, 8($sp)
    jal __strcmp__
    sw $v0, 8($sp)
    lw $t0, -4($sp)
    lw $t1, -8($sp)
    lw $a0, -12($sp)
    lw $a1, -16($sp)
    lw $v0, -20($sp)
    lw $ra, -24($sp)
    addi $sp, $sp, 8\n\n"""
        elif self:
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    seq $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def not_equals(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'double' and t.size == 0:
            c = labelCounter()
            mips_code += """.text
    li $t0, 0
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    c.eq.d $f0, $f2
    bc1t __neq.d__{}
    li $t0, 1
     __neq.d__{}:\tsw $t0, 8($sp)
    addi $sp, $sp, 8\n\n""".format(c, c)
        elif t.name == 'string' and t.size == 0:
            mips_code += """.text
    sw $t0, -8($sp)
    sw $t1, -8($sp)
    sw $a0, -12($sp)
    sw $a1, -16($sp)
    sw $v0, -20($sp)
    sw $ra, -24($sp)
    lw $a0, 0($sp)
    lw $a1, 8($sp)
    jal __strcmp__
    li $t0, 1
    sub $v0, $t0, $v0
    sw $v0, 8($sp)
    lw $t0, -4($sp)
    lw $t1, -8($sp)
    lw $a0, -12($sp)
    lw $a1, -16($sp)
    lw $v0, -20($sp)
    lw $ra, -24($sp)
    addi $sp, $sp, 8\n\n"""
        elif self:
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    sne $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def lt(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    slt $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text
    li $t0, 0
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    c.lt.d $f2, $f0
    bc1f __lt.d__{}
    li $t0, 1
    __lt.d__{}:\tsw $t0, 8($sp)
    addi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def lte(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    sle $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text
    li $t0, 0
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    c.le.d $f2, $f0
    bc1f __lte.d__{}
    li $t0, 1
    __lte.d__{}:\tsw $t0, 8($sp) 
    addi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def gt(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    sgt $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text
    li $t0, 0
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    c.le.d $f2, $f0
    bc1t __gt.d__{}
    li $t0, 1
    __gt.d__{}:\tsw $t0, 8($sp)
    addi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def gte(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    sge $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            c = labelCounter()
            mips_code += """.text
    li $t0, 0
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    c.lt.d $f2, $f0
    bc1t __gte.d__{}
    li $t0, 1
    __gte.d__{}:\tsw $t0, 8($sp)
    addi $sp, $sp, 8\n\n""".format(c, c)
        self.expressionTypes.pop()
        self.expressionTypes.append(Type('bool'))
        return mips_code

    def sum(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    add $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            mips_code += """.text
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    add.d $f4, $f2, $f0
    s.d $f4, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'string':
            mips_code += """.text        
    la $a0, str1
    la $a1, result
    jal
    strcopier
    nop

    la $a0, str2
    or $a1, $v0, $zero
    jal
    strcopier
    nop
    j
    finish
    nop

    strcopier:
    or $t0, $a0, $zero  # Source
    or $t1, $a1, $zero  # Destination

    loop:
    lb $t2, 0($t0)
    beq $t2, $zero, end
    addiu $t0, $t0, 1
    sb $t2, 0($t1)
    addiu $t1, $t1, 1
    b
    loop
    nop

    end:
    or $v0, $t1, $zero
    jr $ra
    nop

    finish:
    j
    finish
    nop
"""
        # TODO : concatination of 2 arrays , 2 strings
        return mips_code

    def sub(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    sub $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        else:
            mips_code += """.text
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    sub.d $f4, $f2, $f0
    s.d $f4, 8($sp)
    addi $sp, $sp, 8\n\n"""
        return mips_code

    def mul(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw   $t0, 0($sp)
    lw   $t1, 8($sp)
    mul  $t2, $t1, $t0
    sw   $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            mips_code += """.text
    l.d   $f0, 0($sp)
    l.d   $f2, 8($sp)
    mul.d $f4, $f2, $f0
    s.d   $f4, 8($sp)
    addi  $sp, $sp, 8\n\n"""
        return mips_code

    def div(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    div $t2, $t1, $t0
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        elif t.name == 'double':
            mips_code += """.text
    l.d $f0, 0($sp)
    l.d $f2, 8($sp)
    div.d $f4, $f2, $f0
    s.d $f4, 8($sp)
    addi $sp, $sp, 8\n\n"""
        return mips_code

    def mod(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        mips_code += """.text
    lw $t0, 0($sp)
    lw $t1, 8($sp)
    div $t1, $t0
    mfhi $t2
    sw $t2, 8($sp)
    addi $sp, $sp, 8\n\n"""
        self.expressionTypes.pop()
        return mips_code

    def minus(self, parse_tree):
        mips_code = ''

        mips_code += ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes.pop()
        if t.name == 'int':
            mips_code += """.text\t\t\t\t# Neg int
    lw $t0, 0($sp)
    sub $t0, $zero, $t0
    sw $t0, 0($sp)
"""
        else:
            mips_code += """.text\t\t\t\t# Neg double
    l.d $f0, 0($sp)
    neg.d $f0, $f0
    s.d $f0, 0($sp)
"""

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

    def read_char(self,parse_tree):
        mips_code = ''

        mips_code += make_indentation(
            """
             .text\t\t\t\t # Read Integer
                 li $v0, 12
                 syscall             
                 sub $sp, $sp, 8
                 sw $v0, 0($sp)
             ##
             """)
        self.expressionTypes.append(Type('int'))
        return mips_code

    def read_int(self,parse_tree):
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

    def read_line(self,parse_tree):

        mips_code = ''
        mips_code += make_indentation(
            """
       .text\t\t\t\t    # Read Line
           li $a0, 256 
           li $v0, 9        
           syscall
           sub $sp, $sp, 8
           sw $v0, 0($sp)
           move $a0, $v0
           li $a1, 256       
           li $v0, 8        
           syscall    
           
           lw $a0, 0($sp)     

           read_{label_id}:
               lb $t0, 0($a0)
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
       """.format(label_id=labelCounter(), ten=labelCounter(), thirt=labelCounter()))
        self.expressionTypes.append(Type('string'))
        return mips_code

    def new_class(self, parse_tree):

        class_name = parse_tree.children[0].value
        class_obj = class_type_objects[class_table[class_name]]
        size = 8 + len(class_obj.variables) * 8
        self.expressionTypes.append(Type(name=class_name))
        mips_code = ''
        mips_code += '.text\n'
        mips_code += '\tli $a0, {}\n'.format(size)
        mips_code += '\tli $v0, 9\n'
        mips_code += '\tsyscall\n'
        mips_code += '\tlw $t0, {}\n'.format(class_name + '_vtable')
        mips_code += '\tsw $t0, 0($v0)\n'
        mips_code += '\taddi $sp, $sp, -8\n'
        mips_code += '\tsw $v0, 0($sp)\n'
        return mips_code

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

        self.expressionTypes.append(Type(name=self.lastType.name, size=self.lastType.size + 1))
        return mips_code

    def val(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        t = self.expressionTypes[-1]
        if t.name == 'double' and t.size == 0:
            mips_code += '.text\n'
            mips_code += '\tlw $t0, 0($sp)\n'
            mips_code += '\tl.d $f0, 0($t0)\n'
            mips_code += '\ts.d $f0, 0($sp)\n\n'
        else:
            mips_code += '.text\n'
            mips_code += '\tlw $t0, 0($sp)\n'
            mips_code += '\tlw $t0, 0($t0)\n'
            mips_code += '\tsw $t0, 0($sp)\n\n'
        return mips_code

    def ident_l_value(self, parse_tree):
        name = parse_tree.children[0].value
        scope = self.current_scope
        while (scope, name) not in symbol_table:
            if '__class__' in scope.split('/')[-1]:
                class_name = scope.split('/')[-1][9:]
                if class_type_objects[class_table[class_name]].find_var(name)[1] >= 0:
                    break
            scope = POP(scope)
        if '__class__' in scope.split('/')[-1]:
            classObject = class_type_objects[class_table[scope.split('/')[-1][9:]]]


            index = classObject.find_var(name)
            index = index[1]
            if index >= 0:
                function_name = deepcopy(self.current_scope).split('/')
                while function_name[-1] != '_local':
                    function_name.pop()
                function_name.pop()
                mips_code = """.text
                            lw $t0, 0($fp)
                            addi $t1, $t0, {}
                            sub $sp, $sp, 8
                            sw $t1, 0($sp)\n\n""".format(index * 8 + 8)

                temp = classObject.find_var(name)
                temp =temp[0]
                self.expressionTypes.append(deepcopy(temp))

                return mips_code
        if len(scope.split('/')) == 3 and '__class__' in scope.split('/')[1]:
            class_name = scope.split('/')[1][9:]
            function = class_type_objects[class_table[class_name]].find_function(scope.split('/')[-1])
            formal_type, index = function[0].find_formal(name)
            mips_code = """.text
    addi $t0, $fp, -{}
    sub $sp, $sp, 8
    sw $t0, 0($sp)\n""".format(index * 8)
            self.expressionTypes.append(deepcopy(formal_type[1]))
            return mips_code
        label_name = scope.replace('/', '_') + '_' + name
        mips_code = """.text
    la $t0, {}
    sub $sp, $sp, 8
    sw $t0, 0($sp)\n\n""".format(label_name)
        t = st_objects[symbol_table[scope, name]].type
        self.expressionTypes.append(deepcopy(t))
        return mips_code

    def mem_access_l_value(self, parse_tree):
        mips_code = self.visit(parse_tree.children[0])
        id = parse_tree.children[1].value

        mips_code += """.text\n\tlw $t0, 0($sp)\n"""

        class_type = self.expressionTypes[-1]
        index = class_type_objects[class_table[class_type.name]].find_var(id)
        index = index[1]
        t = class_type_objects[class_table[class_type.name]].find_var(id)
        t = t[0]
        mips_code += """\taddi $t1, $t0, {}\n\tsw $t1, 0($sp)\n""".format((1 + index) * 8)
        self.expressionTypes.pop()
        self.expressionTypes.append(t)
        return mips_code

    def array_access_l_value(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        self.expressionTypes.pop()
        t = self.expressionTypes[-1]
        if t.name == 'double' and t.size == 1:
            mips_code += """.text
    lw $t7, 8($sp)
    lw $t0, 0($sp)
    li $t1, 8
    mul $t0, $t0, $t1
    add $t1, $t0, $t7
    sw $t1, 8($sp)
    addi $sp, $sp, 8\n\n"""
        else:
            mips_code += """.text
    lw $t7, 8($sp)
    lw $t0, 0($sp)
    li $t1, 4
    mul $t0, $t0, $t1
    add $t1, $t0, $t7
    sw $t1, 8($sp)
    addi $sp, $sp, 8\n\n"""
        self.expressionTypes[-1].size -= 1
        return mips_code


    def method_call(self, parse_tree):

        mips_code =''
        mips_code += self.visit(parse_tree.children[0])
        if self.expressionTypes[-1].size > 0:
            mips_code += """.text
    lw $t0, 0($sp)
    lw $t0, -8($t0)
    sw $t0, 0($sp)\n\n"""

            self.expressionTypes.pop()
            self.expressionTypes.append(Type('int'))
            return mips_code
        self.expressionTypes.pop()
        mips_code = """.text
    addi $sp, $sp, -8
    sw $ra, 0($sp)
    addi $sp, $sp, -8
    sw $fp, 0($sp)\n\n"""

        mips_code += self.visit(parse_tree.children[0])
        for ch in parse_tree.children[2].children:
            mips_code += self.visit(ch)

        mips_code += self.visit(parse_tree.children[0])

        class_type = self.expressionTypes.pop()
        function_name = parse_tree.children[1].value


        idx = class_type_objects[class_table[class_type.name]].find_function(function_name)


        mips_code += '.text\t\t\t# method call {} {}\n'.format(class_type.name, function_name)
        mips_code += '\tlw $t0, 0($sp)\n'
        mips_code += '\taddi $sp, $sp, 8\n'
        mips_code += '\tlw $t0, 0($t0)\n'
        mips_code += '\taddi $t0, $t0, {}\n'.format(4 * idx[1])
        mips_code += '\tlw $t0, 0($t0)\n'
        mips_code += '\taddi $fp, $sp, {}\n'.format(8 * len(parse_tree.children[2].children))
        mips_code += '\tjalr $t0\n'


        mips_code += '.text\t # call {}\n'.format(function_name)

        function = class_type_objects[class_table[class_type.name]].functions[idx[1]]

        if function.return_type.name == 'double' and function.return_type.size == 0:
            mips_code += '\tl.d   $f30, 0($sp)\n'
            mips_code += '\taddi $sp, $sp, 8\n'


        elif function.return_type.name != 'void':
            mips_code += '\tlw   $t8, 0($sp)\n'
            mips_code += '\taddi $sp, $sp, 8\n'
        mips_code += '\taddi $sp, $sp, {}\n'.format(len(parse_tree.children[2].children) * 8 + 8)
        for i in range(len(parse_tree.children[2].children)):
            self.expressionTypes.pop()
        mips_code += '\tlw $fp, 0($sp)\n'
        mips_code += '\taddi $sp, $sp, 8\n'
        mips_code += '\tlw $ra, 0($sp)\n'
        mips_code += '\taddi $sp, $sp, 8\n\n'

        if function.return_type.name == 'double' and function.return_type.size == 0:
            mips_code += """
            \taddi $sp, $sp, -8\n
            \ts.d   $f30, 0($sp)\n"""

        elif function.return_type.name != 'void':
            mips_code += '\taddi $sp, $sp, -8\n'
            mips_code += '\tsw   $t8, 0($sp)\n'
        self.expressionTypes.append(deepcopy(function.return_type))
        return mips_code



    def l_value(self, parse_tree):
        mips_code = ''.join(self.visit_children(parse_tree))
        return mips_code

    def call(self, parse_tree):
        mips_code = ''
        # self.expressionTypes
        if len(parse_tree.children) == 3:
            code = self.visit(parse_tree.children[0])
            if self.expressionTypes[-1].size > 0:
                mips_code += """.text
    lw $t0, 0($sp)
    lw $t0, -8($t0)
    sw $t0, 0($sp)\n\n"""

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
            label = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expressionTypes[-1]
                self.expressionTypes.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == parse_tree:
                        label = funct.label
            formal_name = (label + "/" + formal[0]).replace("/", "_")
            formal_type = formal[1]
            if formal_type.name == 'double' and formal_type.size == 0:
                mips_code += '\tl.d  $f0, {}\n'.format(formal_name)
                mips_code += """addi $sp, $sp, -8
    s.d  $f0, 0($sp)\n\n"""
            else:
                mips_code += '\tlw   $t1, {}\n'.format(formal_name)
                mips_code += """addi $sp, $sp, -8
    sw   $t1, 0($sp)\n\n"""

        # set actual parameters to formal parameters

        if parse_tree._meta[1]:
            label = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expressionTypes[-1]
                self.expressionTypes.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == func_name:
                        label = funct.label
            formal_name = (label + "/" + function.formals[0][0]).replace("/", "_")
            # todo is it really a pointer or it's just a name?
            expr = parse_tree._meta[1]
            mips_code += self.visit(expr)
            mips_code += '.text\n'
            mips_code += '\tlw $v0, 0($sp)\n'  # we don't use type because we are sure that it's class
            mips_code += '\tsw $v0, {}\n'.format(formal_name)
            mips_code += '\taddi $sp, $sp, 8\n'
            self.expressionTypes.pop()
            actual_counter = 1
        else:
            actual_counter = 0

        for expr in parse_tree.children:
            label = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expressionTypes[-1]
                self.expressionTypes.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == func_name:
                        label = funct.label
            mips_code += self.visit(expr)
            formal_name = (label + "/" + function.formals[actual_counter][0]).replace("/", "_")
            mips_code += '.text\n'
            formal_type = function.formals[actual_counter][1]
            if formal_type.name == 'double' and formal_type.size == 0:
                mips_code += '\tl.d  $f0, 0($sp)\n'
                mips_code += '\ts.d  $f0, {}\n'.format(formal_name)
                mips_code += '\taddi $sp, $sp, 8\n\n'
            else:
                mips_code += '\tlw   $v0, 0($sp)\n'
                mips_code += '\tsw   $v0, {}\n'.format(formal_name)  # herererere
                mips_code += '\taddi $sp, $sp, 8\n\n'
            actual_counter += 1
            self.expressionTypes.pop()  # todo check f(double, double) + g(double, double) f: int g: int

        mips_code += '.text\n'
        mips_code += '\taddi $sp, $sp, -8\n'
        mips_code += '\tsw   $ra, 0($sp)\n'

        if parse_tree._meta[1]:  # E1.ident(E1, expr, expr, ...)
            expr = parse_tree._meta[1]
            mips_code += self.visit(expr)
            class_type = self.expressionTypes[-1]
            self.expressionTypes.pop()
            index = class_type_objects[class_table[class_type.name]].find_function_index(func_name)
            mips_code += """.text
    lw $t0, 0($sp)
    addi $sp, $sp, 8
    lw $t0, 0($t0)\n"""

            mips_code += '\taddi $t0, $t0, {}\n'.format(4 * index)
            mips_code += """ lw $t0, 0($t0)
    jalr $t0\n"""
        else:
            label_name = function.name
            mips_code += '\tjal {}\n'.format(label_name.replace('/', '_'))

        if function.return_type.name == 'double' and function.return_type.size == 0:
            mips_code += """l.d   $f30, 0($sp)
    addi $sp, $sp, 8\n"""

        elif function.return_type.name != 'void':
            mips_code += '\tlw   $t8, 0($sp)\n'
            mips_code += '\taddi $sp, $sp, 8\n'

        mips_code += '\tlw   $ra, 0($sp)\n'
        mips_code += '\taddi $sp, $sp, 8\n\n'

        # pop formal parameters
        for formal in reversed(function.formals):
            label = function_scope
            if parse_tree._meta[1]:
                tmp = self.visit(parse_tree._meta[1])
                class_type = self.expressionTypes[-1]
                self.expressionTypes.pop()
                for funct in class_type_objects[class_table[class_type.name]].functions:
                    if funct.name == func_name:
                        label = funct.label
            formal_name = (label + "/" + formal[0]).replace("/", "_")
            formal_type = formal[1]
            if formal_type.name == 'double' and formal_type.size == 0:
                mips_code += 'l.d  $f0, 0($sp)\n'
                mips_code += '\taddi $sp, $sp, 8\n'
                mips_code += '\ts.d  $f0, {}\n\n'.format(formal_name)
            else:
                mips_code += '\tlw   $t0, 0($sp)\n'
                mips_code += '\taddi $sp, $sp, 8\n'
                mips_code += '\tsw   $t0, {}\n\n'.format(formal_name)
        if function.return_type.name == 'double' and function.return_type.size == 0:
            mips_code += '\taddi $sp, $sp, -8\n'
            mips_code += '\ts.d   $f30, 0($sp)\n'
        elif function.return_type.name != 'void':
            mips_code += '\taddi $sp, $sp, -8\n'
            mips_code += '\tsw   $t8, 0($sp)\n'
        mips_code += '# return type is ' + function.return_type.name + ' ' + str(function.return_type.size)
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
        mips_code = """.text
    sub $sp, $sp, 8
    sw $zero, 0($sp)\n\n"""
        self.expressionTypes.append(Type('null'))
        return mips_code

    def get_type(self, t):

        if type(t) == lark.lexer.Token:
            return Type(t)

        ret = self.get_type(t.children[0])
        ret.size += 1
        return ret


def decafCGEN(code):
    code = make_indentation("""
        int dtoi(double x){
            if(x >= 0.0)
                return dtoi_(x);
            return -dtoi_(-x-0.00000000001);
        }
        int ReadInteger__(){
            /*
            \\n| 10
            \\r| 13
            +  | 43
            -  | 45
            x  | 120
            X  | 88
            0  | 48
            9  | 57
            A  | 65
            F  | 70
            a  | 97
            f  | 102
            */
            int res;
            int inp;
            int sign;
            bool hex;
            hex = false;
            sign = 1;
            res = 0;
            while(true){
                inp = ReadChar__();
                if (inp == 10){
                    break;
                }
                if (inp != 43 && inp != 13){
                    if (inp == 45){
                        sign = -1;
                    }else{
                        if (inp == 120 || inp == 88){
                            hex = true;
                        }
                        else{
                            if(!hex){
                                res = res * 10 + inp - 48;
                            }else{
                                if(inp <= 60){
                                    inp = inp - 48;
                                }else{
                                    if(inp <= 75){
                                        inp = inp - 65 + 10;
                                    }else{
                                        inp = inp - 97 + 10;
                                    }
                                }
                                res = res * 16 + inp;
                            }
                        }
                    }
                }
            }
        return res * sign;
    }
    """)+code
    parser = Lark(Grammar, parser="lalr")
    try:
        parse_tree = parser.parse(code)
    except:
        sys.exit("Syntax Error")
    SymbolTable().visit(parse_tree)
    ParentTree().visit(parse_tree)
    set_parents()
    Traversal().visit(parse_tree)
    mips_code = CodeGenerator().visit(parse_tree)
    return mips_code


if __name__ == '__main__':
    print(decafCGEN(code))
