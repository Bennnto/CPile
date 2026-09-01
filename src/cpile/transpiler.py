from .analyzer import Analyzer
from .codegen import CodeGenerator
import os
from pathlib import Path
import ast
import subprocess

def compile_c(c_code, output_name: str ="output.o"):
    """Compile C code into executable file."""
    # save C code to file .c 
    with open("cpile.c", "w") as f:
        f.write(c_code)

    # Compile C code from file .c 
    result = subprocess.run(
        ["gcc", "-o", output_name, "cpile.c"],
        capture_output = True,
        text=True
    )
    if result.returncode != 0:
        print("Compilation Failed :", result.stderr)
    else :
        print("Compile Success Binary created :", output_name)


def transpile(source_code: str) -> str: 
    """Transpiles a python source code into clean C code."""
    analyzer = Analyzer(source_code)
    # Type Analysis
    analyzer.analyze() 

    tree = analyzer.tree
    symbol_table = analyzer.symbol_table
    codegen = CodeGenerator(tree, symbol_table)
    c_code = codegen.generate()
    # Compile C code
    return c_code


def transpile_file(file_path:str) -> str:
    """Read a python file and transpile it into source code"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found at {file_path}")
    
    source_code = path.read_text(encoding="utf-8")
    return transpile(source_code)

    
