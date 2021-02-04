import lark
from lark import Lark, Tree
from lark.visitors import Interpreter

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
    print_stmt : "Print" "(" expr (","expr)* ")" ";" -> print
    expr : l_value "=" expr -> assignment
        | expr1
    expr1 : expr1 "||" expr2 -> or
        | expr2
    expr2 : expr2 "&&" expr3 -> and
        |expr3
    expr3 : expr3 "==" expr4 -> eq
        | expr3 "!=" expr4 -> neq
        | expr4
    expr4 : expr4 "<" expr5 -> lt
        | expr4 ">" expr5 -> gt
        | expr4 "<=" expr5 -> lte
        | expr4 ">=" expr5 -> gte
        | expr5
    expr5 : expr5 "+" expr6 -> sum
        | expr5 "-" expr6 -> sub
        | expr6
    expr6 : expr6 "*" expr7 -> mult
        | expr6 "/" expr7 -> div
        | expr6 "%" expr7 -> mod
        | expr7
    expr7 : "-" expr7 -> neg
        | "!" expr7 -> not
        | expr8
    expr8 : constant 
        | "itod" "(" expr ")" -> int_to_double
        | "dtoi" "(" expr ")" -> double_to_int
        | "itob" "(" expr ")" -> int_to_bool
        | "btoi" "(" expr ")" -> bool_to_int
        | "ReadInteger" "(" ")" -> read_int 
        | "ReadLine" "(" ")" -> read_line        
        | "new" ident -> new_class
        | "NewArray" "(" expr "," type ")" -> new_array
        | l_value -> val
        | "(" expr ")" 
        | "this" -> this        
        | call 
    l_value : ident -> variableAddress
        | expr8 "." ident -> variableAccess
        | expr8 "[" expr "]" -> subscript
    call : ident "(" actuals ")" 
        | expr8 "." ident "(" actuals ")" -> method
    actuals : expr (","expr)* 
        | 
    constant : int_constant -> int
        | double_constant -> double
        | bool_constant -> bool 
        | string_constant -> string
        | "null" -> null
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
if __name__ == '__main__':
    input_code = ""
    parser = Lark(Grammar, parser="lalr", debug=False)
    parse_tree = parser.parse(input_code)
