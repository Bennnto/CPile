import ast 
from .analyzer import Analyzer
from .types import to_c_type, infer_type_from_value, get_format_specifier, get_list_element_type, is_list_type

OPERATORS_MAP = {
    ast.Add : "+",
    ast.Sub : "-",
    ast.Mult : "*",
    ast.Div : "/",
    ast.Mod : "%",
    ast.Eq : "==",
    ast.NotEq : "!=",
    ast.Lt : "<",
    ast.LtE : "<=",
    ast.Gt : ">",
    ast.GtE : ">=",
    ast.And : "&&",
    ast.Or : "||",
    ast.Not : "!",
}

MATH_FUNC = {
    "math.sqrt" : "sqrt",
    "math.pow" : "pow",
    "math.fabs" : "fabs",
    "math.floor" : "floor",
    "math.ceil" : "ceil",
    "abs" : "fabs",
}


class CodeGenerator:
    def __init__(self, tree, symbol_table):
        self.tree = tree
        self.symbol_table = symbol_table
        self.indent_level = 0
        self.lines = []
        self.declared_var = set()
    
    def is_main_block(self, node):
        if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name):
            if node.test.left.id == "__name__":
                return True
        return False

    def emit(self, text:str = ""):
        """Append an indented line of c code to self.lines"""
        if text == "":
            self.lines.append("")
        else:
            indent_str = "  " * self.indent_level
            self.lines.append(f"{indent_str}{text}")

    def generate(self) -> str:
        self.emit("#include <stdio.h>")
        self.emit("#include <stdbool.h>")
        self.emit("#include <stdint.h>")
        self.emit("#include <string.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <math.h>")
        self.emit("")

        # Generate all nodes in AST tree
        for node in self.tree.body :
            self.generate_node(node)
            self.emit("") # Blank line between function

        # Join all line into a single C-String
        return "\n".join(self.lines)

    def generate_expr(self, node) -> str:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "true" if node.value else "false"
            elif isinstance(node.value, str):
                return f'"{node.value}"'
            return str(node.value)
        
        elif isinstance(node, ast.Name):
            return node.id

        elif isinstance(node, ast.BinOp):
            left = self.generate_expr(node.left)
            right = self.generate_expr(node.right)
            ops = node.op
            c_ops = OPERATORS_MAP[type(ops)]
            return f"{left} {c_ops} {right}"

        elif isinstance(node, ast.BoolOp):
            left  = self.generate_expr(node.values[0])
            right = self.generate_expr(node.values[1])
            ops = node.op
            c_ops = OPERATORS_MAP[type(ops)]
            return f"{left} {c_ops} {right}"

        elif isinstance(node, ast.UnaryOp):
            operand = self.generate_expr(node.operand)
            ops = node.op
            c_ops = OPERATORS_MAP[type(ops)]
            return f"{c_ops} {operand}"

        elif isinstance(node, ast.Compare):
            left = self.generate_expr(node.left)
            ops = node.ops[0]
            right = self.generate_expr(node.comparators[0])
            c_ops = OPERATORS_MAP[type(ops)]
            is_left_str = isinstance(node.left, ast.Constant) and isinstance(node.left.value, str) or self.symbol_table.get(getattr(node.left, 'id', None)) == "char*"
            is_right_str = isinstance(node.comparators[0], ast.Constant) and isinstance(node.comparators[0].value, str) or self.symbol_table.get(getattr(node.comparators[0], 'id', None)) == "char*"
            if is_left_str or is_right_str:
                if isinstance(ops, ast.Eq):
                    return f"strcmp({left}, {right}) == 0"
                elif isinstance(ops, ast.NotEq):
                    return f"strcmp({left}, {right}) != 0"
                
            return f"{left} {c_ops} {right}"

        elif isinstance(node, ast.Call):
            func_name = self.generate_expr(node.func)
            if func_name in self.symbol_table and isinstance(self.symbol_table[func_name], dict):
                args = [self.generate_expr(arg) for arg in node.args]
                return f"({func_name}){{{', '.join(args)}}}"

            if func_name == "print":
                if len(node.args) == 1 and isinstance(node.args[0], ast.JoinedStr):
                    joined = node.args[0]
                    fmt_parts = []
                    printf_args = []
                    for piece in joined.values:
                        if isinstance(piece, ast.Constant):
                            fmt_parts.append(str(piece.value))
                        elif isinstance(piece, ast.FormattedValue):
                            expr_code = self.generate_expr(piece.value)
                            var_type = self.symbol_table.get(expr_code, "int32_t")
                            spec = get_format_specifier(var_type)
                            fmt_parts.append(spec)
                            printf_args.append(expr_code)
                    final_fmt = "".join(fmt_parts) + "\\n" 
                    if printf_args:
                        return f'printf("{final_fmt}", {", ".join(printf_args)})'
                    else:
                        return f'printf("{final_fmt}")'
                args = [self.generate_expr(arg) for arg in node.args]
                c_types = []
                for raw_node, arg_str in zip(node.args, args):
                    if isinstance(raw_node, ast.Constant) and isinstance(raw_node.value, str):
                        c_types.append("char*")
                    elif isinstance(raw_node, ast.Constant) and isinstance(raw_node.value, float):
                        c_types.append("double")
                    else:
                        c_types.append(self.symbol_table.get(arg_str, "int32_t")) 
                format_spec = [get_format_specifier(c_type) for c_type in c_types]
                format_str = "".join(format_spec) + "\\n"
                return f"printf(\"{format_str}\", {', '.join(args)})"
            elif func_name == "len":
                arg = self.generate_expr(node.args[0])
                return f"(int32_t)strlen({arg})"
            elif func_name in MATH_FUNC:
                c_func = MATH_FUNC[func_name]
                args = [self.generate_expr(arg) for arg in node.args]
                return f"{c_func}({', '.join(args)})"
            args = [self.generate_expr(arg) for arg in node.args]
            args_str = ", ".join(args)
            return f"{func_name}({args_str})"

        elif isinstance(node, ast.Subscript):
            arr = self.generate_expr(node.value)
            idx = self.generate_expr(node.slice)
            return f"{arr}[{idx}]"

        elif isinstance(node, ast.List):
            items = [self.generate_expr(elt) for elt in node.elts]
            return f"{{{','.join(items)}}}"    

        elif isinstance(node, ast.Attribute):
            obj = self.generate_expr(node.value)
            return f"{obj}.{node.attr}"
        
        elif isinstance(node, ast.IfExp):
            cond = self.generate_expr(node.test)
            true_expr = self.generate_expr(node.body)
            false_expr = self.generate_expr(node.orelse)
            return f"({cond} ? {true_expr} : {false_expr})"
            
            

    def generate_node(self, node) -> str :
        if isinstance(node, ast.FunctionDef):
            self.generate_function(node)
        elif isinstance(node, ast.Expr):
            expr_str = self.generate_expr(node.value)
            self.emit(f"{expr_str};")
        elif isinstance(node, ast.If):
            self.generate_if(node)
        elif isinstance(node, ast.Return):
            self.generate_return(node)
        elif isinstance(node, ast.While):
            self.generate_while(node)
        elif isinstance(node, ast.For):
            self.generate_for(node)
        elif isinstance(node, ast.AnnAssign):
            self.generate_annassign(node)
        elif isinstance(node, ast.Assign):
            self.generate_assign(node)
        elif isinstance(node, ast.ClassDef):
            self.generate_classdef(node)
        elif isinstance(node, ast.Break):
            self.emit(f"break;")
        elif isinstance(node, ast.Continue):
            self.emit(f"continue;")
        elif isinstance(node, ast.AugAssign):
            self.generate_augassign(node)

    def generate_function(self, node: ast.FunctionDef):
        func_name = node.name
        if node.returns is not None:
            if isinstance(node.returns, ast.Constant) and node.returns.value is None:
                ret_c_type = "void"
            elif isinstance(node.returns, ast.Name):
                ret_c_type = to_c_type(node.returns.id)
            else:
                ret_c_type = "void"
        else:
            ret_c_type = "void"

        param = []
        for arg in node.args.args:
            self.declared_var.add(arg.arg)
            arg_name = arg.arg
            if is_list_type(arg.annotation):
                elem_c_type = get_list_element_type(arg.annotation)
                param.append(f"{elem_c_type} {arg_name}[]")
            else:
                arg_type = arg.annotation.id
                arg_c_type = to_c_type(arg_type)
                param.append(f"{arg_c_type} {arg_name}")
        param_str = ", ".join(param)
        self.emit(f"{ret_c_type} {func_name} ({param_str}) {{")
        self.indent_level +=1
        for stmt in node.body:
            self.generate_node(stmt)
        self.indent_level -= 1
        self.emit("}")

    def generate_if(self, node:ast.If):
        #1. Execute function e.g if __name__ == "__main__" :
        if self.is_main_block(node):
            self.emit(f"int main (void) {{")
            self.indent += 1 
            for stmt in node.body:
                self.generate_expr(stmt)
            self.emit(f"return 0;")
            self.indent -= 1
            self.emit("}")
            return

        #2. Regualr if_else 
        test_str = self.generate_expr(node.test)
        self.emit(f"if ({test_str}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.generate_node(stmt)
        self.indent_level -= 1

        curr = node
        while curr.orelse:
            if len(curr.orelse) == 1 and isinstance(curr.orelse[0], ast.If):
                curr = curr.orelse[0]
                elif_test = self.generate_expr(curr.test)
                self.emit(f"}} else if ({elif_test}) {{")
                self.indent_level += 1
                for stmt in curr.body:
                    self.generate_node(stmt)
                self.indent_level -= 1
            else:
                self.emit("} else {")
                self.indent_level += 1
                for stmt in curr.orelse:
                    self.generate_node(stmt)
                self.indent_level -= 1
                break
        self.emit("}")

    def generate_return(self, node:ast.Return):
        return_value = self.generate_expr(node.value)
        self.emit(f"return {return_value};")

    def generate_assign(self, node:ast.Assign):
        if isinstance(node.targets[0], ast.Subscript):
            target_str = self.generate_expr(node.targets[0])
            value_str = self.generate_expr(node.value)
            self.emit(f"{target_str} = {value_str};")
        elif isinstance(node.targets[0], ast.Attribute):
            target_str = self.generate_expr(node.targets[0])
            value_str = self.generate_expr(node.value)
            self.emit(f"{target_str} = {value_str};")
        else:
            var_name = node.targets[0].id 
            var_value = self.generate_expr(node.value)
            if var_name in self.declared_var :
                self.emit(f"{var_name} = {var_value};")
            else :
                self.declared_var.add(var_name)
                var_c_type = self.symbol_table.get(var_name, "int32_t")
                self.emit(f"{var_c_type} {var_name} = {var_value};")
            

    def generate_annassign(self, node:ast.AnnAssign):
        var_name = node.target.id
        self.declared_var.add(var_name)
        if is_list_type(node.annotation):
            if isinstance(node.annotation.slice, ast.Subscript) and is_list_type(node.annotation.slice):
                elem_c_type = get_list_element_type(node.annotation.slice)
                row = len(node.value.elts)
                col = len(node.value.elts[0].elts)
                var_value = self.generate_expr(node.value)
                self.emit(f"{elem_c_type} {var_name}[{row}][{col}] = {var_value};")
            else:
                elem_c_type = get_list_element_type(node.annotation)
                var_value = self.generate_expr(node.value)
                if isinstance(node.value, ast.List):
                    size = len(node.value.elts)
                    self.emit(f"{elem_c_type} {var_name}[{size}] = {var_value};")
                else :
                    self.emit(f"{elem_c_type} {var_name}[] = {var_value};")
        else:
            var_c_type = to_c_type(node.annotation.id)
            var_value = self.generate_expr(node.value)
            self.emit(f"{var_c_type} {var_name} = {var_value};")
    
    def generate_while(self, node:ast.While):
        cond_str = self.generate_expr(node.test)
        self.emit(f"while ({cond_str}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.generate_node(stmt)
        self.indent_level -= 1
        self.emit("}")

    def generate_for(self, node:ast.For):
        target = node.target.id

        args = node.iter.args
        if len(args) == 1:
            start_str = "0"
            stop_str = self.generate_expr(args[0])
        elif len(args) >= 2:
            start_str = self.generate_expr(args[0])
            stop_str = self.generate_expr(args[1])
        if len(args) == 3:
            step_str = self.generate_expr(args[2])
            inc_str = f"{target} += {step_str}"
        else:
            inc_str = f"{target} += 1"

        self.emit(f"for (int32_t {target} = {start_str}; {target} < {stop_str}; {inc_str}) {{")
        self.indent_level += 1
        for stmt in node.body :
            self.generate_node(stmt)
        self.indent_level -= 1
        self.emit("}")

    def generate_classdef(self, node:ast.ClassDef):
        class_name = node.name
        self.emit(f"typedef struct {{")
        self.indent_level += 1
        for stmt in node.body :
            if isinstance(stmt, ast.AnnAssign):
                field_name = stmt.target.id
                field_type = stmt.annotation.id 
                field_c_type = to_c_type(field_type)
                self.emit(f"{field_c_type} {field_name};")
        self.indent_level -= 1
        self.emit(f"}} {class_name};\n")

    def generate_augassign(self, node:ast.AugAssign):
        target_str = self.generate_expr(node.target)
        op_str = OPERATORS_MAP[type(node.op)]
        val_str = self.generate_expr(node.value)
        self.emit(f"{target_str} {op_str}= {val_str};")

