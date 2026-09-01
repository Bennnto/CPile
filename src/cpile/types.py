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