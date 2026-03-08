from fastapi import FastAPI, BackgroundTasks
from gard.logger import setup_logger, logger
from gard.models import VulnerabilityReport, Patch, VerificationResult, FunctionInfo, FullVulnerabilityReport
from gard.extractor.extractor import FunctionExtractor
from gard.pipeline import SecurePatchPipeline

setup_logger()
app = FastAPI(title="SecurePatch Backend")
extractor = FunctionExtractor()
pipeline = SecurePatchPipeline()

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
async def scan_workspace(workspace_path: str):
    logger.info("scan_workspace_called", path=workspace_path)
    reports = await pipeline.run_full_scan(workspace_path)
    return {"status": "success", "reports": reports}

@app.post("/scan-function")
async def scan_vulnerabilities(report: VulnerabilityReport):
    # This remains for single function scan if needed
    logger.info("scan_vulnerabilities_called", function=report.function_name)
    return {"status": "received", "report": report}

@app.post("/patch")
async def generate_patch(patch: Patch):
    logger.info("generate_patch_called", function=patch.function_name)
    return {"status": "received", "patch": patch}

@app.post("/verify")
async def verify_patch(result: VerificationResult):
    logger.info("verify_patch_called", function=result.function_name)
    return {"status": "received", "result": result}
