import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from functools import lru_cache
from typing import Optional
import gc
from gard.models import FunctionInfo, VulnerabilityReport
from gard.logger import get_logger

logger = get_logger(__name__)


class ModelCache:
    _instance: Optional["ModelCache"] = None
    _detector: Optional["VulnerabilityDetector"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_detector(
        self, model_name: str = "cisco-ai/SecureBERT2.0-code-vuln-detection"
    ) -> "VulnerabilityDetector":
        if self._detector is None or self._detector.model_name != model_name:
            self._detector = VulnerabilityDetector(model_name)
        return self._detector

    def clear_cache(self):
        global _cached_model, _cached_tokenizer
        if self._detector:
            del self._detector.model
            del self._detector.tokenizer
            self._detector = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Model cache cleared")


_cached_model: Optional[AutoModelForSequenceClassification] = None
_cached_tokenizer: Optional[AutoTokenizer] = None


class VulnerabilityDetector:
    def __init__(self, model_name: str = "cisco-ai/SecureBERT2.0-code-vuln-detection"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(
            "Initializing VulnerabilityDetector",
            model_name=model_name,
            device=self.device,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(
            self.device
        )
        self.model.eval()

    def detect_vulnerabilities(
        self, functions: list[FunctionInfo], batch_size: int = 4
    ) -> list[VulnerabilityReport]:
        reports = []

        for i in range(0, len(functions), batch_size):
            batch = functions[i : i + batch_size]
            codes = [f.code for f in batch]

            # Tokenize batch
            inputs = self.tokenizer(
                codes,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
                predictions = torch.argmax(logits, dim=1)

            for idx, func in enumerate(batch):
                pred_idx = int(predictions[idx].item())
                is_vulnerable = pred_idx == 1
                confidence = float(probabilities[idx][pred_idx].item())

                report = VulnerabilityReport(
                    function_name=func.name,
                    file_path=func.file_path,
                    is_vulnerable=is_vulnerable,
                    confidence=confidence,
                )
                reports.append(report)

            logger.info("Processed batch", size=len(batch), start_idx=i)

        return reports


def get_detector(
    model_name: str = "cisco-ai/SecureBERT2.0-code-vuln-detection",
) -> VulnerabilityDetector:
    """Get or create a cached VulnerabilityDetector instance."""
    cache = ModelCache()
    return cache.get_detector(model_name)


def clear_model_cache():
    """Clear the model cache and free GPU memory."""
    cache = ModelCache()
    cache.clear_cache()
