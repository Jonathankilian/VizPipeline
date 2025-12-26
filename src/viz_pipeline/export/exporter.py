"""
ExportEngine - File Export Management

Purpose:
    Export reports to disk (HTML, JSON, etc.)
"""

import json
from pathlib import Path
from ..core.types import Report


class ExportEngine:
    """
    Export reports to files.

    Purpose:
        Save HTML, JSON, and other report formats to disk.

    How to use:
        >>> exporter = ExportEngine()
        >>> exporter.export_html(report, "report.html")
        >>> exporter.export_json(report, "report.json")

    Attributes:
        None (stateless)
    """

    def export_html(self, report: Report, filepath: str) -> None:
        """
        Export HTML report to file.

        Inputs:
            report (Report): Complete report object
            filepath (str): Output file path

        What output:
            None (writes file)
        """
        if report.html_report is None:
            raise ValueError("Report has no HTML content (enable_export_html=False)")

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            f.write(report.html_report)

    def export_json(self, report: Report, filepath: str) -> None:
        """
        Export JSON summary to file.

        Inputs:
            report (Report): Complete report object
            filepath (str): Output file path

        What output:
            None (writes file)
        """
        if report.json_summary is None:
            raise ValueError("Report has no JSON summary")

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(report.json_summary, f, indent=2, default=str)

    def export_all(self, report: Report, output_dir: str) -> None:
        """
        Export all report formats to directory.

        Inputs:
            report (Report): Complete report object
            output_dir (str): Output directory path

        What output:
            None (writes files)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.export_html(report, str(output_dir / "report.html"))
        except ValueError:
            pass

        try:
            self.export_json(report, str(output_dir / "report.json"))
        except ValueError:
            pass