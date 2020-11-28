import re
import sys

reserved = [
    ('void', 'VOID'),
    ('int', 'INT'),
    ('double', 'DOUBLE'),
    ('bool', 'BOOL'),
    ('string', 'STRING'),
    ('class', 'CLASS'),
    ('interface', 'INTERFACE'),
    ('null', 'NULL'),
    ('this', 'THIS'),
    ('extends', 'EXTENDS'),
    ('implements', 'IMPLEMENTS'),
    ('for', 'FOR'),
    ('while', 'WHILE'),
    ('if', 'IF'),
    ('else', 'ELSE'),
    ('return', 'RETURN'),
    ('break', 'BREAK'),
    ('continue', 'CONTINUE'),
    ('new', 'NEW'),
    ('NewArray', 'NEWARRAY'),
    ('Print', 'PRINT'),
    ('ReadInteger', 'READINTEGER'),
    ('ReadLine', 'READLINE'),
    ('dtoi', 'DTOI'),
    ('itod', 'ITOD'),
    ('btoi', 'BTOI'),
    ('itob', 'ITOB'),
    ('private', 'PRIVATE'),
    ('protected', 'PROTECTED'),
    ('public', 'PUBLIC')
]
tokens = [
             ('\s', 'WHITESPACE'),
             ('\.', 'DOT'),
             (',', 'COMMA'),
             (';', 'SEMICOLON'),
             ('\(', 'LPAREN'),
             ('\)', 'RPAREN'),
             ('{', 'LBRACE'),
             ('}', 'RBRACE'),
             ('\[', 'LBRACKET'),
             ('\]', 'RBRACKET'),
             ('==', 'EQ'),
             ('!=', 'NEQ'),
             ('=', 'ASSIGN'),
             ('!', 'NOT'),
             ('\+', 'PLUS'),
             ('-', 'MINUS'),
             ('\*', 'MULTIPLY'),
             ('/', 'DIVIDE'),
             ('%', 'MODE'),
             ('&&', 'AND'),
             ('\|\|', 'OR'),
             ('>=', 'GEQ'),
             ('<=', 'LEQ'),
             ('<', 'LT'),
             ('>', 'GT'),
             ('[a-zA-Z][_a-zA-Z0-9]*', 'T_ID'),
             ('\d+\.(\d*)?((e|E)(\+|-)?\d+)?|\d+(e|E)(\+|-)?\d+', 'T_DOUBLELITERAL'),
             ('0[x|X][0-9a-fA-F]+|\d+', 'T_INTLITERAL'),
             ('"[^"\\n]*"', 'T_STRINGLITERAL'),
             ('true|false', 'T_BOOLEANLITERAL'),
         ] + reserved


class Token(object):
    def __init__(self, type, value, pos):
        self.type = type
        self.value = value
        self.pos = pos

    def __str__(self):
        if self.type[:2] == 'T_':
            return '%s %s' % (self.type, self.value)
        else:
            return '%s' % (self.value)


class LexerError(Exception):
    def __init__(self, pos):
        self.pos = pos


class Lexer(object):
    def __init__(self, tokens):
        pattern_index = 1
        regex_patterns = []
        self.pattern_type = {}

        for regex, type in tokens:
            pattern_number = 'Pattern' + str(pattern_index)
            regex_patterns.append('(?P<%s>%s)' % (pattern_number, regex))
            self.pattern_type[pattern_number] = type
            pattern_index += 1

        self.regex = re.compile('|'.join(regex_patterns))

    def input(self, buffer):
        oneLineComment_removed = re.sub('//.*', '', buffer)
        multiLineComment_removed = re.sub('/\*(.|\n)*?\*/', '', oneLineComment_removed)
        self.buffer = multiLineComment_removed
        self.pos = 0

    def token(self):
        if self.pos >= len(self.buffer):
            return None
        else:
            tok = self.regex.match(self.buffer, self.pos)
            if tok:
                groupname = tok.lastgroup
                token_type = self.pattern_type[groupname]
                if token_type == 'T_ID' and (tok.group(groupname) == 'true' or tok.group(groupname) == 'false'):
                    token = Token('T_BOOLEANLITERAL', tok.group(groupname), self.pos)
                elif token_type == 'T_ID' and ((tok.group(groupname), tok.group(groupname).upper()) in reserved):
                    token = Token(tok.group(groupname).upper(), tok.group(groupname), self.pos)
                else:
                    token = Token(token_type, tok.group(groupname), self.pos)
                self.pos = tok.end()
                return token
            raise LexerError(self.pos)

    def tokenizer(self):
        while True:
            token = self.token()
            if token is None:
                break
            if token.type == 'WHITESPACE':
                continue
            yield token


if __name__ == '__main__':
    myLexer = Lexer(tokens)
    file = open("DecafCode.decaf", "r")
    myLexer.input(file.read())

    try:
        for token in myLexer.tokenizer():
            print(token)
    except LexerError:
        print('UNDEFINED_TOKEN')
