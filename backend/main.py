from gard.extractor.python_parser import PythonParser
from gard.critic.detector import VulnerabilityDetector
from gard.actor import run_actor_agent
from gard.models import FunctionInfo


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


def main():
    parser = PythonParser()
    functions = parser.parse_functions("example.py", EXAMPLE_CODE)

    print(f"Found {len(functions)} functions:\n")
    for func in functions:
        print(f"  - {func.name} (lines {func.start_line}-{func.end_line})")
    print("\n--- Detecting vulnerabilities ---\n")

    detector = VulnerabilityDetector()
    reports = detector.detect_vulnerabilities(functions)

    for report in reports:
        status = "VULNERABLE" if report.is_vulnerable else "SAFE"
        print(f"Function: {report.function_name}")
        print(f"  Status: {status}")

        if report.is_vulnerable:
            func = next(f for f in functions if f.name == report.function_name)
            print("\n--- Generating patch ---\n")
            patch = run_actor_agent(func, report)
            print(f"  Explanation: {patch.explanation}")
            print(f"\n  Diff:")
            for line in patch.diff.split("\n"):
                print(f"    {line}")
        print()


if __name__ == "__main__":
    main()
