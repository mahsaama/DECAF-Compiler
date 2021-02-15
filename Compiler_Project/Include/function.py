class_type_objects = []
function_objects = []
function_table = {}
class_table = {}


class Type:
    name: str
    size: int

    def __init__(self, name=None, meta=None, size=0):
        self.name = name
        self.size = size
        self._meta = meta


class Class:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        self.variables = []
        self.functions = []
        class_type_objects.append(self)

    def find_function(self, name):
        counter = 0
        for func in self.functions:
            if func.name == name:
                return func, counter
            counter += 1
        raise Exception("")

    def find_var(self, ident):
        counter = 0
        for var in self.variables:
            if var[0] == ident:
                return self.variables[counter][1], counter
            else:
                counter += 1
        return self.variables[-1][1], -1


class Function:
    def __init__(self, name=None, label=None, return_type=Type(), formals=None):
        self.name = name
        self.return_type = return_type

        if formals is None:
            self.formals = []
        else:
            self.formals = formals
        self.label = label

    def find_formal(self, name: str):
        print
        counter = 0
        for formal in self.formals:
            if formal[0] == name:
                return formal, counter
            counter += 1
        raise ChildProcessError()


def lib_functions():
    function_objects.append(
        Function(name='itob', label='_itob_', return_type=Type('bool'), formals=[['ival', Type('int')]])
    )

    function_table['itob'] = 0

    function_objects.append(
        Function(name='btoi', label='_btoi_', return_type=Type('bool'), formals=[['bval', Type('bool')]])
    )

    function_table['btoi'] = 1

    function_objects.append(
        Function(name='itod', label='_itod_', return_type=Type('double'), formals=[['ival', Type('int')]])
    )

    function_table['itod'] = 2

    function_objects.append(
        Function(name='dtoi_', label='_dtoi_', return_type=Type('int'), formals=[['dval', Type('double')]])

    )

    function_table['dtoi_'] = 3

    function_objects.append(
        Function(name='ReadChar__', label='_ReadChar__', return_type=Type('int'), formals=[])
    )

    function_table['ReadChar__'] = 4


def make_indentation(code):

    space_count = 0
    codes = code.split("\n")
    if len(codes[0]) == 0:
        codes = codes[1:]


    for c in codes[0]:
        if c == ' ':
            space_count = space_count+1
        else:
            break


    for cd in codes:
        if cd[:space_count] == ' ' * space_count:
            cd = cd[space_count:]
        cd = cd + "\n"

    codes[-1] = "\n"
    res = ' '.join(codes)
    return res


#lib_functions()

