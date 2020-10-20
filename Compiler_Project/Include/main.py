import sys, getopt
from DecafLexer import *


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    with open("tests/" + inputfile, "r") as input_file:
    # do stuff with input file
        lexer.input(input_file.read())

    with open("out/" + outputfile, "w") as output_file:
        # write result to output file.
        # for the sake of testing :
        # output_file.write()
        sys.stdout = output_file
        for token in get_token(lexer):
            if token.type[:2] == 'T_':
                print("%s %s" % (token.type, token.value))

            else:
                print(token.value)


if __name__ == "__main__":
    main(sys.argv[1:])