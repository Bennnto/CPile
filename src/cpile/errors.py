import ast

class CompileDiagnostic(Exception):
    def __init__(self, message:str, source_code:str, file_name:str, node:ast.AST, hint:str=None):
        self.message = message
        self.source_code = source_code
        self.file_name = file_name
        self.node = node
        self.hint = hint
        super().__init__(format_diagnostic(self))

def format_diagnostic(diagnostic:CompileDiagnostic) -> str:
    lines = diagnostic.source_code.splitlines()
    lineno = getattr(diagnostic.node, "lineno", 1)
    col_offset = getattr(diagnostic.node, "col_offset", 0)
    end_col_offset = getattr(diagnostic.node, "end_col_offset", col_offset + 1)
    line_idx = lineno -1 
    code_line = lines[line_idx] if 0 <= line_idx < len(lines) else ""
    arrow = " " * col_offset + "^" * max(1, end_col_offset - col_offset)

    output = [
        f"Error: {diagnostic.message}",
        f"--------> {diagnostic.file_name}: {lineno} : {col_offset + 1}",
        f"         |",
        f"{lineno:2d}       | {code_line}",
        f"         | {arrow}",
    ]
    if diagnostic.hint:
        output.append("         |")
        output.append(f"    Help: {diagnostic.hint}")
    return "\n".join(output)
