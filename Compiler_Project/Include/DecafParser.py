import lark
from lark import Lark
import re

Grammar = """
    start : (decl)+
    decl : variable_decl 
        | function_decl 
        | class_decl 
        | interface_decl
    variable_decl : variable ";"
    variable : type ident
    type : "int" 
        | "double" 
        | "bool" 
        | "string" 
        | ident 
        | type "[]"
    function_decl : type ident "("formals")" stmt_block 
        | "void" ident "("formals")" stmt_block
    formals : variable (","variable)* 
        | 
    class_decl : "class" ident ("extends" ident)? ("implements" ident("," ident)*)? "{"(field)*"}"
    field : access_mode variable_decl 
        | access_mode function_decl
    access_mode : "private" 
        | "protected" 
        | "public" 
        | 
    interface_decl : "interface" ident "{"(prototype)*"}"
    prototype : type ident "(" formals ")" ";" 
        | "void" ident "(" formals ")" ";"
    stmt_block : "{" (variable_decl)* (stmt)* "}"
    stmt : (expr)? ";" 
        | if_stmt 
        | while_stmt 
        | for_stmt 
        | break_stmt 
        | continue_stmt 
        | return_stmt 
        | print_stmt 
        | stmt_block
    if_stmt : "if" "(" expr ")" stmt ("else" stmt)?
    while_stmt : "while" "(" expr ")" stmt
    for_stmt : "for" "(" (expr)? ";" expr ";" (expr)? ")" stmt
    return_stmt : "return" (expr)? ";"
    break_stmt : "break" ";"
    continue_stmt : "continue" ";"
    print_stmt : "Print" "(" expr (","expr)* ")" ";"
    expr : l_value "=" expr 
        | constant 
        | l_value 
        | "this" 
        | call 
        | "(" expr ")" 
        | expr "+" expr 
        | expr "-" expr 
        | expr "*" expr 
        | expr "/" expr 
        | expr "%" expr 
        | "-" expr 
        | expr "<" expr 
        | expr "<=" expr 
        | expr ">" expr 
        | expr ">=" expr 
        | expr "==" expr 
        | expr "!=" expr 
        | expr "&&" expr 
        | expr "||" expr 
        | "!" expr 
        | "ReadInteger" "(" ")" 
        | "ReadLine" "(" ")" 
        | "new" ident 
        | "NewArray" "(" expr "," type ")" 
        | "itod" "(" expr ")" 
        | "dtoi" "(" expr ")" 
        | "itob" "(" expr ")" 
        | "btoi" "(" expr ")"
    l_value : ident 
        | expr "." ident 
        | expr "[" expr "]"
    call : ident "(" actuals ")" 
        | expr "." ident "(" actuals ")"
    actuals : expr (","expr)* 
        | 
    constant : int_constant 
        | double_constant 
        | bool_constant 
        | string_constant 
        | "null"
    double_constant : /(\d+\.(\d*)?((e|E)(\+|-)?\d+)?)/ 
        | /(\d+(e|E)(\+|-)?\d+)/
    int_constant : /(0[x|X][0-9a-fA-F]+)/ 
        | /(\d+)/
    bool_constant : /(true)/ 
        | /(false)/
    string_constant : /"[^"\\n]*"/
    ident :  /(?!((true)|(false)|(void)|(int)|(double)|(bool)|(string)|(class)|(interface)|(null)|(this)|(extends)|(implements)|(for)|(while)|(if)|(else)|(return)|(break)|(continue)|(new)|(NewArray)|(Print)|(ReadInteger)|(ReadLine)|(dtoi)|(itod)|(btoi)|(itob)|(private)|(protected)|(public))([^_a-zA-Z0-9]|$))[a-zA-Z][_a-zA-Z0-9]*/
    INLINE_COMMENT : "//" /[^\\n]*/ "\\n"
    MULTILINE_COMMENT : "/*" /.*?/ "*/"
    %ignore INLINE_COMMENT 
    %ignore MULTILINE_COMMENT
    %import common.WS
    %ignore WS
    """

def LALR_parser(input_code):
    try:
        parser = Lark(Grammar, parser="lalr", debug=False)
        parser.parse(input_code)
    except:
        return "Syntax Error"
    return "OK"

if __name__ == '__main__':
    test = """

int getSomeValue() {
    return something;
}

int main() {
    int a;
    int b;
    bool c;
    double d;
    d = 1.2E5 * 5. + 1.;
    c = (a / b < 100);
    c = true || false;
}

    """
    print(LALR_parser(test))
