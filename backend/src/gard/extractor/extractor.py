import os
from typing import List
from gard.extractor.factory import ParserFactory
from gard.models import FunctionInfo
import glob

class FunctionExtractor:
    def extract_functions(self, workspace_path: str) -> List[FunctionInfo]:
        all_functions = []
        for root, _, files in os.walk(workspace_path):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in [".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java"]: 
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    parser = ParserFactory.get_parser(ext)
                    functions = parser.parse_functions(file_path, content)
                    
                    # Basic test discovery logic
                    self._discover_tests(functions, root)
                    all_functions.extend(functions)
        
        return all_functions

    def _discover_tests(self, functions: List[FunctionInfo], root: str):
        # Placeholder for test discovery
        # Simple heuristic: look for test_*.py or *_test.py in the same dir or 'tests/' dir
        test_files = glob.glob(os.path.join(root, "test_*.py")) + glob.glob(os.path.join(root, "tests", "test_*.py"))
        
        for func in functions:
            for test_file in test_files:
                # This is a very rough heuristic
                func.test_file = test_file
                # In a real implementation, we'd parse the test file to find specific test functions
                func.test_function_names = [f"test_{func.name}"]
