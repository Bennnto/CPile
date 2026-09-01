import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cpile.types import to_c_type, get_format_specifier, infer_type_from_value
import ast

# Test map to c type
assert to_c_type("int") == "int32_t"
assert to_c_type("bool") == "bool"
assert to_c_type("str") == "char*"
assert to_c_type("float") == "double"

# Test match format specifier
assert get_format_specifier("int32_t") == "%d"
assert get_format_specifier("double") == "%f"
assert get_format_specifier("char*") == "%s"
assert get_format_specifier("bool") == "%d"

# Test infer type from value
assert infer_type_from_value(ast.Constant(value="Hello World")) == "char*"
assert infer_type_from_value(ast.Constant(value=40)) == "int32_t"
assert infer_type_from_value(ast.Constant(value=True)) == "bool"
assert infer_type_from_value(ast.Constant(value=3.14159265359)) == "double"

print("All tests passed!")
