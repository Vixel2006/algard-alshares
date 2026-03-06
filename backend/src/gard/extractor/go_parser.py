import tree_sitter_go as tsgo
from tree_sitter import Language, Parser
from typing import List
from gard.extractor.base import BaseParser
from gard.models import FunctionInfo

GO_LANGUAGE = Language(tsgo.language())

class GoParser(BaseParser):
    def __init__(self):
        self.parser = Parser(GO_LANGUAGE)

    def get_language_name(self) -> str:
        return "go"

    def parse_functions(self, file_path: str, content: str) -> List[FunctionInfo]:
        tree = self.parser.parse(bytes(content, "utf8"))
        functions = []
        
        query = GO_LANGUAGE.query("""
            (function_declaration
                name: (identifier) @name) @func
            (method_declaration
                name: (field_identifier) @name) @func
        """)
        
        captures = query.captures(tree.root_node)
        
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
