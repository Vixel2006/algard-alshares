import asyncio
from typing import List
from gard.models import FunctionInfo, FullVulnerabilityReport, VulnerabilityReport, Patch, VerificationResult
from gard.extractor.extractor import FunctionExtractor
from gard.critic.agent import run_critic_agent
from gard.actor.agent import run_actor_agent
from gard.verifier.agent import run_verifier_agent
from gard.logger import get_logger

logger = get_logger(__name__)

class SecurePatchPipeline:
    def __init__(self):
        self.extractor = FunctionExtractor()

    async def run_full_scan(self, workspace_path: str) -> List[FullVulnerabilityReport]:
        logger.info("Pipeline: Starting full workspace scan", path=workspace_path)
        
        # 1. Extract functions
        functions = self.extractor.extract_functions(workspace_path)
        logger.info("Pipeline: Extracted functions", count=len(functions))
        
        return await self.run_on_functions(functions)

    async def run_on_functions(self, functions: List[FunctionInfo]) -> List[FullVulnerabilityReport]:
        if not functions:
            return []

        # 2. Run Critic Agent (Vulnerability Detection)
        # Assuming run_critic_agent can handle multiple functions or we wrap it
        vulnerability_reports = await asyncio.to_thread(run_critic_agent, functions)
        
        # 3. Process vulnerable functions in parallel
        tasks = []
        for i, report in enumerate(vulnerability_reports):
            if report.is_vulnerable:
                tasks.append(self._process_vulnerable_function(functions[i], report))
        
        full_reports = await asyncio.gather(*tasks)
        
        # Add non-vulnerable functions to the final result if needed, 
        # or just return the ones that need attention.
        # For now, let's return all, but without patches for non-vulnerable ones.
        
        result = []
        vulnerable_map = {r.function.name: r for r in full_reports}
        
        for i, report in enumerate(vulnerability_reports):
            func = functions[i]
            if report.is_vulnerable and func.name in vulnerable_map:
                result.append(vulnerable_map[func.name])
            else:
                result.append(FullVulnerabilityReport(
                    function=func,
                    vulnerability=report,
                    patch=None,
                    verification=None
                ))
        
        logger.info("Pipeline: Scan completed", vulnerable_count=len(full_reports))
        return result

    async def _process_vulnerable_function(self, function_info: FunctionInfo, report: VulnerabilityReport) -> FullVulnerabilityReport:
        logger.info("Pipeline: Processing vulnerable function", name=function_info.name)
        
        # 4. Run Actor Agent (Patch Generation)
        try:
            # We might want to pass test code here if available
            patch = await asyncio.to_thread(run_actor_agent, function_info, report)
            
            # 5. Run Verifier Agent (Verification)
            verification = await asyncio.to_thread(run_verifier_agent, function_info, patch)
            
            return FullVulnerabilityReport(
                function=function_info,
                vulnerability=report,
                patch=patch,
                verification=verification
            )
        except Exception as e:
            logger.error("Pipeline: Error processing function", name=function_info.name, error=str(e))
            return FullVulnerabilityReport(
                function=function_info,
                vulnerability=report,
                patch=None,
                verification=None
            )
