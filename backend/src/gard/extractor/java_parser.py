import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from typing import List
from gard.extractor.base import BaseParser
from gard.models import FunctionInfo

JAVA_LANGUAGE = Language(tsjava.language())

class JavaParser(BaseParser):
    def __init__(self):
        self.parser = Parser(JAVA_LANGUAGE)

    def get_language_name(self) -> str:
        return "java"

    def parse_functions(self, file_path: str, content: str) -> List[FunctionInfo]:
        tree = self.parser.parse(bytes(content, "utf8"))
        functions = []
        
        query = JAVA_LANGUAGE.query("""
            (method_declaration
                name: (identifier) @name) @func
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
