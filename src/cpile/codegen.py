import ast 
from .analyzer import Analyzer
from .types import to_c_type, infer_type_from_value, get_format_specifier

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


class CodeGenerator:
    def __init__(self, tree, symbol_table):
        self.tree = tree
        self.symbol_table = symbol_table
        self.indent_level = 0
        self.lines = []
        self.declared_var = set()

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
            return f"{left} {c_ops} {right}"

        elif isinstance(node, ast.Call):
            func_name = self.generate_expr(node.func)
            if func_name == "print":
                arg = self.generate_expr(node.args[0])
                c_type = self.symbol_table.get(arg, "int32_t")
                format_spec = get_format_specifier(c_type)
                return f"printf(\"{format_spec}\\n\", {arg})"
            args = [self.generate_expr(arg) for arg in node.args]
            args_str = ", ".join(args)
            return f"{func_name}({args_str})"

    


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

    def generate_function(self, node: ast.FunctionDef):
        func_name = node.name
        if node.returns is not None :
            return_type = node.returns.id
            ret_c_type = to_c_type(return_type)
        else:
            ret_c_type = "void"

        param = []
        for arg in node.args.args:
            self.declared_var.add(arg.arg)
            arg_name = arg.arg
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
        var_c_type = to_c_type(node.annotation.id)
        var_value = self.generate_expr(node.value)
        self.declared_var.add(var_name)
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