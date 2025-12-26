"""
ReportComposer - HTML & JSON Report Generation

Purpose:
    Assemble complete HTML and JSON reports from all pipeline outputs.
"""

from typing import Dict, Any
from ..core.types import PlotPlan, DataProfile, InferredType


class ReportComposer:
    """
    Compose HTML and JSON reports.

    Purpose:
        Generate human-readable HTML reports and machine-readable JSON summaries.

    How to use:
        >>> composer = ReportComposer()
        >>> html = composer.compose_html(plan, profile, type_assignment, audit)
        >>> json_summary = composer.compose_json_summary(plan, profile, ...)

    Attributes:
        None (stateless)
    """

    def compose_html(
            self,
            plot_plan: PlotPlan,
            data_profile: DataProfile,
            type_assignment: Dict[str, InferredType],
            audit_log: Dict[str, Any],
    ) -> str:
        """
        Generate HTML report.

        Inputs:
            plot_plan, data_profile, type_assignment, audit_log: From pipeline

        What output:
            str: Complete HTML document
        """
        sections = []

        sections.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VizPipeline Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
                table { border-collapse: collapse; width: 100%; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f0f0f0; }
                .metric { font-weight: bold; }
            </style>
        </head>
        <body>
        """)

        # Title
        sections.append("<h1>VizPipeline Report</h1>")

        # Overview section
        sections.append("<h2>Dataset Overview</h2>")
        sections.append(f"""
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Rows</td><td>{data_profile.n_rows}</td></tr>
            <tr><td>Columns</td><td>{data_profile.n_cols}</td></tr>
            <tr><td>Memory (MB)</td><td>{data_profile.memory_mb:.2f}</td></tr>
            <tr><td>Quality Issues</td><td>{len(data_profile.quality_issues)}</td></tr>
        </table>
        """)

        # Type inference section
        sections.append("<h2>Column Type Inference</h2>")
        sections.append("""
        <table>
            <tr><th>Column</th><th>Inferred Type</th><th>Confidence</th></tr>
        """)
        for col, ta in type_assignment.items():
            sections.append(f"""
            <tr>
                <td>{col}</td>
                <td>{ta.inferred_type.value}</td>
                <td>{ta.confidence:.2f}</td>
            </tr>
            """)
        sections.append("</table>")

        # Plot plan section
        sections.append("<h2>Selected Visualizations</h2>")
        sections.append(f"""
        <table>
            <tr><th>Plot Type</th><th>Count</th></tr>
            <tr><td>Univariate</td><td>{plot_plan.univariate_count}</td></tr>
            <tr><td>Bivariate</td><td>{plot_plan.bivariate_count}</td></tr>
            <tr><td>Multivariate</td><td>{plot_plan.multivariate_count}</td></tr>
            <tr><td><strong>Total</strong></td><td><strong>{len(plot_plan.items)}</strong></td></tr>
        </table>
        """)

        # Audit log section
        sections.append("<h2>Audit Log (Pipeline Decisions)</h2>")
        sections.append("<pre>")
        import json
        sections.append(json.dumps(audit_log, indent=2))
        sections.append("</pre>")

        sections.append("</body></html>")

        return "\n".join(sections)

    def compose_json_summary(
            self,
            plot_plan: PlotPlan,
            data_profile: DataProfile,
            type_assignment: Dict[str, InferredType],
            audit_log: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate JSON summary.

        Inputs:
            plot_plan, data_profile, type_assignment, audit_log: From pipeline

        What output:
            dict: Machine-readable summary (JSON-serializable)
        """
        return {
            "profile": data_profile.to_dict(),
            "type_assignment": {
                col: ta.to_dict() for col, ta in type_assignment.items()
            },
            "plot_plan": plot_plan.to_dict(),
            "audit_log": audit_log,
        }