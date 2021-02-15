from Compiler_Project.Include.function import make_indentation

standard_library_functions = """
_PrintInt:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        li      $v0, 1
        lw      $a0, 4($fp)
        syscall
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_SimplePrintDouble:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8

        li      $v0, 3
        l.d     $f12, 0($fp)    # load double value to $f12
        syscall

        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_PrintDoubleWithoutFourDecimal:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        li      $v0, 3
        l.d     $f12, 0($fp)    # load double value to $f12
        syscall
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra

_PrintDouble:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        l.d     $f12, 0($fp)    # load double value to $f12

        cvt.w.d  $f0,$f12
        mfc1 $a0, $f0
        li      $v0, 1
        syscall
        move $t0, $a0

        li      $v0, 4
        la      $a0, DOT
        syscall

        mtc1.d $t0, $f0
        cvt.d.w $f0, $f0
        sub.d $f4, $f0, $f12


        l.d $f0, CONST10000
        mul.d $f12, $f0, $f4
        cvt.w.d  $f0,$f12
        mfc1 $a0, $f0
        li      $v0, 1
        syscall

        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_PrintString:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        li      $v0, 4
        lw      $a0, 4($fp)
        syscall
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_PrintNewLine:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        li      $v0, 4
        la      $a0, NEWLINE
        syscall
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_PrintBool:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        lw      $t1, 4($fp)
        blez    $t1, fbr
        li      $v0, 4          # system call for print_str
        la      $a0, TRUE       # address of str to print
        syscall
        b end
fbr:    li      $v0, 4          # system call for print_str
        la      $a0, FALSE      # address of str to print
        syscall
end:    move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_Alloc:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        li      $v0, 9
        lw      $a0, 4($fp)
        syscall
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_StringEqual:
        subu    $sp, $sp, 8     # decrement sp to make space to save ra, fp
        sw      $fp, 8($sp)     # save fp
        sw      $ra, 4($sp)     # save ra
        addiu   $fp, $sp, 8     # set up new fp
        subu    $sp, $sp, 4     # decrement sp to make space for locals/temps
        li      $v0, 0
        #Determine length string 1
        lw      $t0, 4($fp)
        li      $t3, 0
bloop1: lb      $t5, ($t0)
        beqz    $t5, eloop1
        addi    $t0, 1
        addi    $t3, 1
        b       bloop1
eloop1: # Determine length string 2
        lw      $t1, 8($fp)
        li      $t4, 0
bloop2: lb      $t5, ($t1)
        beqz    $t5, eloop2
        addi    $t1, 1
        addi    $t4, 1
        b       bloop2
eloop2: bne     $t3,$t4,end1    # Check String Lengths Same
        lw      $t0, 4($fp)
        lw      $t1, 8($fp)
        li      $t3, 0
bloop3: lb      $t5, ($t0)
        lb      $t6, ($t1)
        bne     $t5, $t6, end1
        beqz    $t5, eloop3     # if zero, then we hit the end of both strings
        addi    $t3, 1
        addi    $t0, 1
        addi    $t1, 1
        b       bloop3
eloop3: li      $v0, 1
end1:   move    $sp, $fp        # pop callee frame off stack
        lw      $ra, -4($fp)    # restore saved ra
        lw      $fp, 0($fp)     # restore saved fp
        jr      $ra             # return from function
_Halt:
        li      $v0, 10
        syscall
_ReadInteger:
        subu    $sp, $sp, 8     # decrement sp to make space to save ra, fp
        sw      $fp, 8($sp)     # save fp
        sw      $ra, 4($sp)     # save ra
        addiu   $fp, $sp, 8     # set up new fp
        subu    $sp, $sp, 4     # decrement sp to make space for locals/temps
        li      $v0, 5
        syscall
        move    $sp, $fp        # pop callee frame off stack
        lw      $ra, -4($fp)    # restore saved ra
        lw      $fp, 0($fp)     # restore saved fp
        jr      $ra
_ReadLine:
        subu    $sp, $sp, 8     # decrement sp to make space to save ra, fp
        sw      $fp, 8($sp)     # save fp
        sw      $ra, 4($sp)     # save ra
        addiu   $fp, $sp, 8     # set up new fp
        subu    $sp, $sp, 4     # decrement sp to make space for locals/temps
        # allocate space to store memory
        li      $a0, 128        # request 128 bytes
        li      $v0, 9          # syscall "sbrk" for memory allocation
        syscall                 # do the system call
        # read in the new line
        li      $a1, 128        # size of the buffer
        move    $a0, $v0        # location of the buffer
        li      $v0, 8
        syscall
        move    $t1, $a0
bloop4: lb      $t5, ($t1)
        beqz    $t5, eloop4
        addi    $t1, 1
        b       bloop4
eloop4: addi    $t1, -1         # add \0 at the end.
        li      $t6, 0
        sb      $t6, ($t1)
        move    $v0, $a0        # save buffer location to v0 as return value  
        move    $sp, $fp        # pop callee frame off stack
        lw      $ra, -4($fp)    # restore saved ra
        lw      $fp, 0($fp)     # restore saved fp
        jr      $ra
_ITOD:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        lw $t0,4($fp)           #copy top stack to t0
        mtc1.d $t0, $f0
        cvt.d.w $f0, $f0
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_DTOI:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        l.d $f0,0($fp)     #move top stack to f0
        li.d $f6, 0.5 # round to nearest integer
        add.d $f0, $f0, $f6
        cvt.w.d $f0,$f0
        mfc1.d $v0,$f0

        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_ITOB:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        lw $t0,4($fp)           #copy top stack to t0
        beqz $t0,_itob_label
        addu $v0,$zero,1
        b _itob_endlabel
        _itob_label:
        add $v0,$zero,$zero
        _itob_endlabel:
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
_BTOI:
        subu    $sp, $sp, 8
        sw      $fp, 8($sp)
        sw      $ra, 4($sp)
        addiu   $fp, $sp, 8
        lw $v0,4($fp)           #copy top stack to t0
        move    $sp, $fp
        lw      $ra, -4($fp)
        lw      $fp, 0($fp)
        jr      $ra
.data
TRUE:.asciiz "true"
FALSE:.asciiz "false"
NEWLINE:.asciiz "\\n"
DOT: .asciiz "."
CONST10000: .double -10000.0
"""


