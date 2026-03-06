import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor
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

        query = Query(
            PY_LANGUAGE,
            """
            (function_definition
                name: (identifier) @name) @func
        """,
        )

        cursor = QueryCursor(query)
        captures = cursor.captures(tree.root_node)

        func_nodes = captures.get("func", [])
        name_nodes = captures.get("name", [])

        for func_node, name_node in zip(func_nodes, name_nodes):
            functions.append(
                FunctionInfo(
                    name=content[name_node.start_byte : name_node.end_byte],
                    file_path=file_path,
                    start_line=func_node.start_point[0] + 1,
                    end_line=func_node.end_point[0] + 1,
                    code=content[func_node.start_byte : func_node.end_byte],
                )
            )

        return functions
