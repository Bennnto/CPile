import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.cpile.analyzer import Analyzer
from src.cpile.codegen import CodeGenerator


code ="""
class Vector:
    x: int
    y: int
def dot(a: Vector, b: Vector) -> int:
    return a.x * b.x + a.y * b.y
"""

analyzer = Analyzer(code)
analyzer.analyze()
generator = CodeGenerator(analyzer.tree, analyzer.symbol_table)
c_code = generator.generate()
with open("array.c", "w") as f:
    f.write(c_code)
print("--- Generated C Code ---")
print(c_code)
print("------------------------")