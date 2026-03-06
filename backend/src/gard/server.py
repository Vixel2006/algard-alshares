from fastapi import FastAPI
from gard.logger import setup_logger, logger
from gard.models import VulnerabilityReport, Patch, VerificationResult, FunctionInfo
from gard.extractor.extractor import FunctionExtractor

setup_logger()
app = FastAPI(title="SecurePatch Backend")
extractor = FunctionExtractor()

@app.get("/health")
async def health_check():
    logger.info("health_check_triggered")
    return {"status": "ok", "version": "0.1.0"}

@app.post("/extract")
async def extract_workspace_functions(workspace_path: str):
    logger.info("extract_workspace_functions_called", path=workspace_path)
    functions = extractor.extract_functions(workspace_path)
    return {"status": "success", "functions": functions}

@app.post("/scan")
async def scan_vulnerabilities(report: VulnerabilityReport):
    # Placeholder for Critic Agent
    logger.info("scan_vulnerabilities_called", function=report.function_name)
    return {"status": "received", "report": report}

@app.post("/patch")
async def generate_patch(patch: Patch):
    # Placeholder for Actor Agent
    logger.info("generate_patch_called", function=patch.function_name)
    return {"status": "received", "patch": patch}

@app.post("/verify")
async def verify_patch(result: VerificationResult):
    # Placeholder for Verifier Agent
    logger.info("verify_patch_called", function=result.function_name)
    return {"status": "received", "result": result}