def primitve_inst():

    mips_code = make_indentation(
        """
        .text
            root_ReadChar__:
            .text
            start_rstmt_65:
            start_rstmt_66:
            .text
            
                li $v0, 12           #read_char
                syscall             #ReadChar
                sub $sp, $sp, 8
                sw $v0, 0($sp)
            
                
            
                lw   $t8, 0($sp)
                addi $sp, $sp, 8
                addi $sp, $sp, -8
                sw   $t8, 0($sp)
                jr   $ra
            
            end_rstmt_66:
            start_rstmt_67:
                lw   $t8, 0($sp)
                addi $sp, $sp, 8
                addi $sp, $sp, -8
                sw   $t8, 0($sp)
                jr   $ra
            
            end_rstmt_67:
            end_rstmt_65:
            """
    )+ make_indentation(
""" # ITOD
             .data
                 .align 2
                 root_itod_ival: .space 4
             .text
                 root_itod:
                 la $t0, root_itod_ival
                 sub $sp, $sp, 8
                 sw $t0, 0($sp)
                 lw $t0, 0($sp)
                 lw $t0, 0($t0)
                 sw $t0, 0($sp)
                 mtc1.d $t0, $f0
                 cvt.d.w $f0, $f0
                 sub $sp, $sp, 8
                 s.d $f0, 0($sp)
                 l.d   $f30, 0($sp)
                 addi $sp, $sp, 8
                 addi $sp, $sp, 8
                 addi $sp, $sp, -8
                 s.d   $f30, 0($sp)
                 jr   $ra
             """
    )+ make_indentation(
        """
        #DTOI
        root_dtoi_:
        .data
        .align 2
        root_dtoi__dval: .space 8
        .text
            li $t0, 1
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            la $t0, root_dtoi__dval
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            lw $t0, 0($sp)
            l.d $f0, 0($t0)
            li.d $f6, 0.5 # round to nearest integer
            add.d $f0, $f0, $f6
            cvt.w.d $f0,$f0
            mfc1.d $a0,$f0
            sw $a0, 0($sp)
            l.d   $f30, 0($sp)
            addi $sp, $sp, 8
            addi $sp, $sp, 8
            addi $sp, $sp, -8
            s.d   $f30, 0($sp)
            jr   $ra
        """
    )+make_indentation("""
        # ceil
        root_ceil__:
        .data
        .align 2
        root_ceil___dval: .space 8
        .text
            li $t0, 1
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            la $t0, root_ceil___dval
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            lw $t0, 0($sp)
            l.d $f0, 0($t0)
            # li.d $f6, 0.5 # round to nearest integer
            # add.d $f0, $f0, $f6
            cvt.w.d $f0,$f0
            mfc1.d $a0,$f0
            sw $a0, 0($sp)
            l.d   $f30, 0($sp)
            addi $sp, $sp, 8
            addi $sp, $sp, 8
            addi $sp, $sp, -8
            s.d   $f30, 0($sp)
            jr   $ra
        """)+make_indentation("""
        .text
        root_itob:
        .data
        .align 2
            root_itob_ival: .space 4
        .text
            la $t0, root_itob_ival
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            lw $t0, 0($sp)
            lw $t0, 0($t0)
            sw $t0, 0($sp)
            li $t0, 0
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            lw $t0, 0($sp)
            lw $t1, 8($sp)
            sne $t2, $t1, $t0
            sw $t2, 8($sp)
            addi $sp, $sp, 8
            l.d   $f30, 0($sp)
            addi $sp, $sp, 8
            addi $sp, $sp, -8
            s.d   $f30, 0($sp)
            jr   $ra
        """)+make_indentation("""
        .text
        root_btoi:
        .data
        .align 2
        root_btoi_bval: .space 4
        .text
        start_btoi_stmt_1:
        start_btoi_stmt_2:
        # if starts here:
        .text
            la $t0, root_btoi_bval
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            lw $t0, 0($sp)
            lw $t0, 0($t0)
            sw $t0, 0($sp)
            lw $a0, 0($sp)
            addi $sp, $sp, 8
            beq $a0, 0, end_btoi_stmt_3
            j  start_btoi_stmt_3
        start_btoi_stmt_3:
        start_btoi_stmt_4:
        start_btoi_stmt_5:
            li $t0, 1
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            l.d   $f30, 0($sp)
            addi $sp, $sp, 8
            addi $sp, $sp, -8
            s.d   $f30, 0($sp)
            jr   $ra
        end_btoi_stmt_5:
        end_btoi_stmt_4:
        end_btoi_stmt_3:
        end_btoi_stmt_2:
        start_btoi_stmt_6:
        .text
            li $t0, 0
            sub $sp, $sp, 8
            sw $t0, 0($sp)
            l.d   $f30, 0($sp)
            addi $sp, $sp, 8
            addi $sp, $sp, -8
            s.d   $f30, 0($sp)
            jr   $ra
        end_btoi_stmt_6:
        end_btoi_stmt_1:
        """)

    return mips_code



#print(primitve_inst())
