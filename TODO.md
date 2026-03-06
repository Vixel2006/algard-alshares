# SecurePatch - Implementation Plan

## Phase 1: Foundation (Week 1-2)

### 1.1 Project Setup
- [x] Initialize Python project with pyproject.toml
- [x] Set up logging with structlog
- [x] Create basic FastAPI server for backend
- [x] Initialize VS Code extension with TypeScript
- [x] Set up extension development environment

### 1.2 Basic Communication
- [x] Implement HTTP client in extension to talk to Python backend
- [x] Create health check endpoint
- [x] Set up extension activation/deactivation
- [x] Configure VS Code settings API

### 1.3 Data Models
- [x] Define FunctionInfo, VulnerabilityReport, Patch, VerificationResult models
- [x] Implement Pydantic schemas
- [x] Create serialization/deserialization utilities

## Phase 2: Function Extractor (Week 3)

### 2.1 AST Parsing
- [x] Install tree-sitter and language parsers
- [x] Implement multi-language function detection (Python, JS/TS, Java, Go)
- [x] Create function boundary identification
- [x] Handle nested functions and closures

### 2.2 Test Discovery
- [x] Implement test file discovery (test_*.py, *_test.js, etc.)
- [x] Map functions to their corresponding test functions
- [x] Handle test file patterns per language

### 2.3 Extension Integration
- [x] Create sidebar panel with function list
- [x] Implement inline decorations for detected functions

## Phase 3: Critic Agent - SecureBERT (Week 4-5)

### 3.1 Model Setup
- [ ] Download CiscoAI SecureBERT 2.0 model
- [ ] Set up local inference pipeline with transformers + torch
- [ ] Implement batch processing for multiple functions
- [ ] Add model caching and memory management

### 3.2 Vulnerability Detection
- [ ] Create VulnerabilityDetector class
- [ ] Implement CWE classification mapping
- [ ] Add confidence scoring
- [ ] Handle model output parsing

### 3.3 Tools Implementation
- [ ] Implement `get_function_code()` tool
- [ ] Implement `get_function_tests()` tool
- [ ] Integrate tools with agent framework

## Phase 4: Actor Agent - Gemini (Week 6-7)

### 4.1 Gemini Integration
- [ ] Set up Google GenAI client
- [ ] Configure Gemini 2.5 Flash model
- [ ] Implement API key management

### 4.2 Patch Generation
- [ ] Create PatchGenerator class
- [ ] Implement prompt templates for security fixes
- [ ] Add function context (code + tests) to prompts
- [ ] Implement diff generation

### 4.3 Tools Implementation
- [ ] Implement `get_function_code()` tool for Actor
- [ ] Implement `get_function_tests()` tool for Actor
- [ ] Add explanation generation

## Phase 5: Verifier Agent (Week 8)

### 5.1 Test Execution
- [ ] Create TestRunner class
- [ ] Implement pytest integration for Python
- [ ] Add jest integration for JavaScript/TypeScript
- [ ] Handle test discovery and execution

### 5.2 Result Parsing
- [ ] Parse test output (JSON format preferred)
- [ ] Implement regression detection
- [ ] Add timeout handling

### 5.3 Integration
- [ ] Implement `run_unit_tests()` tool
- [ ] Create verification result format
- [ ] Integrate with patch workflow

## Phase 6: Full Workflow Integration (Week 9)

### 6.1 Agent Orchestration
- [ ] Implement Critic → Actor → Verifier pipeline
- [ ] Add error handling and retry logic
- [ ] Implement parallel function scanning
- [ ] Add progress tracking

### 6.2 User Experience
- [ ] Implement "Fix" action in sidebar
- [ ] Add patch preview with diff view
- [ ] Implement accept/reject functionality
- [ ] Add "Fix All" and "Verify All" commands

### 6.3 Extension UI
- [ ] Create vulnerability list with severity
- [ ] Add inline decorations (color-coded by severity)
- [ ] Implement status bar updates
- [ ] Add hover tooltips

## Phase 7: Polish & Features (Week 10)

### 7.1 Advanced Features
- [ ] Implement scan on save
- [ ] Add auto-verify option
- [ ] Create progress notifications
- [ ] Add configuration UI in VS Code settings

### 7.2 Error Handling
- [ ] Add comprehensive error handling
- [ ] Implement user-friendly error messages
- [ ] Add logging for debugging

### 7.3 Performance
- [ ] Optimize function extraction
- [ ] Implement function caching
- [ ] Add parallel processing for scanning

## Phase 8: Testing & Release (Week 11-12)

### 8.1 Testing
- [ ] Write unit tests for Python backend
- [ ] Write integration tests for extension
- [ ] Test with real-world vulnerable codebases
- [ ] Perform security review

### 8.2 Documentation
- [ ] Create user documentation
- [ ] Write API documentation
- [ ] Add extension marketplace description

### 8.3 Release Preparation
- [ ] Configure vsce for publishing
- [ ] Create extension icon and assets
- [ ] Test extension installation
- [ ] Publish to VS Code Marketplace
