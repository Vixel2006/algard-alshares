import asyncio
import os
from gard.extractor.python_parser import PythonParser
from gard.pipeline import SecurePatchPipeline
from gard.logger import setup_logger

setup_logger()

EXAMPLE_CODE = """
import os
import pickle

def login_user(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    return cursor.fetchone()

def safe_login(username, password):
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    return cursor.fetchone()

def execute_command(cmd):
    os.system(cmd)

def deserialize_data(data):
    return pickle.loads(data)

def check_permissions(user_id):
    if user_id == 1:
        return True
    return False

def hardcoded_secret():
    api_key = "sk-1234567890abcdef"
    return api_key
"""


async def main():
    parser = PythonParser()
    functions = parser.parse_functions("example.py", EXAMPLE_CODE)

    print(f"Found {len(functions)} functions:\n")
    for func in functions:
        print(f"  - {func.name} (lines {func.start_line}-{func.end_line})")
    
    print("\n--- Running SecurePatch Pipeline ---\n")

    pipeline = SecurePatchPipeline()
    reports = await pipeline.run_on_functions(functions)

    for report in reports:
        status = "VULNERABLE" if report.vulnerability.is_vulnerable else "SAFE"
        print(f"Function: {report.function.name}")
        print(f"  Status: {status}")

        if report.vulnerability.is_vulnerable:
            print(f"  CWE: {report.vulnerability.cwe_id if hasattr(report.vulnerability, 'cwe_id') else 'N/A'}")
            
            if report.patch:
                print("\n  --- Generated Patch ---")
                print(f"  Explanation: {report.patch.explanation}")
                print(f"\n  Diff:")
                for line in report.patch.diff.split("\n"):
                    print(f"    {line}")
            
            if report.verification:
                print(f"\n  --- Verification ---")
                print(f"  Status: {report.verification.status}")
                if report.verification.status == "passed":
                    print("  ✅ Verification successful!")
                else:
                    print("  ❌ Verification failed or errored.")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
