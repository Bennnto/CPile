import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.cpile.analyzer import Analyzer
from src.cpile.codegen import CodeGenerator
code = """
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""
analyzer = Analyzer(code)
analyzer.analyze()
generator = CodeGenerator(analyzer.tree, analyzer.symbol_table)
c_code = generator.generate()
with open("fib.c", "w") as f:
    f.write(c_code)
print("--- Generated C Code ---")
print(c_code)
print("------------------------")