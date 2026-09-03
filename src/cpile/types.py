import ast

TYPE_MAP = {
    'str' : 'char*',
    'int' : 'int32_t',
    'bool' : 'bool',
    'float' : 'double',
}

FORMAT_MAP = {
    'char*' : '%s',
    'int32_t' : '%d',
    'bool' : '%d',
    'double' : '%f'
}

class TranspileError(Exception):
    pass

def to_c_type(type_name : str) -> str :
    if type_name in ("None", "void" ):
        return "void"
    if type_name in TYPE_MAP :
        return TYPE_MAP[type_name]
    raise TranspileError(f"Type {type_name} not support by the transpiler")

def get_format_specifier(c_type: str) -> str:
    if c_type in FORMAT_MAP :
        return FORMAT_MAP[c_type]
    raise TranspileError(f"Type {c_type} not support for format specifier")


def infer_type_from_value(node: ast.Constant) -> str :
    value = node.value
    if isinstance(value, str):
        return "char*"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int32_t"
    elif isinstance(value, float):
        return "double"
    else :
        return "void"

def is_list_type(node):
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "list":
        return True
    else :
        return False

def get_list_element_type(node:ast.Subscript) -> str :
    """ Extract the element C type from a list [...]"""
    if isinstance(node.slice, ast.Name):
        elem_type = node.slice.id
        return to_c_type(elem_type)
    raise TranspileError(f"Unspoorted list slice type : {ast.dump(node.slice)}")
