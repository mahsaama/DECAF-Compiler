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
rules = [
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
    ('[a-zA-Z_][a-zA-Z_0-9]*', 'T_ID'),
    ('\d+\.(\d+)?((e|E)(\+|-)?\d+)?|\d+(e|E)(\+|-)?\d+', 'T_DOUBLELITERAL'),
    ('0[x|X][0-9a-fA-F]+|\d+', 'T_INTLITERAL'),
    ('\"[^\"\\\\]*(\\\\.[^\"\\\\]*)*\"', 'T_STRINGLITERAL'),
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
    def __init__(self, rules, skip_whitespace=True):
        idx = 1
        regex_parts = []
        self.group_type = {}

        for regex, type in rules:
            groupname = 'GROUP%s' % idx
            regex_parts.append('(?P<%s>%s)' % (groupname, regex))
            self.group_type[groupname] = type
            idx += 1

        self.regex = re.compile('|'.join(regex_parts))
        self.skip_whitespace = skip_whitespace
        self.re_whitespace_skip = re.compile('\S')

    def input(self, buffer):
        oneLineComment_removed = re.sub('//.*', '', buffer)
        multiLineComment_removed = re.sub('/\*(.|\n)*?\*/', '', oneLineComment_removed)
        self.buffer = multiLineComment_removed
        self.pos = 0

    def token(self):
        if self.pos >= len(self.buffer):
            return None
        else:
            if self.skip_whitespace:
                t = self.re_whitespace_skip.search(self.buffer, self.pos)
                if t:
                    self.pos = t.start()
                else:
                    return None
            t = self.regex.match(self.buffer, self.pos)
            if t:
                groupname = t.lastgroup
                token_type = self.group_type[groupname]
                if token_type == 'T_ID' and (t.group(groupname) == 'true' or t.group(groupname) == 'false'):
                    token = Token('T_BOOLEANLITERAL', t.group(groupname), self.pos)
                elif token_type == 'T_ID' and ((t.group(groupname),t.group(groupname).upper()) in reserved):
                    token = Token(t.group(groupname).upper(), t.group(groupname), self.pos)
                else:
                    token = Token(token_type, t.group(groupname), self.pos)
                self.pos = t.end()
                return token

            raise LexerError(self.pos)

    def tokenizer(self):
        while True:
            token = self.token()
            if token is None:
                break
            yield token

if __name__ == '__main__':
    myLexer = Lexer(rules, skip_whitespace=True)
    file = open("DecafCode.decaf", "r")
    myLexer.input(file.read())

    try:
        for token in myLexer.tokenizer():
            print(token)
    except LexerError:
        print('UNDEFINED_TOKEN')