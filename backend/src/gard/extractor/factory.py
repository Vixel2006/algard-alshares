from typing import Dict, Type
from gard.extractor.base import BaseParser
from gard.extractor.python_parser import PythonParser
from gard.extractor.javascript_parser import JSParser, TSParser
from gard.extractor.go_parser import GoParser
from gard.extractor.java_parser import JavaParser

class ParserFactory:
    _parsers: Dict[str, Type[BaseParser]] = {
        ".py": PythonParser,
        ".js": JSParser,
        ".jsx": JSParser,
        ".ts": TSParser,
        ".tsx": TSParser,
        ".go": GoParser,
        ".java": JavaParser,
    }

    @classmethod
    def get_parser(cls, file_extension: str) -> BaseParser:
        parser_class = cls._parsers.get(file_extension)
        if not parser_class:
            raise ValueError(f"No parser available for extension: {file_extension}")
        return parser_class()
