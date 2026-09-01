import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cpile.analyzer import Analyzer



code = """
def add(a: int, b: int) -> int:
    result: int = a + b
    return result
def count_up(n: int) -> void:
    for i in range(n):
        x = 10
"""
analyzer = Analyzer(code)
analyzer.analyze()
print("Symbol table:", analyzer.symbol_table)
assert analyzer.symbol_table["a"] == "int32_t"
assert analyzer.symbol_table["b"] == "int32_t"
assert analyzer.symbol_table["add"] == "int32_t"
assert analyzer.symbol_table["result"] == "int32_t"
assert analyzer.symbol_table["n"] == "int32_t"
assert analyzer.symbol_table["i"] == "int32_t"
assert analyzer.symbol_table["x"] == "int32_t"
print("All analyzer tests passed! 🎉")
