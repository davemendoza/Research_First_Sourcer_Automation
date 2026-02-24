from .llm_reasoning_engine import LLMReasoningEngine
from .citation_tracking_engine import CitationTrackingEngine
from .temporal_monitoring_engine import TemporalMonitoringEngine
from .succession_alert_engine import SuccessionAlertEngine

class IntelligenceOrchestrator:

    def __init__(self):

        self.reasoning = LLMReasoningEngine()
        self.citation = CitationTrackingEngine()
        self.temporal = TemporalMonitoringEngine()
        self.succession = SuccessionAlertEngine()

    def analyze_candidate(self, candidate):

        result = {}

        result["reasoning"] = self.reasoning.explain_score(candidate)
        result["citations"] = self.citation.track(candidate)
        result["temporal"] = self.temporal.analyze(candidate)
        result["succession"] = self.succession.evaluate(candidate)

        return result
