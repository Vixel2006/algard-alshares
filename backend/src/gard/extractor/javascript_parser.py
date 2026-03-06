import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser
from typing import List
from gard.extractor.base import BaseParser
from gard.models import FunctionInfo

JS_LANGUAGE = Language(tsjs.language())
TS_LANGUAGE = Language(tsts.language_typescript())

class JSTSParsers(BaseParser):
    def __init__(self, language: Language, name: str):
        self.parser = Parser(language)
        self.language = language
        self.name = name

    def get_language_name(self) -> str:
        return self.name

    def parse_functions(self, file_path: str, content: str) -> List[FunctionInfo]:
        tree = self.parser.parse(bytes(content, "utf8"))
        functions = []
        
        # Query for function declarations, arrow functions, and method definitions
        query = self.language.query("""
            (function_declaration
                name: (identifier) @name) @func
            (variable_declarator
                name: (identifier) @name
                value: (arrow_function)) @func
            (method_definition
                name: (property_identifier) @name) @func
        """)
        
        captures = query.captures(tree.root_node)
        
        func_pairs = []
        current_func = None
        for node, tag in captures:
            if tag == "func":
                current_func = node
            elif tag == "name" and current_func:
                functions.append(FunctionInfo(
                    name=content[node.start_byte:node.end_byte],
                    file_path=file_path,
                    start_line=current_func.start_point[0] + 1,
                    end_line=current_func.end_point[0] + 1,
                    code=content[current_func.start_byte:current_func.end_byte]
                ))
                current_func = None
            
        return functions

class JSParser(JSTSParsers):
    def __init__(self):
        super().__init__(JS_LANGUAGE, "javascript")

class TSParser(JSTSParsers):
    def __init__(self):
        super().__init__(TS_LANGUAGE, "typescript")
