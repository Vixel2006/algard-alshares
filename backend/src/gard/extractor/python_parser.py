import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from typing import List
from gard.extractor.base import BaseParser
from gard.models import FunctionInfo

PY_LANGUAGE = Language(tspython.language())

class PythonParser(BaseParser):
    def __init__(self):
        self.parser = Parser(PY_LANGUAGE)

    def get_language_name(self) -> str:
        return "python"

    def parse_functions(self, file_path: str, content: str) -> List[FunctionInfo]:
        tree = self.parser.parse(bytes(content, "utf8"))
        functions = []
        
        query = PY_LANGUAGE.query("""
            (function_definition
                name: (identifier) @name) @func
        """)
        
        captures = query.captures(tree.root_node)
        
        # tree-sitter returns a list of (node, tag) tuples
        # We need to pair @func with its @name
        func_nodes = [c[0] for c in captures if c[1] == "func"]
        name_nodes = [c[0] for c in captures if c[1] == "name"]
        
        for func_node, name_node in zip(func_nodes, name_nodes):
            functions.append(FunctionInfo(
                name=content[name_node.start_byte:name_node.end_byte],
                file_path=file_path,
                start_line=func_node.start_point[0] + 1,
                end_line=func_node.end_point[0] + 1,
                code=content[func_node.start_byte:func_node.end_byte]
            ))
            
        return functions
