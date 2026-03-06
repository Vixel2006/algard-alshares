from abc import ABC, abstractmethod
from typing import List
from gard.models import FunctionInfo

class BaseParser(ABC):
    @abstractmethod
    def parse_functions(self, file_path: str, content: str) -> List[FunctionInfo]:
        """Parse functions from the given file content."""
        pass

    @abstractmethod
    def get_language_name(self) -> str:
        """Return the language name supported by this parser."""
        pass
