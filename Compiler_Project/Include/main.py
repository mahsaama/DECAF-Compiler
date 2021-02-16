import sys, getopt
from DecafCodeGenerator import *



def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print ('main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open("tests/" + inputfile, "r") as input_file:
        # PHASE_1
        # myLexer = Lexer(tokens)
        # myLexer.input(input_file.read())

    	# PHASE_2
        input_code = input_file.read()

    with open("out/" + outputfile, "w") as output_file:
        # PHASE_1
        # sys.stdout =  output_file
        # try:
        #         for token in myLexer.tokenizer():
        #             print(token)
        # except LexerError:
        #         print('UNDEFINED_TOKEN')

		# PHASE_2
        # output_file.write(LALR_parser(input_code))
        output_file.write(decafCGEN(input_code))
        # for the sake of testing :
        output_file.write("""
            # PROGRAM: Hello, World!
            .data # Data declaration section
            out_string: .asciiz "Hello, World!"
            .text # Assembly language instructions
            main: # Start of code section
            li $v0, 4 # system call code for printing string = 4
            la $a0, out_string # load address of string to be printed into $a0
            syscall # call operating system to perform operation in $""")
if __name__ == "__main__":
    main(sys.argv[1:])
