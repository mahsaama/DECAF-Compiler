import sys
import ply.lex as lex

reserved = {
    'void': 'VOID',
    'int': 'INT',
    'double': 'DOUBLE',
    'bool': 'BOOL',
    'string': 'STRING',
    'class': 'CLASS',
    'interface': 'INTERFACE',
    'null': 'NULL',
    'this': 'THIS',
    'extends': 'EXTENDS',
    'implements': 'IMPLEMENTS',
    'for': 'FOR',
    'while': 'WHILE',
    'if': 'IF',
    'else': 'ELSE',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'new': 'NEW',
    'NewArray': 'NEWARRAY',
    'Print': 'PRINT',
    'ReadInteger': 'READINTEGER',
    'ReadLine': 'READLINE',
    'dtoi': 'DTOI',
    'itod': 'ITOD',
    'btoi': 'BTOI',
    'itob': 'ITOB',
    'private': 'PRIVATE',
    'protected': 'PROTECTED',
    'public': 'PUBLIC',
}

tokens = ['DOT', 'COMMA', 'SEMICOLON',
          'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
          'ASSIGN',
          'NOT', 'PLUS', 'MINUS',
          'MULTIPLY', 'DIVIDE', 'MODE', 'AND', 'OR', 'EQ', 'NEQ', 'LT', 'LEQ', 'GT', 'GEQ',
          'T_ID', 'T_INTLITERAL', 'T_DOUBLELITERAL', 'T_STRINGLITERAL', 'T_BOOLEANLITERAL'] + list(reserved.values())


t_DOT = r'\.'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODE = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_AND = r'&&'
t_OR = r'\|\|'
t_EQ = r'=='
t_NEQ = r'!='
t_LT = r'<'
t_LEQ = r'<='
t_GT = r'>'
t_GEQ = r'>='
t_NOT = r'!'
t_SEMICOLON = r';'
t_ASSIGN = r'='
t_COMMA = r','
t_ignore_COMMENT = r'//.*'
t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if not (t.value == 'true' or t.value == 'false'):
        t.type = reserved.get(t.value, 'T_ID')
        return t
    else:
        t.type = reserved.get(t.value, 'T_BOOLEANLITERAL')
        return t


def t_DOUBLELITERAL(t):
    r'\d+\.(\d+)?((e|E)(\+|-)?\d+)?|\d+(e|E)(\+|-)?\d+'
    t.type = reserved.get(t.value, 'T_DOUBLELITERAL')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    pass

def t_ignore_COMMENT_MULTI(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_INTLITERAL(t):
    r'0[x|X][0-9a-fA-F]+|\d+'
    t.type = reserved.get(t.value, 'T_INTLITERAL')
    return t

def t_STRINGLITERAL(t):
    r'"([^\\"]|\\\\|\\"|\\n|\\t)*"'
    t.type = reserved.get(t.value, 'T_STRINGLITERAL')
    t.lexer.lineno += t.value.count('\n')
    return t

def t_error(t):
    print("UNDEFINED_TOKEN")
    t.lexer.skip(1)

lexer = lex.lex()

def get_token(lexer):
    while True:
        t = lexer.token()
        if not t:
            return
        yield t

if __name__ == '__main__':
    file = open("DecafCode.decaf","r")
    lexer.input(file.read())
    for token in get_token(lexer):
        if token.type[:2] == 'T_':
            print("%s %s" % (token.type, token.value))
        else:
            print(token.value)
