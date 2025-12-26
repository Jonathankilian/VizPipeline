"""
VizPipeline Orchestrator - Core Pipeline Orchestration

Purpose:
    Central coordinator that executes the complete visualization workflow:
    1. Profiling → 2. Type Inference → 3. Relationship Scoring
    → 4. Decision Engine → 5. Plot Generation → 6. Report Composition
    → 7. Final Report Assembly

All steps are modular and independently testable.
"""

from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime

from .types import Report, PlotPlan, InferredType
from .config import VizConfig, DEFAULT_CONFIG
from ..profiling.profiler import DataframeProfiler
from ..typing.inferencer import ColumnTypeInferencer
from ..scoring.scorer import RelationshipScorer
from ..decision.engine import DecisionEngine
from ..plotting.factory import PlotFactory
from ..reporting.composer import ReportComposer
from ..export.exporter import ExportEngine
from ..diagnostics.logging import LogManager


class VizPipeline:
    """
    Central orchestrator for the complete visualization pipeline.

    Purpose:
        Execute full data visualization workflow from raw DataFrame to
        polished Report with plots, audit logs, and HTML/JSON exports.

    How to use:
        >>> import pandas as pd
        >>> from viz_pipeline import VizPipeline, VizConfig
        >>> 
        >>> df = pd.read_csv("data.csv")
        >>> config = VizConfig(max_univariate_plots=20)
        >>> report = VizPipeline.run(df, target_cols=["churn"], config=config)
        >>> 
        >>> print(f"Selected {report.plot_plan.univariate_count} univariate plots")
        >>> print(f"Warnings: {report.warnings}")
        >>> with open("report.html", "w") as f:
        ...     f.write(report.html_report)

    Attributes:
        None (stateless class - use @staticmethod methods)
    """

    @staticmethod
    def run(
            df: pd.DataFrame,
            target_cols: Optional[List[str]] = None,
            id_cols: Optional[List[str]] = None,
            config: Optional[VizConfig] = None,
    ) -> Report:
        """
        Execute complete visualization pipeline.

        Purpose:
            Process a pandas DataFrame through all 7 pipeline steps:
            1. Profile data (shape, dtypes, quality issues)
            2. Infer column types (numeric, categorical, datetime, etc.)
            3. Score all bivariate relationships
            4. Select plots using decision heuristics
            5. Generate matplotlib figures for each plot
            6. Compose HTML and JSON reports
            7. Assemble final Report object with audit trail

        Inputs:
            df (pd.DataFrame): Cleaned data with no duplicates, consistent dtypes.
                Minimum: 10 rows, 1 column.
                Can be cleaned with: df.drop_duplicates().astype(...).fillna(...)

            target_cols (List[str], optional): Column names that are target variables.
                If provided, bivariate plots prioritize (feature, target) relationships.
                Example: ["churn", "target"]
                Default: None (generic bivariate selection)

            id_cols (List[str], optional): Column names that are identifiers (skipped).
                Example: ["id", "customer_id", "employee_id"]
                Default: None (auto-detection by naming patterns)

            config (VizConfig, optional): Configuration with toggles and limits.
                Controls: plot limits, sampling, export format, seed, feature toggles.
                Default: DEFAULT_CONFIG (sensible defaults)

        What output:
            Report: Complete dataclass containing:
                - plot_plan (PlotPlan): Ranked list of selected plots
                - data_profile (DataProfile): Dataset statistics
                - type_assignment (Dict[str, InferredType]): Column types
                - html_report (str): Full HTML document (if enabled)
                - json_summary (dict): Machine-readable summary
                - audit_log (dict): All decisions and rules fired
                - warnings (List[str]): Non-blocking issues
                - errors (List[str]): Critical issues
                - metadata (dict): Version, timestamp, seed, config

        Warnings/Failure modes:
            - IF df.shape[0] < 10: Raises ValueError("DataFrame has X rows; minimum 10")
            - IF target_cols not in df.columns: Raises KeyError("Missing columns: {set}")
            - IF id_cols not in df.columns: Raises KeyError("Missing columns: {set}")
            - IF df is not pd.DataFrame: Raises TypeError("Expected pd.DataFrame, got ...")
            - IF no plots selected (sparse/unusual data): Produces report with warnings
            - IF enable_sampling=True and n > limit: Data is downsampled (stratified)
            - IF plotting fails for item: Logged as warning, pipeline continues

        Determinism/Performance:
            - Deterministic: Yes (if seed is set, row order identical)
            - Typical runtime: ~10s for n=10k, p=20 (depends on hardware + toggles)

        Raises:
            ValueError: If df.shape[0] < 10
            KeyError: If target_cols or id_cols not in df.columns
            TypeError: If df is not pd.DataFrame

        Example:
            >>> df = pd.DataFrame({
            ...     "age": [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
            ...     "income": [30, 45, 50, 60, 70, 80, 90, 100, 110, 120],
            ...     "churn": [0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
            ... })
            >>> report = VizPipeline.run(df, target_cols=["churn"])
            >>> print(f"Generated {len(report.plot_plan.items)} plots")
        """

        # ========== INITIALIZATION ==========
        config = config or DEFAULT_CONFIG
        log = LogManager(
            enabled=config.enable_audit_log,
            enable_warnings=config.enable_warnings
        )

        # Set seed for reproducibility
        np.random.seed(config.seed)

        start_time = datetime.now()

        # ========== INPUT VALIDATION ==========
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pd.DataFrame, got {type(df)}")

        if df.shape[0] < 10:
            raise ValueError(f"DataFrame has {df.shape[0]} rows; minimum 10 required")

        target_cols = target_cols or []
        id_cols = id_cols or []

        if target_cols and not all(col in df.columns for col in target_cols):
            missing = set(target_cols) - set(df.columns)
            raise KeyError(f"target_cols not in DataFrame: {missing}")

        if id_cols and not all(col in df.columns for col in id_cols):
            missing = set(id_cols) - set(df.columns)
            raise KeyError(f"id_cols not in DataFrame: {missing}")

        log.log_decision(
            "PIPELINE_START",
            {
                "n_rows": df.shape[0],
                "n_cols": df.shape[1],
                "seed": config.seed,
                "target_cols": target_cols,
                "id_cols": id_cols,
            }
        )

        # ========== STEP 1: PROFILING ==========
        profiler = DataframeProfiler()
        profile = profiler.profile(df)
        issues = profiler.detect_quality_issues(df)
        profile.quality_issues = issues

        for issue in issues:
            if issue.severity == "ERROR":
                log.error(issue.message)
            else:
                log.warning(issue.message)

        log.log_decision(
            "STEP_1_PROFILING_COMPLETE",
            {
                "n_rows": profile.n_rows,
                "n_cols": profile.n_cols,
                "quality_issues_count": len(issues),
            }
        )

        # ========== STEP 2: TYPE INFERENCE ==========
        type_inferrer = ColumnTypeInferencer()
        type_assignment = type_inferrer.infer_types(df, id_cols=id_cols)

        log.log_decision(
            "STEP_2_TYPE_INFERENCE_COMPLETE",
            {
                col: ta.inferred_type.value
                for col, ta in type_assignment.items()
            }
        )

        # ========== STEP 3: RELATIONSHIP SCORING ==========
        rel_scorer = RelationshipScorer()
        score_dict = rel_scorer.score_all_pairs(df, type_assignment)

        log.log_decision(
            "STEP_3_RELATIONSHIP_SCORING_COMPLETE",
            {
                "pairs_scored": len(score_dict),
                "redundant_pairs": sum(1 for s in score_dict.values() if s.is_redundant),
            }
        )

        # ========== STEP 4: DECISION ENGINE ==========
        engine = DecisionEngine()
        plot_plan = engine.select_and_rank(
            df=df,
            type_assignment=type_assignment,
            score_dict=score_dict,
            profile=profile,
            target_cols=target_cols,
            config=config,
            log=log,
        )

        log.log_decision(
            "STEP_4_DECISION_ENGINE_COMPLETE",
            {
                "univariate_selected": plot_plan.univariate_count,
                "bivariate_selected": plot_plan.bivariate_count,
                "multivariate_selected": plot_plan.multivariate_count,
                "total_plots": len(plot_plan.items),
            }
        )

        # ========== STEP 5: PLOT GENERATION ==========
        plot_factory = PlotFactory()
        plots_succeeded = 0
        plots_failed = 0

        for item in plot_plan.items:
            try:
                item.figure = plot_factory.create_plot(item, df, config)
                plots_succeeded += 1
            except Exception as e:
                plots_failed += 1
                log.warning(f"Failed to create plot {item.plot_id}: {str(e)}")

        log.log_decision(
            "STEP_5_PLOT_GENERATION_COMPLETE",
            {
                "plots_succeeded": plots_succeeded,
                "plots_failed": plots_failed,
                "total_attempts": len(plot_plan.items),
            }
        )

        # ========== STEP 6: REPORT COMPOSITION ==========
        composer = ReportComposer()

        html_report = None
        json_summary = None

        if config.enable_export_html:
            html_report = composer.compose_html(
                plot_plan=plot_plan,
                data_profile=profile,
                type_assignment=type_assignment,
                audit_log=log.get_audit_log(),
            )

        json_summary = composer.compose_json_summary(
            plot_plan=plot_plan,
            data_profile=profile,
            type_assignment=type_assignment,
            audit_log=log.get_audit_log(),
        )

        log.log_decision("STEP_6_REPORT_COMPOSITION_COMPLETE", {})

        # ========== STEP 7: ASSEMBLE REPORT ==========
        elapsed_seconds = (datetime.now() - start_time).total_seconds()

        report = Report(
            plot_plan=plot_plan,
            data_profile=profile,
            type_assignment=type_assignment,
            html_report=html_report,
            json_summary=json_summary,
            audit_log=log.get_audit_log(),
            warnings=log.get_warnings(),
            errors=log.get_errors(),
            metadata={
                "version": "0.1.0",
                "timestamp": datetime.now().isoformat(),
                "seed": config.seed,
                "elapsed_seconds": elapsed_seconds,
                "config": config.to_dict(),
            }
        )

        log.log_decision(
            "STEP_7_REPORT_ASSEMBLY_COMPLETE",
            {
                "total_plots": len(report.plot_plan.items),
                "warnings_count": len(report.warnings),
                "errors_count": len(report.errors),
                "elapsed_seconds": elapsed_seconds,
            }
        )

        log.log_decision("PIPELINE_COMPLETE", {})

        return report

    @staticmethod
    def run_with_defaults(df: pd.DataFrame) -> Report:
        """
        Convenience method: run pipeline with default configuration.

        Purpose:
            Quick entry point for users who want sensible defaults.
            Equivalent to: VizPipeline.run(df, config=DEFAULT_CONFIG)

        Inputs:
            df (pd.DataFrame): Input data (minimum 10 rows).

        What output:
            Report: Complete report with default settings.

        How to use:
            >>> df = pd.read_csv("my_data.csv")
            >>> report = VizPipeline.run_with_defaults(df)
            >>> print(f"Generated {len(report.plot_plan.items)} visualizations")

        Raises:
            Same as VizPipeline.run()

        Example:
            >>> report = VizPipeline.run_with_defaults(df)
        """
        return VizPipeline.run(df, config=DEFAULT_CONFIG)