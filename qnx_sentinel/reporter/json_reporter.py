"""
QNX Sentinel - JSON Reporter
Serializes analysis reports and test outputs to standard machine-readable JSON.
"""

from pathlib import Path
from qnx_sentinel.core.models import AnalysisReport, TestRunReport


class JSONReporter:
    """Exports structured analysis reports to JSON format."""

    @staticmethod
    def render(report: AnalysisReport, indent: int = 2) -> str:
        return report.to_json(indent=indent)

    @staticmethod
    def save(report: AnalysisReport, output_path: str | Path, indent: int = 2) -> Path:
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report.to_json(indent=indent), encoding="utf-8")
        return out
