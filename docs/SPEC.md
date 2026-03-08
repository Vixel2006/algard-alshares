# SecurePatch - VS Code Security Vulnerability Patching Extension

## Project Overview

**Project Name:** SecurePatch  
**Type:** VS Code Extension with Python Backend  
**Core Functionality:** Actor-Critic multi-agent system that detects security vulnerabilities in functions, generates patches using an LLM, and verifies fixes via unit tests  
**Target Users:** Developers who want to identify and fix security vulnerabilities in their codebases

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VS Code Extension                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Extension UI (TypeScript)                 │   │
│  │  - Sidebar: Vulnerability list & patch preview               │   │
│  │  - Inline decorations: Highlight vulnerable functions       │   │
│  │  - Command palette: Scan, Fix All, Verify                   │   │
│  │  - Status bar: Scan status & counts                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                               │                                      │
│                    JSON-RPC / HTTP                                   │
│                               ▼                                      │
├─────────────────────────────────────────────────────────────────────┤
│                     Python Backend Service                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Function Extractor (AST-based)                  │   │
│  │  - Parses source code to identify functions                  │   │
│  │  - Extracts function code, signature, imports                │   │
│  │  - Finds associated unit tests                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                               │                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │    Critic    │───►│    Actor     │───►│   Verifier   │         │
│  │   Agent      │    │   Agent      │    │   Agent      │         │
│  │ (SecureBERT) │    │(Gemini 2.5)  │    │ (Test Runner)│         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│         │                   │                   │                  │
│         ▼                   ▼                   ▼                  │
│  - Vulnerability      - Patch generation   - Unit test execution   │
│    detection         - Code generation     - Regression check       │
│  - CWE classification - Explanation         - Validation report     │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Design (Actor-Critic)

#### 1. Critic Agent (Detection)
- **Model:** CiscoAI SecureBERT 2.0 Code Vuln Detection
- **Access:** Local inference (Hybrid - local model + cloud LLM)
- **Responsibility:** Analyze functions for security vulnerabilities
- **Tools:**
  - `get_function_code(function_name, file_path)` - Retrieve function source
  - `get_function_tests(function_name)` - Find associated unit tests
- **Output:** `VulnerabilityReport` with:
  - `is_vulnerable`: boolean
  - `cwe_id`: str (e.g., "CWE-89" for SQL injection)
  - `severity`: "critical" | "high" | "medium" | "low"
  - `explanation`: str (why it's vulnerable)
  - `confidence`: float (0-1)

#### 2. Actor Agent (Patch Generation)
- **Model:** Google Gemini 2.5 Flash
- **Access:** Google AI Studio API
- **Respons patches for vulnerabilities
- **Tools:**
ibility:** Generate secure  - `get_function_code(function_name, file_path)` - Context for patching
  - `get_function_tests(function_name)` - Tests to preserve
- **Input:** Vulnerability report from Critic
- **Output:** `Patch` with:
  - `patched_code`: str
  - `explanation`: str (what was changed and why)
  - `diff`: str (unified diff format)

#### 3. Verifier Agent
- **Responsibility:** Ensure patch doesn't break functionality
- **Tools:**
  - `run_unit_tests(function_name)` - Execute associated tests
  - `get_test_results()` - Parse test output
- **Input:** Patched code + original tests
- **Output:** `VerificationResult` with:
  - `status`: "passed" | "failed" | "error"
  - `tests_run`: int
  - `tests_passed`: int
  - `test_output`: str
  - `regression_detected`: boolean

### Communication Flow

```
User triggers scan
       │
       ▼
Function Extractor identifies all functions in workspace
       │
       ▼
For each function:
  ┌──────────────────────────────────────┐
  │  Critic Agent (SecureBERT)          │
  │  - get_function_code()               │
  │  - Analyze for vulnerabilities      │
  └──────────────┬───────────────────────┘
                │
        [Vulnerable?]
                │
       Yes      │ No
       ▼        ▼
  ┌──────────┐  Skip
  │  Actor   │
  │  Agent   │
  │(Gemini)  │
  └────┬─────┘
       │
       ▼
  ┌──────────────────┐
  │  Verifier Agent │
  │  - run_unit_tests│
  └────────┬─────────┘
           │
           ▼
    User presented with:
    - Vulnerability info
    - Patch preview
    - Test results
    - Accept/Reject
```

## Tech Stack

### VS Code Extension (TypeScript)
- **Language:** TypeScript 5.x
- **Framework:** VS Code Extension API
- **IPC:** HTTP/JSON-RPC to Python backend
- **Dependencies:**
  - `vscode` - Extension API
  - `axios` - HTTP client

### Python Backend
- **Language:** Python 3.11+
- **Dependencies:**
  - `transformers` - SecureBERT model loading/inference
  - `torch` - ML runtime
  - `google-genai` - Gemini API client
  - `tree-sitter` + `tree-sitter-lang` - Multi-language AST parsing
  - `pytest` - Test execution
  - `pydantic` - Data validation
  - `structlog` - Logging
  - `fastapi` - Optional HTTP server
  - `uvicorn` - ASGI server

### Data Models

```python
class VulnerabilityReport(BaseModel):
    function_name: str
    file_path: str
    is_vulnerable: bool
    cwe_id: str | None
    severity: Literal["critical", "high", "medium", "low"]
    explanation: str
    confidence: float

class Patch(BaseModel):
    function_name: str
    file_path: str
    original_code: str
    patched_code: str
    explanation: str
    diff: str

class VerificationResult(BaseModel):
    function_name: str
    status: Literal["passed", "failed", "error"]
    tests_run: int
    tests_passed: int
    test_output: str
    regression_detected: bool

class FunctionInfo(BaseModel):
    name: str
    file_path: str
    start_line: int
    end_line: int
    code: str
    test_file: str | None
    test_function_names: list[str]
```

## Extension Features

1. **Sidebar Panel**
   - List of detected vulnerabilities
   - Severity indicators (color-coded)
   - "Fix" and "Verify" actions per item
   - Patch preview with diff view

2. **Inline Decorations**
   - Highlight vulnerable functions in editor
   - Color by severity (red=critical, orange=high, yellow=medium, blue=low)

3. **Command Palette**
   - `SecurePatch: Scan Workspace` - Full scan
   - `SecurePatch: Scan File` - Single file
   - `SecurePatch: Fix All` - Apply all patches
   - `SecurePatch: Verify` - Run verification

4. **Status Bar**
   - Scan progress
   - Vulnerability count by severity

5. **Hover Tooltips**
   - Quick vulnerability summary
   - "Fix" action button

## Configuration

- `securepatch.geminiApiKey`: string (Google AI Studio - VS Code secrets)
- `securepatch.securebertPath`: string (path to local model)
- `securepatch.scanOnSave`: boolean (default: true)
- `securepatch.autoVerify`: boolean (default: true)
- `securepatch.severityThreshold`: "critical" | "high" | "medium" | "low"
- `securepatch.languages`: string[] (default: ["python", "javascript", "typescript", "java", "go"])
- `securepatch.maxFunctionLines`: int (skip functions > N lines, default: 500)

## Multi-Language Support

Initial language support:
- **Python** - Full support (tree-sitter-python, pytest)
- **C, C++** - Full support

Function detection via:
- AST parsing with tree-sitter
- Function definition patterns per language
- Test file discovery (e.g., `test_*.py`, `*_test.js`, `*_test.go`)
