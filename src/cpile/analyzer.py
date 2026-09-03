
import ast
from .types import (
    to_c_type,
    get_format_specifier,
    infer_type_from_value,
    TranspileError,
    is_list_type,
    get_list_element_type,
    TYPE_MAP,
)
from .errors import CompileDiagnostic

class Analyzer :
    def __init__(self, source_code:str, file_name: str = "<input>"):
        """Get python source code parse and 
        travse source code store variable, type in dict"""
        self.source_code = source_code
        self.file_name = file_name
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
        elif isinstance(node, ast.ClassDef):
            self.visit_classdef(node)

    def visit_function(self, node: ast.FunctionDef):
        # Function name and returns type
        func_name = node.name
        if node.returns is not None:
            if isinstance(node.returns, ast.Constant) and node.returns.value is None:
                return_type_c_type = "void"
            elif isinstance(node.returns, ast.Name):
                return_type_c_type = to_c_type(node.returns.id)
            else:
                return_type_c_type = "void"
            self.symbol_table[func_name] = return_type_c_type
        else:
            self.symbol_table[func_name] = "void"

        # Parameter
        for arg in node.args.args:
            arg_name = arg.arg 
            if arg.annotation is None :
                raise CompileDiagnostic(
                    message = f"Parameter '{arg_name}' in function '{func_name}' is missing a type annotation",
                    source_code = self.source_code,
                    file_name = self.file_name,
                    node = arg,
                    hint = f"Add a type hint like '{arg_name} : int'"
                )
            if is_list_type(arg.annotation):
                elem_c_type = get_list_element_type(arg.annotation)
                self.symbol_table[arg_name] = f"{elem_c_type}[]"
            else:
                arg_type = arg.annotation.id
                arg_type_c_type = to_c_type(arg_type)
                self.symbol_table[arg_name] = arg_type_c_type        
        
        # function body 
        for stmt in node.body:
            self.visit(stmt)

    def visit_assign(self, node:ast.Assign):
        # If mutating an array element (e.g. a[i] = temp), no new variable to declare
        if isinstance(node.targets[0], ast.Subscript):
            return

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
        var_value = node.value
        
        # check if it is list type ; list[]
        if is_list_type(node.annotation):
            elem_c_type = get_list_element_type(node.annotation)
            self.symbol_table[var_name] = f"{elem_c_type}[]"
            return

        var_type = node.annotation.id
        # covert python type to c type
        var_c_type = to_c_type(var_type)
        
        # infer python value to c type 
        if node.value is not None and isinstance(node.value, ast.Constant):
            value_c_type = infer_type_from_value(var_value)
            if var_c_type != value_c_type :
                raise CompileDiagnostic(
                    message = f"Variable type '{var_c_type}' not match with value type '{value_c_type}' for variable name {var_name}",
                    source_code = self.source_code,
                    file_name = self.file_name,
                    node = node,
                    hint = f"Change declaration to '{var_name}: {value_c_type}' or check assigned value"
                )

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
            
    def visit_classdef(self, node:ast.ClassDef):
        class_name = node.name
        # Register node.name to Type map so class will recognized as a type 
        TYPE_MAP[class_name] = class_name
        # add struct definition to symbol table
        struct_fields = {}
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                field_name = stmt.target.id
                field_type = stmt.annotation.id 
                field_c_type = to_c_type(field_type)
                struct_fields[field_name] = field_c_type
        self.symbol_table[class_name] = struct_fields

