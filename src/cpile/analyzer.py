
import ast
from .types import (
    to_c_type,
    get_format_specifier,
    infer_type_from_value,
    TranspileError,
)

class Analyzer :
    def __init__(self, source_code:str):
        """Get python source code parse and 
        travse source code store variable, type in dict"""
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.symbol_table = {}
        

    def analyze(self):
        """ Entry point to traverse"""
        for node in self.tree.body :
            self.visit(node)

    def visit(self, node):
        """Call the right method base on node type."""
        if isinstance(node, ast.FunctionDef):
            self.visit_function(node)
        elif isinstance(node, ast.If):
            self.visit_if(node)
        elif isinstance(node, ast.Assign):
            self.visit_assign(node)
        elif isinstance(node, ast.AnnAssign):
            self.visit_annassign(node)
        elif isinstance(node, ast.For):
            self.visit_for(node)
        elif isinstance(node, ast.While):
            self.visit_while(node)

    def visit_function(self, node: ast.FunctionDef):
        # Function name and returns type
        func_name = node.name
        if node.returns is not None:
            return_type = node.returns.id
            return_type_c_type = to_c_type(return_type)
            self.symbol_table[func_name] = return_type_c_type
        else:
            self.symbol_table[func_name] = "void"

        # Parameter
        for arg in node.args.args:
            arg_name = arg.arg 
            if arg.annotation is None :
                raise TranspileError(f"Parameter '{arg_name}' in function '{func_name}' is missing a type annotation")
            arg_type = arg.annotation.id
            arg_type_c_type = to_c_type(arg_type)
            self.symbol_table[arg_name] = arg_type_c_type        
        
        # function body 
        for stmt in node.body:
            self.visit(stmt)

    def visit_assign(self, node:ast.Assign):
        # assign node e.g. x = 5
        var_name = node.targets[0].id 
        var_value = node.value

        # Infer c-type from value and store in symbol table
        if isinstance(node.value, ast.Constant):
            var_type = infer_type_from_value(var_value)
            self.symbol_table[var_name] = var_type
        else : 
            pass
        
    def visit_annassign(self, node:ast.AnnAssign):
        var_name = node.target.id
        var_type = node.annotation.id
        var_value = node.value

        # covert python type to c type
        var_c_type = to_c_type(var_type)
        
        # infer python value to c type 
        if node.value is not None and isinstance(node.value, ast.Constant):
            value_c_type = infer_type_from_value(var_value)
            if var_c_type != value_c_type :
                raise TranspileError(f"Variable type '{var_c_type}' not match with value type '{value_c_type}' for variable name {var_name}")

        self.symbol_table[var_name] = var_c_type
            
    def visit_if(self, node:ast.If):
        for stmt in node.body :
            self.visit(stmt)

        for stmt in node.orelse:
            self.visit(stmt)

    def visit_for(self, node:ast.For):
        if isinstance(node.iter, ast.Call):
            target_name = node.target.id
            self.symbol_table[target_name] = "int32_t"
            
            for stmt in node.body:
                self.visit(stmt)
        
        elif isinstance(node.iter, ast.List):
            target_name = node.target.id
            for item in node.iter.elts:
                if isinstance(item, ast.Constant):
                    target_c_type = infer_type_from_value(item.value)
                self.symbol_table[target_name] = target_c_type
            
            for stmt in node.body:
                self.visit(stmt)

    def visit_while(self, node:ast.While):
        for stmt in node.body :
            self.visit(stmt)
            