# **VizPipeline: Generalistic Visualization Pipeline for Pandas DataFrames**

**Implementation Blueprint & Developer Guide**

---

## **PART 1: REPOSITORY STRUCTURE & PACKAGING**

### **1.1 Directory Layout**

```
viz-pipeline/
├── README.md                              # Main documentation
├── pyproject.toml                         # PEP 518 package config
├── CHANGELOG.md                           # Version history
├── LICENSE                                # MIT or Apache 2.0
├── .gitignore
├── .github/
│   └── workflows/
│       └── tests.yml                      # CI/CD pipeline
├── src/
│   └── viz_pipeline/
│       ├── __init__.py                    # Package entry point + version
│       ├── core/
│       │   ├── __init__.py
│       │   ├── orchestrator.py            # VizPipeline.run()
│       │   ├── types.py                   # Data classes (Report, PlotPlan, etc.)
│       │   └── config.py                  # Configuration defaults + schema
│       ├── profiling/
│       │   ├── __init__.py
│       │   └── profiler.py                # DataframeProfiler class
│       ├── typing/
│       │   ├── __init__.py
│       │   ├── inferencer.py              # ColumnTypeInferrer class
│       │   └── rules.py                   # Type inference rules
│       ├── scoring/
│       │   ├── __init__.py
│       │   └── scorer.py                  # RelationshipScorer class
│       ├── decision/
│       │   ├── __init__.py
│       │   ├── engine.py                  # DecisionEngine class
│       │   └── heuristics.py              # Plot selection heuristics
│       ├── plotting/
│       │   ├── __init__.py
│       │   └── factory.py                 # PlotFactory class
│       ├── reporting/
│       │   ├── __init__.py
│       │   ├── composer.py                # ReportComposer class
│       │   └── templates.py               # HTML/Markdown templates
│       ├── export/
│       │   ├── __init__.py
│       │   └── exporter.py                # ExportEngine class
│       ├── diagnostics/
│       │   ├── __init__.py
│       │   └── logging.py                 # LogManager class
│       └── utils/
│           ├── __init__.py
│           ├── helpers.py                 # Utility functions
│           └── constants.py               # Enums, constants
├── tests/
│   ├── conftest.py                        # Pytest fixtures
│   ├── unit/
│   │   ├── test_profiler.py
│   │   ├── test_inferencer.py
│   │   ├── test_scorer.py
│   │   ├── test_engine.py
│   │   ├── test_factory.py
│   │   ├── test_composer.py
│   │   ├── test_exporter.py
│   │   └── test_config.py
│   ├── integration/
│   │   ├── test_pipeline_end_to_end.py
│   │   └── test_pipeline_with_datasets.py
│   ├── regression/
│   │   └── test_failure_modes.py
│   ├── golden/
│   │   ├── iris_plotplan.json
│   │   ├── titanic_plotplan.json
│   │   └── airbnb_berlin_plotplan.json
│   └── fixtures/
│       ├── data/
│       │   ├── iris_clean.csv
│       │   ├── titanic_clean.csv
│       │   └── airbnb_berlin_clean.csv
│       └── datasets.py                    # Dataset loaders
├── notebooks/
│   ├── 01_quickstart.ipynb                # User entry point
│   ├── 02_tool_usage.ipynb                # Individual tool examples
│   ├── 03_configuration.ipynb             # Config toggles walkthrough
│   └── 04_advanced.ipynb                  # Advanced patterns
└── docs/
    ├── api_reference.md
    ├── architecture.md
    ├── contributing.md
    └── examples.md
```

### **1.2 pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "viz-pipeline"
version = "0.1.0"
description = "Generalistic visualization pipeline for pandas DataFrames"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = [
    "data-visualization",
    "exploratory-data-analysis",
    "pandas",
    "matplotlib",
    "seaborn"
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Scientific/Engineering :: Visualization",
]

dependencies = [
    "pandas>=1.3.0",
    "numpy>=1.20.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.12.0",
    "scipy>=1.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "isort>=5.0",
    "flake8>=6.0",
    "mypy>=1.0",
]
docs = [
    "mkdocs>=1.4",
    "mkdocs-material>=9.0",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "hypothesis>=6.0",  # For property-based testing
]

[project.urls]
Homepage = "https://github.com/you/viz-pipeline"
Repository = "https://github.com/you/viz-pipeline.git"
Issues = "https://github.com/you/viz-pipeline/issues"
Documentation = "https://viz-pipeline.readthedocs.io"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = "-v --cov=src/viz_pipeline --cov-report=term-missing --cov-report=html"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "regression: marks tests as regression tests",
]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start permissive
```

---

## **PART 2: CORE DATA STRUCTURES (types.py)**

```python
# src/viz_pipeline/core/types.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import pandas as pd
from datetime import datetime


class ColumnType(Enum):
    """Enumeration of inferred column types."""
    BOOLEAN = "boolean"
    ID_LIKE = "id_like"
    DATETIME = "datetime"
    NUMERIC = "numeric"
    HIGH_CARDINALITY = "high_cardinality"
    CATEGORICAL = "categorical"
    TEXT = "text"
    UNKNOWN = "unknown"


class PlotType(Enum):
    """Enumeration of supported plot types."""
    # Univariate
    HISTOGRAM = "histogram"
    KDE = "kde"
    BOXPLOT = "boxplot"
    VIOLIN = "violin"
    BARPLOT = "barplot"
    PIE = "pie"
    
    # Bivariate
    SCATTER = "scatter"
    HEXBIN = "hexbin"
    KDE_2D = "kde_2d"
    HEATMAP = "heatmap"
    BOX_STRIP = "box_strip"
    VIOLIN_STRIP = "violin_strip"
    
    # Multivariate
    PAIRPLOT = "pairplot"
    SCATTER_3D = "scatter_3d"
    CORRELATION_HEATMAP = "correlation_heatmap"


class RelationshipType(Enum):
    """Types of relationships between columns."""
    NUMERIC_NUMERIC = "numeric_numeric"
    NUMERIC_CATEGORICAL = "numeric_categorical"
    CATEGORICAL_CATEGORICAL = "categorical_categorical"
    DATETIME_NUMERIC = "datetime_numeric"
    DATETIME_CATEGORICAL = "datetime_categorical"
    TEXT_NUMERIC = "text_numeric"
    TEXT_CATEGORICAL = "text_categorical"
    UNKNOWN = "unknown"


@dataclass
class InferredType:
    """Result of column type inference."""
    column_name: str
    inferred_type: ColumnType
    confidence: float  # 0.0 to 1.0
    rule_id: str  # Which rule fired (e.g., "R_BOOLEAN_001")
    reason: str  # Human-readable explanation
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "column_name": self.column_name,
            "inferred_type": self.inferred_type.value,
            "confidence": self.confidence,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "metadata": self.metadata,
        }


@dataclass
class DataQualityIssue:
    """A single data quality problem."""
    severity: str  # "ERROR", "WARNING", "INFO"
    column: Optional[str]  # None if dataset-level
    message: str
    metric_name: str  # e.g., "missingness_pct", "cardinality"
    metric_value: Optional[Any] = None


@dataclass
class DataProfile:
    """High-level statistics about the dataset."""
    n_rows: int
    n_cols: int
    memory_mb: float
    dtypes_distribution: Dict[str, int]  # {dtype: count}
    missing_by_col: Dict[str, float]  # {col_name: pct_missing}
    unique_by_col: Dict[str, int]  # {col_name: n_unique}
    quality_issues: List[DataQualityIssue] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "memory_mb": self.memory_mb,
            "dtypes_distribution": self.dtypes_distribution,
            "missing_by_col": self.missing_by_col,
            "unique_by_col": self.unique_by_col,
            "quality_issues": [
                {
                    "severity": issue.severity,
                    "column": issue.column,
                    "message": issue.message,
                    "metric_name": issue.metric_name,
                    "metric_value": issue.metric_value,
                }
                for issue in self.quality_issues
            ],
        }


@dataclass
class RelationshipScore:
    """Numeric score for a bivariate relationship."""
    col_a: str
    col_b: str
    relationship_type: RelationshipType
    primary_score: float  # e.g., Pearson r, Cramér's V
    secondary_score: Optional[float] = None  # e.g., p-value
    is_redundant: bool = False  # True if |score| > 0.95
    effect_size_interpretation: str = "unknown"  # "small", "medium", "large"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "col_a": self.col_a,
            "col_b": self.col_b,
            "relationship_type": self.relationship_type.value,
            "primary_score": self.primary_score,
            "secondary_score": self.secondary_score,
            "is_redundant": self.is_redundant,
            "effect_size_interpretation": self.effect_size_interpretation,
            "metadata": self.metadata,
        }


@dataclass
class PlotItem:
    """A single plot to be generated."""
    plot_id: str  # Unique identifier (e.g., "UNI_001")
    plot_type: PlotType
    column_a: str
    column_b: Optional[str] = None  # None for univariate
    column_c: Optional[str] = None  # None unless 3D
    rank: int = 0  # Priority ranking
    score: Optional[float] = None  # Relevance score from RelationshipScorer
    reason: str = ""  # Why this plot was selected
    params: Dict[str, Any] = field(default_factory=dict)  # Plot parameters
    figure = None  # Matplotlib figure object (populated after plotting)
    
    def to_dict(self) -> dict:
        """Convert to JSON (figure excluded)."""
        return {
            "plot_id": self.plot_id,
            "plot_type": self.plot_type.value,
            "column_a": self.column_a,
            "column_b": self.column_b,
            "column_c": self.column_c,
            "rank": self.rank,
            "score": self.score,
            "reason": self.reason,
            "params": self.params,
        }


@dataclass
class PlotPlan:
    """The complete plan of visualizations to generate."""
    items: List[PlotItem] = field(default_factory=list)
    univariate_count: int = 0
    bivariate_count: int = 0
    multivariate_count: int = 0
    audit_log: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "univariate_count": self.univariate_count,
            "bivariate_count": self.bivariate_count,
            "multivariate_count": self.multivariate_count,
            "items": [item.to_dict() for item in self.items],
            "audit_log": self.audit_log,
        }


@dataclass
class Report:
    """Complete output of VizPipeline.run()."""
    plot_plan: PlotPlan
    data_profile: DataProfile
    type_assignment: Dict[str, InferredType]
    html_report: Optional[str] = None
    json_summary: Optional[Dict[str, Any]] = None
    audit_log: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Version, timestamp, etc.
    
    def to_dict(self) -> dict:
        """Convert to JSON (html_report and figures excluded)."""
        return {
            "metadata": self.metadata,
            "profile": self.data_profile.to_dict(),
            "type_assignment": {
                col: ta.to_dict() for col, ta in self.type_assignment.items()
            },
            "plot_plan": self.plot_plan.to_dict(),
            "audit_log": self.audit_log,
            "warnings": self.warnings,
            "errors": self.errors,
        }
```

### **1.3 Configuration Schema (config.py)**

```python
# src/viz_pipeline/core/config.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json


@dataclass
class VizConfig:
    """Central configuration for VizPipeline."""
    
    # Thresholds
    high_card_threshold: int = 50  # Unique values > this = high-cardinality
    sample_limit: int = 10000  # Downsample if n_rows > this
    missing_allowed_pct: float = 0.2  # Warn if missing > this
    
    # Limits (guardrails)
    max_univariate_plots: int = 25
    max_bivariate_pairs: int = 15
    max_multivariate_views: int = 3
    target_top_k_features: int = 5
    
    # Plot parameters
    numeric_bins: int = 20
    text_sample_n: int = 100
    overplot_threshold_n: int = 1000
    
    # Feature toggles
    enable_target_analysis: bool = True
    enable_multivariate: bool = True
    enable_datetime_views: bool = True
    enable_text_summary: bool = True
    enable_export_html: bool = True
    enable_sampling: bool = True
    enable_audit_log: bool = True
    enable_warnings: bool = True
    
    # Reproducibility
    seed: int = 42
    
    # Export
    export_format: str = "html"  # "html", "json", "both"
    export_dir: Optional[str] = None
    
    # Advanced
    correlation_redundancy_threshold: float = 0.95
    numeric_only_correlation: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            k: v for k, v in self.__dict__.items()
        }
    
    @staticmethod
    def from_dict(config_dict: Dict[str, Any]) -> "VizConfig":
        """Create config from dictionary (for JSON loading)."""
        return VizConfig(**config_dict)
    
    def to_json(self, filepath: str) -> None:
        """Save config to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def from_json(filepath: str) -> "VizConfig":
        """Load config from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return VizConfig.from_dict(data)


# Default configuration
DEFAULT_CONFIG = VizConfig()
```

---

## **PART 3: ORCHESTRATOR (orchestrator.py)**

```python
# src/viz_pipeline/core/orchestrator.py

from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime

from .types import Report, PlotPlan, InferredType
from .config import VizConfig, DEFAULT_CONFIG
from ..profiling.profiler import DataframeProfiler
from ..typing.inferencer import ColumnTypeInferrer
from ..scoring.scorer import RelationshipScorer
from ..decision.engine import DecisionEngine
from ..plotting.factory import PlotFactory
from ..reporting.composer import ReportComposer
from ..export.exporter import ExportEngine
from ..diagnostics.logging import LogManager


class VizPipeline:
    """
    Central orchestrator for the visualization pipeline.
    
    Purpose: Execute a complete data visualization workflow from DataFrame to Report.
    
    How to use:
        >>> from viz_pipeline import VizPipeline
        >>> df = pd.read_csv("data.csv")
        >>> report = VizPipeline.run(df, target_cols=["target"])
        >>> print(report.warnings)
        >>> print(report.plot_plan.univariate_count)
    
    Attributes:
        None (stateless)
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
            Process a pandas DataFrame through the full pipeline: profiling,
            type inference, relationship scoring, plot planning, generation,
            and report composition. Returns a structured Report object.
        
        How to use:
            >>> df = pd.read_csv("my_data.csv")
            >>> report = VizPipeline.run(
            ...     df,
            ...     target_cols=["churn"],
            ...     config=VizConfig(max_bivariate_pairs=10)
            ... )
            >>> # Access results:
            >>> print(f"Selected {report.plot_plan.univariate_count} univariate plots")
            >>> with open("report.html", "w") as f:
            ...     f.write(report.html_report)
        
        Inputs:
            df (pd.DataFrame): Cleaned data with no duplicates, consistent dtypes.
                Shape can be (n, p) with n >= 10, p >= 1.
            target_cols (List[str], optional): Column names that are target variables.
                If provided, bivariate plots prioritize these. Default: None.
            id_cols (List[str], optional): Column names that are identifiers (skipped).
                Example: ["id", "customer_id"]. Default: None.
            config (VizConfig, optional): Configuration object with toggles and limits.
                If None, uses DEFAULT_CONFIG. Default: None.
        
        What output:
            Report: A dataclass containing:
                - plot_plan (PlotPlan): Ranked list of plots to generate (PlotItem objects)
                - data_profile (DataProfile): Shape, dtypes, missingness, quality signals
                - type_assignment (Dict[str, InferredType]): Inferred type + confidence for each col
                - html_report (str, optional): Full HTML report (if enable_export_html=True)
                - json_summary (dict, optional): Machine-readable summary
                - audit_log (dict): Decisions, rules fired, limits applied, sampling info
                - warnings (List[str]): Non-blocking issues (e.g., "Column X is constant")
                - errors (List[str]): Blocking issues (if any; may be non-empty but pipeline continues)
                - metadata (dict): Version, timestamp, seed used, total runtime
        
        Warnings/Failure modes:
            - IF df.shape[0] < 10: Raises ValueError (too few observations).
            - IF target_cols not in df.columns: Raises KeyError.
            - IF no plots selected (highly sparse/unusual data): Produces report with warnings.
            - IF config toggles disabled (e.g., enable_export_html=False): Report.html_report is None.
            - IF enable_sampling=True and n > sample_limit: Data is downsampled (stratified by target).
        
        Determinism/Performance:
            - Deterministic: If seed is set in config and row order is identical, output is identical.
            - Performance: ~1 min for n=100k, p=50 with all toggles enabled (depends on hardware).
        
        Raises:
            ValueError: If df has < 10 rows.
            KeyError: If target_cols or id_cols not in df.columns.
            TypeError: If df is not pd.DataFrame.
        """
        
        # Initialize
        config = config or DEFAULT_CONFIG
        log = LogManager(enabled=config.enable_audit_log, enable_warnings=config.enable_warnings)
        
        # Set seed for reproducibility
        np.random.seed(config.seed)
        
        # Validate inputs
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pd.DataFrame, got {type(df)}")
        if df.shape[0] < 10:
            raise ValueError(f"DataFrame has {df.shape[0]} rows; minimum 10 required")
        if target_cols and not all(col in df.columns for col in target_cols):
            missing = set(target_cols) - set(df.columns)
            raise KeyError(f"target_cols not in DataFrame: {missing}")
        if id_cols and not all(col in df.columns for col in id_cols):
            missing = set(id_cols) - set(df.columns)
            raise KeyError(f"id_cols not in DataFrame: {missing}")
        
        log.log_decision(
            "PIPELINE_START",
            {"n_rows": df.shape[0], "n_cols": df.shape[1], "seed": config.seed}
        )
        
        # --- STEP 1: Profiling ---
        profiler = DataframeProfiler()
        profile = profiler.profile(df)
        issues = profiler.detect_quality_issues(df)
        
        for issue in issues:
            if issue.severity == "ERROR":
                log.error(issue.message)
            else:
                log.warning(issue.message)
        
        log.log_decision("PROFILING_COMPLETE", {"quality_issues_count": len(issues)})
        
        # --- STEP 2: Type Inference ---
        type_inferrer = ColumnTypeInferrer()
        type_assignment = type_inferrer.infer_types(df, id_cols=id_cols or [])
        
        log.log_decision(
            "TYPE_INFERENCE_COMPLETE",
            {
                col: ta.inferred_type.value
                for col, ta in type_assignment.items()
            }
        )
        
        # --- STEP 3: Relationship Scoring ---
        rel_scorer = RelationshipScorer()
        score_dict = rel_scorer.score_all_pairs(df, type_assignment)
        
        log.log_decision(
            "RELATIONSHIP_SCORING_COMPLETE",
            {
                "pairs_scored": len(score_dict),
                "redundant_pairs": sum(1 for s in score_dict.values() if s.is_redundant)
            }
        )
        
        # --- STEP 4: Decision Engine ---
        engine = DecisionEngine()
        plot_plan = engine.select_and_rank(
            df=df,
            type_assignment=type_assignment,
            score_dict=score_dict,
            profile=profile,
            target_cols=target_cols or [],
            config=config,
            log=log,
        )
        
        log.log_decision(
            "DECISION_ENGINE_COMPLETE",
            {
                "univariate_selected": plot_plan.univariate_count,
                "bivariate_selected": plot_plan.bivariate_count,
                "multivariate_selected": plot_plan.multivariate_count,
            }
        )
        
        # --- STEP 5: Plot Generation ---
        plot_factory = PlotFactory()
        for item in plot_plan.items:
            try:
                item.figure = plot_factory.create_plot(item, df, config)
            except Exception as e:
                log.warning(f"Failed to create plot {item.plot_id}: {str(e)}")
        
        log.log_decision("PLOT_GENERATION_COMPLETE", {"plots_generated": len(plot_plan.items)})
        
        # --- STEP 6: Report Composition ---
        composer = ReportComposer()
        
        report_sections = []
        if config.enable_export_html:
            html = composer.compose_html(
                plot_plan=plot_plan,
                data_profile=profile,
                type_assignment=type_assignment,
                audit_log=log.get_audit_log(),
            )
            report_sections.append(("html", html))
        
        json_summary = composer.compose_json_summary(
            plot_plan=plot_plan,
            data_profile=profile,
            type_assignment=type_assignment,
            audit_log=log.get_audit_log(),
        )
        report_sections.append(("json", json_summary))
        
        log.log_decision("REPORT_COMPOSITION_COMPLETE", {})
        
        # --- STEP 7: Assemble Report ---
        report = Report(
            plot_plan=plot_plan,
            data_profile=profile,
            type_assignment=type_assignment,
            html_report=dict(report_sections).get("html"),
            json_summary=dict(report_sections).get("json"),
            audit_log=log.get_audit_log(),
            warnings=log.get_warnings(),
            errors=log.get_errors(),
            metadata={
                "version": "0.1.0",
                "timestamp": datetime.now().isoformat(),
                "seed": config.seed,
                "config": config.to_dict(),
            }
        )
        
        log.log_decision("PIPELINE_COMPLETE", {})
        
        return report
    
    @staticmethod
    def run_with_defaults(df: pd.DataFrame) -> Report:
        """
        Convenience method: run pipeline with default configuration.
        
        Inputs:
            df (pd.DataFrame): Input data.
        
        What output:
            Report: Complete report with default settings.
        
        How to use:
            >>> report = VizPipeline.run_with_defaults(df)
        """
        return VizPipeline.run(df, config=DEFAULT_CONFIG)
```

---

## **PART 4: EXAMPLE IMPLEMENTATION STUBS**

### **4.1 Profiler (profiling/profiler.py)**

```python
# src/viz_pipeline/profiling/profiler.py

from typing import List
import pandas as pd
import numpy as np
from ..core.types import DataProfile, DataQualityIssue


class DataframeProfiler:
    """
    Purpose: Quick data quality statistics.
    
    How to use:
        >>> profiler = DataframeProfiler()
        >>> profile = profiler.profile(df)
        >>> print(f"Dataset: {profile.n_rows} rows, {profile.memory_mb:.1f} MB")
    """
    
    def profile(self, df: pd.DataFrame) -> DataProfile:
        """
        Inputs: df (pd.DataFrame)
        
        What output: DataProfile with shape, dtypes, missing %, unique counts.
        """
        return DataProfile(
            n_rows=df.shape[0],
            n_cols=df.shape[1],
            memory_mb=df.memory_usage(deep=True).sum() / (1024 ** 2),
            dtypes_distribution=df.dtypes.value_counts().to_dict(),
            missing_by_col={col: df[col].isna().mean() for col in df.columns},
            unique_by_col={col: df[col].nunique() for col in df.columns},
        )
    
    def detect_quality_issues(self, df: pd.DataFrame) -> List[DataQualityIssue]:
        """
        Inputs: df (pd.DataFrame)
        
        What output: List of DataQualityIssue objects (severity: ERROR/WARNING/INFO).
        """
        issues = []
        
        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            issues.append(DataQualityIssue(
                severity="WARNING",
                column=None,
                message=f"Dataset has {dup_count} duplicate rows.",
                metric_name="duplicate_rows",
                metric_value=dup_count,
            ))
        
        # Check for constant columns
        for col in df.columns:
            if df[col].nunique() <= 1:
                issues.append(DataQualityIssue(
                    severity="WARNING",
                    column=col,
                    message=f"Column '{col}' is constant (only {df[col].nunique()} unique value).",
                    metric_name="constant_column",
                    metric_value=1,
                ))
        
        # Check for high missingness
        for col in df.columns:
            missing_pct = df[col].isna().mean()
            if missing_pct > 0.5:
                issues.append(DataQualityIssue(
                    severity="WARNING",
                    column=col,
                    message=f"Column '{col}' has {missing_pct*100:.1f}% missing values.",
                    metric_name="high_missingness",
                    metric_value=missing_pct,
                ))
        
        return issues
```

### **4.2 Type Inferencer (typing/inferencer.py)**

```python
# src/viz_pipeline/typing/inferencer.py

from typing import Dict, List
import pandas as pd
import numpy as np
from ..core.types import ColumnType, InferredType


class ColumnTypeInferrer:
    """
    Purpose: Infer column types robustly with audit trail.
    
    How to use:
        >>> inferrer = ColumnTypeInferrer()
        >>> ta = inferrer.infer_types(df)
        >>> for col, inferred in ta.items():
        ...     print(f"{col}: {inferred.inferred_type.value} (confidence={inferred.confidence:.2f})")
    """
    
    def infer_types(
        self,
        df: pd.DataFrame,
        id_cols: List[str] = None,
    ) -> Dict[str, InferredType]:
        """
        Inputs:
            df (pd.DataFrame): Input DataFrame.
            id_cols (List[str], optional): Columns to mark as ID_LIKE.
        
        What output:
            Dict[str, InferredType]: Mapping of column name → InferredType object.
        
        How it works:
            Applies type inference rules in order:
            1. Boolean (True/False/0/1)
            2. ID-like (in id_cols or name matches /id|ID/)
            3. Datetime (datetime64 or parseable)
            4. Numeric (int/float or coercible)
            5. High-cardinality (>threshold unique)
            6. Categorical (<=threshold unique)
            7. Text (long strings)
            8. Unknown (fallback)
        """
        id_cols = id_cols or []
        type_assignment = {}
        
        for col in df.columns:
            inferred = self._infer_single_column(df[col], col, id_cols)
            type_assignment[col] = inferred
        
        return type_assignment
    
    def _infer_single_column(
        self,
        series: pd.Series,
        col_name: str,
        id_cols: List[str],
    ) -> InferredType:
        """Infer type for a single column."""
        
        # Rule 1: Boolean
        if set(series.dropna().unique()) <= {True, False, 0, 1}:
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.BOOLEAN,
                confidence=0.99,
                rule_id="R_BOOLEAN_001",
                reason="Unique values in {True, False, 0, 1}",
            )
        
        # Rule 2: ID-like
        if col_name in id_cols or any(x in col_name.lower() for x in ["id", "index"]):
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.ID_LIKE,
                confidence=0.95,
                rule_id="R_ID_LIKE_001",
                reason=f"Column name '{col_name}' matches ID pattern.",
            )
        
        # Rule 3: Datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.DATETIME,
                confidence=0.99,
                rule_id="R_DATETIME_001",
                reason="dtype is datetime64.",
            )
        
        # Try to parse as datetime if dtype is object
        if series.dtype == "object":
            try:
                pd.to_datetime(series, errors='coerce')
                if series.dropna().shape[0] > 0:
                    parsed = pd.to_datetime(series, errors='coerce')
                    if parsed.notna().mean() > 0.8:  # >80% successful parse
                        return InferredType(
                            column_name=col_name,
                            inferred_type=ColumnType.DATETIME,
                            confidence=0.8,
                            rule_id="R_DATETIME_002",
                            reason="Successfully parsed 80%+ as datetime.",
                        )
            except:
                pass
        
        # Rule 4: Numeric
        if pd.api.types.is_numeric_dtype(series):
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.NUMERIC,
                confidence=0.99,
                rule_id="R_NUMERIC_001",
                reason="dtype is numeric (int/float).",
            )
        
        # Rule 5 & 6: High-cardinality vs Categorical
        n_unique = series.nunique()
        if n_unique > 50:  # Threshold
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.HIGH_CARDINALITY,
                confidence=0.9,
                rule_id="R_HIGHCARD_001",
                reason=f"{n_unique} unique values > 50 threshold.",
            )
        else:
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.CATEGORICAL,
                confidence=0.9,
                rule_id="R_CATEGORICAL_001",
                reason=f"{n_unique} unique values <= 50 threshold.",
            )
    
    def validate_type(
        self,
        series: pd.Series,
        inferred_type: InferredType,
    ) -> bool:
        """Validate inferred type. Return False if mismatch detected."""
        # Simple checks; can be extended
        if inferred_type.inferred_type == ColumnType.BOOLEAN:
            return set(series.dropna().unique()) <= {True, False, 0, 1}
        elif inferred_type.inferred_type == ColumnType.NUMERIC:
            return pd.api.types.is_numeric_dtype(series)
        return True
```

---

## **PART 5: DECISION ENGINE STUB (decision/engine.py)**

```python
# src/viz_pipeline/decision/engine.py

from typing import Dict, List, Optional
import pandas as pd
from ..core.types import (
    PlotPlan, PlotItem, PlotType, InferredType, ColumnType,
    RelationshipScore
)
from ..core.config import VizConfig
from ..diagnostics.logging import LogManager


class DecisionEngine:
    """
    Purpose: Central rule block for plot selection and prioritization.
    
    How to use:
        >>> engine = DecisionEngine()
        >>> plan = engine.select_and_rank(
        ...     df, type_assignment, score_dict, profile, target_cols, config, log
        ... )
        >>> print(f"Selected {len(plan.items)} plots")
    """
    
    def select_and_rank(
        self,
        df: pd.DataFrame,
        type_assignment: Dict[str, InferredType],
        score_dict: Dict[tuple, RelationshipScore],
        profile,
        target_cols: List[str],
        config: VizConfig,
        log: LogManager,
    ) -> PlotPlan:
        """
        Inputs:
            df, type_assignment, score_dict, profile: From prior steps.
            target_cols: Column names for target-aware analysis.
            config: VizConfig with limits and toggles.
            log: LogManager for audit trail.
        
        What output:
            PlotPlan with ranked, filtered PlotItem objects.
        """
        plan = PlotPlan()
        plot_id_counter = 0
        
        # --- Univariate plots ---
        univariate_items = self._select_univariate(
            type_assignment, df, config, log
        )
        for item in univariate_items[:config.max_univariate_plots]:
            item.plot_id = f"UNI_{plot_id_counter:03d}"
            item.rank = plot_id_counter
            plan.items.append(item)
            plot_id_counter += 1
        plan.univariate_count = len(univariate_items)
        
        # --- Bivariate plots ---
        if config.enable_target_analysis and target_cols:
            bivariate_items = self._select_bivariate_target_aware(
                type_assignment, score_dict, target_cols, config, log
            )
        else:
            bivariate_items = self._select_bivariate_generic(
                type_assignment, score_dict, config, log
            )
        
        for item in bivariate_items[:config.max_bivariate_pairs]:
            item.plot_id = f"BIV_{plot_id_counter:03d}"
            item.rank = plot_id_counter
            plan.items.append(item)
            plot_id_counter += 1
        plan.bivariate_count = len(bivariate_items)
        
        # --- Multivariate plots ---
        if config.enable_multivariate:
            multivar_items = self._select_multivariate(
                bivariate_items, target_cols, config, log
            )
            for item in multivar_items[:config.max_multivariate_views]:
                item.plot_id = f"MUL_{plot_id_counter:03d}"
                item.rank = plot_id_counter
                plan.items.append(item)
                plot_id_counter += 1
            plan.multivariate_count = len(multivar_items)
        
        plan.audit_log = {
            "univariate_selected": plan.univariate_count,
            "bivariate_selected": plan.bivariate_count,
            "multivariate_selected": plan.multivariate_count,
            "total_plots": len(plan.items),
        }
        
        return plan
    
    def _select_univariate(
        self,
        type_assignment: Dict[str, InferredType],
        df: pd.DataFrame,
        config: VizConfig,
        log: LogManager,
    ) -> List[PlotItem]:
        """Select univariate plots."""
        items = []
        
        for col_name, inferred_type in type_assignment.items():
            # Skip ID-like, unknown, datetime (for now)
            if inferred_type.inferred_type in [
                ColumnType.ID_LIKE,
                ColumnType.UNKNOWN,
            ]:
                continue
            
            # Check for constant columns
            if df[col_name].nunique() <= 1:
                log.warning(f"Skipping constant column: {col_name}")
                continue
            
            # Select plot type based on inferred type
            if inferred_type.inferred_type == ColumnType.BOOLEAN:
                plot_type = PlotType.PIE
            elif inferred_type.inferred_type == ColumnType.NUMERIC:
                plot_type = PlotType.HISTOGRAM
            elif inferred_type.inferred_type == ColumnType.CATEGORICAL:
                if df[col_name].nunique() <= 5:
                    plot_type = PlotType.PIE
                else:
                    plot_type = PlotType.BARPLOT
            elif inferred_type.inferred_type == ColumnType.HIGH_CARDINALITY:
                plot_type = PlotType.BARPLOT
            else:
                continue
            
            item = PlotItem(
                plot_id="",  # Set later
                plot_type=plot_type,
                column_a=col_name,
                reason=f"Univariate: {inferred_type.inferred_type.value}",
                params={"bins": config.numeric_bins},
            )
            items.append(item)
        
        return items
    
    def _select_bivariate_target_aware(
        self,
        type_assignment: Dict[str, InferredType],
        score_dict: Dict[tuple, RelationshipScore],
        target_cols: List[str],
        config: VizConfig,
        log: LogManager,
    ) -> List[PlotItem]:
        """Select bivariate plots, prioritizing target relationships."""
        items = []
        
        # Get scores for (feature, target) pairs and rank by score
        target_pairs = [
            (score, col_a, col_b)
            for (col_a, col_b), score in score_dict.items()
            if col_b in target_cols and col_a not in target_cols
        ]
        target_pairs.sort(key=lambda x: abs(x[0].primary_score), reverse=True)
        
        # Take top-K target relationships
        for score, col_a, col_b in target_pairs[:config.target_top_k_features]:
            plot_type = self._select_bivariate_plot_type(
                type_assignment[col_a],
                type_assignment[col_b],
            )
            
            item = PlotItem(
                plot_id="",
                plot_type=plot_type,
                column_a=col_a,
                column_b=col_b,
                score=score.primary_score,
                reason=f"Target-aware: score={score.primary_score:.2f}",
            )
            items.append(item)
        
        return items
    
    def _select_bivariate_generic(
        self,
        type_assignment: Dict[str, InferredType],
        score_dict: Dict[tuple, RelationshipScore],
        config: VizConfig,
        log: LogManager,
    ) -> List[PlotItem]:
        """Select bivariate plots, ranked by relationship strength."""
        items = []
        
        # Filter out redundant pairs
        non_redundant = [
            (score, col_a, col_b)
            for (col_a, col_b), score in score_dict.items()
            if not score.is_redundant
        ]
        
        # Rank by score
        non_redundant.sort(key=lambda x: abs(x[0].primary_score), reverse=True)
        
        for score, col_a, col_b in non_redundant:
            plot_type = self._select_bivariate_plot_type(
                type_assignment[col_a],
                type_assignment[col_b],
            )
            
            item = PlotItem(
                plot_id="",
                plot_type=plot_type,
                column_a=col_a,
                column_b=col_b,
                score=score.primary_score,
                reason=f"Bivariate: score={score.primary_score:.2f}",
            )
            items.append(item)
        
        return items
    
    def _select_bivariate_plot_type(
        self,
        type_a: InferredType,
        type_b: InferredType,
    ) -> PlotType:
        """Select appropriate bivariate plot type based on column types."""
        # Simplified logic; can be extended
        if type_a.inferred_type == ColumnType.NUMERIC and \
           type_b.inferred_type == ColumnType.NUMERIC:
            return PlotType.SCATTER
        elif type_a.inferred_type in [ColumnType.NUMERIC, ColumnType.HIGH_CARDINALITY] and \
             type_b.inferred_type in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]:
            return PlotType.BOX_STRIP
        else:
            return PlotType.HEATMAP
    
    def _select_multivariate(
        self,
        bivariate_items: List[PlotItem],
        target_cols: List[str],
        config: VizConfig,
        log: LogManager,
    ) -> List[PlotItem]:
        """Select multivariate plots (optional)."""
        # Simple: create correlation heatmap if >= 3 features
        if len(bivariate_items) >= 3:
            return [PlotItem(
                plot_id="",
                plot_type=PlotType.CORRELATION_HEATMAP,
                column_a="all_numeric",
                reason="Multivariate: Correlation heatmap for top features",
            )]
        return []
```

---

## **PART 6: REPORT COMPOSER STUB (reporting/composer.py)**

```python
# src/viz_pipeline/reporting/composer.py

from typing import Dict, Any, Optional
from ..core.types import PlotPlan, DataProfile, InferredType


class ReportComposer:
    """
    Purpose: Assemble Report HTML, JSON, and Markdown sections.
    
    How to use:
        >>> composer = ReportComposer()
        >>> html = composer.compose_html(plot_plan, profile, type_assignment, audit)
        >>> with open("report.html", "w") as f:
        ...     f.write(html)
    """
    
    def compose_html(
        self,
        plot_plan: PlotPlan,
        data_profile: DataProfile,
        type_assignment: Dict[str, InferredType],
        audit_log: Dict[str, Any],
    ) -> str:
        """
        Inputs:
            plot_plan, data_profile, type_assignment, audit_log: From pipeline.
        
        What output:
            str: Complete HTML document as string.
        
        How to use:
            >>> html = composer.compose_html(...)
            >>> with open("output.html", "w") as f:
            ...     f.write(html)
        """
        sections = []
        
        # Title
        sections.append("<html><head><title>VizPipeline Report</title></head><body>")
        sections.append("<h1>Data Visualization Report</h1>")
        
        # Overview
        sections.append(self._section_overview(data_profile))
        
        # Type Inference
        sections.append(self._section_types(type_assignment))
        
        # PlotPlan
        sections.append(self._section_plots(plot_plan))
        
        # Audit
        sections.append(self._section_audit(audit_log))
        
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
        Inputs: plot_plan, data_profile, type_assignment, audit_log
        
        What output:
            dict: Machine-readable summary (JSON-serializable).
        """
        return {
            "profile": data_profile.to_dict(),
            "type_assignment": {
                col: ta.to_dict() for col, ta in type_assignment.items()
            },
            "plot_plan": plot_plan.to_dict(),
            "audit_log": audit_log,
        }
    
    def _section_overview(self, profile: DataProfile) -> str:
        """Generate overview section."""
        return f"""
        <h2>Dataset Overview</h2>
        <table border="1">
        <tr><td>Rows</td><td>{profile.n_rows}</td></tr>
        <tr><td>Columns</td><td>{profile.n_cols}</td></tr>
        <tr><td>Memory (MB)</td><td>{profile.memory_mb:.1f}</td></tr>
        </table>
        """
    
    def _section_types(self, type_assignment: Dict[str, InferredType]) -> str:
        """Generate type inference section."""
        rows = []
        for col, ta in type_assignment.items():
            rows.append(f"<tr><td>{col}</td><td>{ta.inferred_type.value}</td><td>{ta.confidence:.2f}</td></tr>")
        return f"""
        <h2>Column Type Inference</h2>
        <table border="1">
        <tr><th>Column</th><th>Inferred Type</th><th>Confidence</th></tr>
        {''.join(rows)}
        </table>
        """
    
    def _section_plots(self, plan: PlotPlan) -> str:
        """Generate plot plan section."""
        return f"""
        <h2>Selected Visualizations</h2>
        <p>Total plots: {len(plan.items)}</p>
        <p>Univariate: {plan.univariate_count}</p>
        <p>Bivariate: {plan.bivariate_count}</p>
        <p>Multivariate: {plan.multivariate_count}</p>
        """
    
    def _section_audit(self, audit_log: Dict[str, Any]) -> str:
        """Generate audit log section."""
        return f"""
        <h2>Audit Log</h2>
        <pre>{str(audit_log)}</pre>
        """
```

---

## **PART 7: LOGGING (diagnostics/logging.py)**

```python
# src/viz_pipeline/diagnostics/logging.py

from typing import Dict, List, Any
from collections import defaultdict


class LogManager:
    """
    Purpose: Central logging for warnings, errors, and audit decisions.
    
    How to use:
        >>> log = LogManager()
        >>> log.warning("Potential issue detected")
        >>> log.log_decision("RULE_X_FIRED", {"detail": "value"})
        >>> audit = log.get_audit_log()
    """
    
    def __init__(self, enabled: bool = True, enable_warnings: bool = True):
        self.enabled = enabled
        self.enable_warnings = enable_warnings
        self._warnings: List[str] = []
        self._errors: List[str] = []
        self._decisions: Dict[str, Any] = defaultdict(list)
    
    def warning(self, message: str) -> None:
        """Log a warning (non-blocking)."""
        if self.enable_warnings:
            self._warnings.append(message)
    
    def error(self, message: str) -> None:
        """Log an error (potentially blocking)."""
        self._errors.append(message)
    
    def log_decision(self, rule_id: str, details: Dict[str, Any]) -> None:
        """Log a decision/rule firing."""
        if self.enabled:
            self._decisions[rule_id].append(details)
    
    def get_warnings(self) -> List[str]:
        return self._warnings
    
    def get_errors(self) -> List[str]:
        return self._errors
    
    def get_audit_log(self) -> Dict[str, Any]:
        return dict(self._decisions)
```

---

## **PART 8: PACKAGE ENTRY POINT (__init__.py)**

```python
# src/viz_pipeline/__init__.py

__version__ = "0.1.0"
__author__ = "Your Name"

from .core.orchestrator import VizPipeline
from .core.config import VizConfig, DEFAULT_CONFIG
from .core.types import (
    ColumnType,
    PlotType,
    Report,
    PlotPlan,
    DataProfile,
)

__all__ = [
    "VizPipeline",
    "VizConfig",
    "DEFAULT_CONFIG",
    "ColumnType",
    "PlotType",
    "Report",
    "PlotPlan",
    "DataProfile",
]
```

---

## **PART 9: MINIMAL TEST EXAMPLE (tests/unit/test_orchestrator.py)**

```python
# tests/unit/test_orchestrator.py

import pytest
import pandas as pd
import numpy as np
from viz_pipeline import VizPipeline, VizConfig, DEFAULT_CONFIG


class TestVizPipelineBasic:
    """Test basic orchestrator functionality."""
    
    @pytest.fixture
    def df_iris(self):
        """Load iris dataset."""
        from sklearn.datasets import load_iris
        iris = load_iris()
        return pd.DataFrame(
            iris.data,
            columns=iris.feature_names
        )
    
    def test_run_with_defaults(self, df_iris):
        """Test basic pipeline execution."""
        report = VizPipeline.run_with_defaults(df_iris)
        
        assert report is not None
        assert report.plot_plan is not None
        assert len(report.plot_plan.items) > 0
        assert report.data_profile.n_rows == 150
        assert report.data_profile.n_cols == 4
    
    def test_run_with_config(self, df_iris):
        """Test with custom config."""
        config = VizConfig(
            max_univariate_plots=5,
            max_bivariate_pairs=3,
        )
        report = VizPipeline.run(df_iris, config=config)
        
        assert report.plot_plan.univariate_count <= 5
        assert report.plot_plan.bivariate_count <= 3
    
    def test_run_with_target_cols(self, df_iris):
        """Test target-aware analysis."""
        df = df_iris.copy()
        df['target'] = np.random.choice([0, 1], size=150)
        
        report = VizPipeline.run(
            df,
            target_cols=['target'],
            config=VizConfig(enable_target_analysis=True)
        )
        
        assert len(report.warnings) >= 0  # May have warnings, but shouldn't error
    
    def test_error_on_small_df(self):
        """Test error on small dataset."""
        df = pd.DataFrame({'a': [1, 2, 3]})  # Only 3 rows
        
        with pytest.raises(ValueError):
            VizPipeline.run(df)
    
    def test_error_on_invalid_target_col(self, df_iris):
        """Test error on invalid target column."""
        with pytest.raises(KeyError):
            VizPipeline.run(df_iris, target_cols=['nonexistent'])
    
    def test_reproducibility(self, df_iris):
        """Test determinism with seed."""
        config = VizConfig(seed=42)
        
        report1 = VizPipeline.run(df_iris, config=config)
        report2 = VizPipeline.run(df_iris, config=config)
        
        # Check that plot plans are identical
        assert len(report1.plot_plan.items) == len(report2.plot_plan.items)
        for item1, item2 in zip(report1.plot_plan.items, report2.plot_plan.items):
            assert item1.column_a == item2.column_a
            assert item1.plot_type == item2.plot_type
```

---

## **PART 10: GOLDEN FILE TEST EXAMPLE (tests/integration/test_golden.py)**

```python
# tests/integration/test_golden.py

import pytest
import json
import pandas as pd
from pathlib import Path
from viz_pipeline import VizPipeline, DEFAULT_CONFIG


class TestGoldenFiles:
    """Test against golden file baselines for known datasets."""
    
    GOLDEN_DIR = Path(__file__).parent.parent / "golden"
    
    @pytest.fixture
    def iris_data(self):
        from sklearn.datasets import load_iris
        iris = load_iris()
        return pd.DataFrame(
            iris.data,
            columns=iris.feature_names
        )
    
    def test_iris_plotplan_golden(self, iris_data):
        """Check iris plotplan matches golden file."""
        report = VizPipeline.run(iris_data, config=DEFAULT_CONFIG)
        
        # Load golden file
        golden_path = self.GOLDEN_DIR / "iris_plotplan.json"
        with open(golden_path) as f:
            golden = json.load(f)
        
        # Compare key metrics
        assert report.plot_plan.univariate_count == golden["univariate_count"]
        assert report.plot_plan.bivariate_count == golden["bivariate_count"]
        
        # Compare column types
        assert set(report.type_assignment.keys()) == set(golden["columns_typed"])
```

---

## **PART 11: DOCSTRING TEMPLATE**

```python
# Template for all public methods

def my_function(param1: Type1, param2: Type2) -> ReturnType:
    """
    Purpose:
        One-sentence summary of what this function does.
    
    How to use:
        Describe the typical usage pattern in 2-3 sentences.
        Example: "Call this after profiling to infer column types."
    
    Inputs:
        param1 (Type1): Description. Constraint: [constraints].
        param2 (Type2): Description. Default: [default].
    
    What output:
        Returns (ReturnType): Describes the return value structure.
        - Field1: Meaning of field1.
        - Field2: Meaning of field2.
    
    Warnings/Failure modes:
        - IF [condition]: [behavior]. Solution: [fix].
        - IF [condition]: [behavior]. Solution: [fix].
    
    Determinism/Performance:
        - Deterministic: Yes/No. (If Yes: conditions for reproducibility.)
        - Typical runtime: [estimate for typical data size].
    
    Raises:
        ValueError: IF [condition].
        TypeError: IF [condition].
    
    Example:
        >>> result = my_function(param1_value, param2_value)
        >>> print(result)
    """
    # Implementation
    pass
```

---

## **PART 12: README.md STRUCTURE**

```markdown
# VizPipeline: Generalistic Visualization for Pandas DataFrames

## What it is / What it is not

**What it is:**
- A modular Python package for exploratory data visualization
- Automated column-type detection and visualization selection
- Guardrails against overplotting, high-cardinality bias, multicollinearity spam
- Reproducible pipeline with audit logs and configuration toggles

**What it is NOT:**
- A domain-specific analytics tool (no sales/marketing bias)
- An "auto-insight" system making causal claims
- A plot-fine-tuning service (cosmetic parameters are user's responsibility)
- A replacement for hypothesis-driven visualization

## Installation

### Local Development (Editable)

```bash
git clone https://github.com/you/viz-pipeline.git
cd viz-pipeline
pip install -e ".[dev]"
```

### From PyPI (when released)

```bash
pip install viz-pipeline
```

## Quickstart (Pipeline Mode)

```python
import pandas as pd
from viz_pipeline import VizPipeline

# Load data
df = pd.read_csv("my_data.csv")

# Run pipeline
report = VizPipeline.run(df, target_cols=["churn"])

# Access results
print(f"Selected {report.plot_plan.univariate_count} univariate plots")
print(f"Warnings: {report.warnings}")

# Export HTML
with open("report.html", "w") as f:
    f.write(report.html_report)
```

## Tool Usage (Individual Components)

### Profiler

```python
from viz_pipeline.profiling import DataframeProfiler

profiler = DataframeProfiler()
profile = profiler.profile(df)
print(f"Dataset: {profile.n_rows} rows, {profile.memory_mb:.1f} MB")
```

### Type Inferencer

```python
from viz_pipeline.typing import ColumnTypeInferrer

inferrer = ColumnTypeInferrer()
types = inferrer.infer_types(df, id_cols=["id"])
for col, inferred in types.items():
    print(f"{col}: {inferred.inferred_type.value}")
```

## Configuration Guide

### Feature Toggles

```python
from viz_pipeline import VizConfig, VizPipeline

config = VizConfig(
    enable_target_analysis=True,        # Prioritize target relationships
    enable_multivariate=True,           # Include 3D/correlation plots
    enable_datetime_views=True,         # Visualize datetime columns
    enable_export_html=True,            # Generate HTML report
    max_univariate_plots=20,            # Limit univariate plots
    max_bivariate_pairs=10,             # Limit bivariate pairs
)

report = VizPipeline.run(df, config=config)
```

### Limits & Thresholds

- `high_card_threshold`: Unique values > this = high-cardinality (default: 50)
- `sample_limit`: Downsample if n_rows > this (default: 10000)
- `overplot_threshold_n`: Use Hexbin if n > this for scatter (default: 1000)

## Output Guide

### HTML Report

```python
with open("output.html", "w") as f:
    f.write(report.html_report)
```

Includes chapters:
- Dataset Overview
- Column Type Inference
- Visualization Plan
- Selected Plots
- Audit Log & Warnings

### JSON Summary

```python
import json

with open("summary.json", "w") as f:
    json.dump(report.json_summary, f, indent=2)
```

Machine-readable schema:
- `profile`: Shape, dtypes, missingness
- `type_assignment`: Inferred types with confidence
- `plot_plan`: Ranked plots
- `audit_log`: Rules fired, limits applied

### Audit Log

```python
print(report.audit_log)
```

Transparently logs:
- Which rules fired during type inference
- Which plots were selected and why
- Sampling decisions
- Quality issues detected

## Failure Modes & Guardrails

### High-Cardinality Handling

If a categorical column has >50 unique values:
- Univariate: Show top-20 categories
- Bivariate: Aggregate or use heatmap instead of bar

### Overplotting

If n > 1000 in a scatter plot:
- Automatically switch to hexbin or KDE
- Apply alpha transparency
- Log decision in audit

### ID-like Columns

Columns named `*id*` or in `id_cols` are:
- Excluded from type-specific plots
- Never used as bivariate feature

### Multicollinearity

Pairs with Spearman correlation >0.95:
- Deduplicated (only one plot)
- Marked as "redundant" in audit

### Sampling Bias

If `enable_sampling=True`:
- Uses stratified sampling by target (if target exists)
- Preserves target distribution in sample
- Logs sampling info in audit

## Testing & Contributing

### Run Tests

```bash
pytest tests/ -v --cov=src/viz_pipeline
```

### Test Structure

- `tests/unit/`: Individual component tests
- `tests/integration/`: End-to-end pipeline tests
- `tests/regression/`: Known failure mode tests
- `tests/golden/`: Baseline comparison tests

### Contributing

1. Fork repo
2. Create feature branch (`git checkout -b feature/my-feature`)
3. Write tests (aim for >90% coverage)
4. Submit PR with description

## Versioning & Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

Current version: 0.1.0 (Alpha)

---

**Questions?** Open an issue on GitHub or check the full API docs.
```

---

## **PART 13: MEILENSTEINE (CHECKLIST)**

```markdown
# Implementation Milestones

- [ ] **M1: Repo Skeleton & Packaging**
  - [ ] Create directory structure
  - [ ] Write pyproject.toml
  - [ ] Set up .gitignore
  - [ ] Initialize VizPipeline class with run() signature
  
- [ ] **M2: Data Structures & Config**
  - [ ] Implement core/types.py (all dataclasses)
  - [ ] Implement core/config.py (VizConfig)
  - [ ] Write Docstrings for types
  
- [ ] **M3: Profiling & Type Inference**
  - [ ] Implement DataframeProfiler
  - [ ] Implement ColumnTypeInferrer + rules
  - [ ] Unit tests for profiler & inferencer
  - [ ] Docstrings (How to use + Inputs + Outputs)
  
- [ ] **M4: Relationship Scoring**
  - [ ] Implement RelationshipScorer
  - [ ] Implement numeric/categorical/mixed scoring
  - [ ] Handle redundancy detection
  - [ ] Unit tests
  
- [ ] **M5: Decision Engine & Plot Planning**
  - [ ] Implement DecisionEngine.select_and_rank()
  - [ ] Implement univariate selection heuristics
  - [ ] Implement bivariate selection (generic + target-aware)
  - [ ] Implement multivariate selection
  - [ ] Unit tests
  
- [ ] **M6: Plot Factory**
  - [ ] Implement PlotFactory.create_plot()
  - [ ] Basic matplotlib/seaborn wrappers
  - [ ] Handle overplotting cases
  - [ ] Unit tests
  
- [ ] **M7: Report Composition & Export**
  - [ ] Implement ReportComposer.compose_html()
  - [ ] Implement ReportComposer.compose_json_summary()
  - [ ] HTML template with chapters
  - [ ] Unit tests
  
- [ ] **M8: Diagnostics & Logging**
  - [ ] Implement LogManager
  - [ ] Integrate logging throughout pipeline
  - [ ] Test audit trail generation
  
- [ ] **M9: Complete Orchestrator**
  - [ ] Wire all components into VizPipeline.run()
  - [ ] Integration test (end-to-end)
  - [ ] Test with real dataset (Iris, Titanic, etc.)
  
- [ ] **M10: Documentation per Method**
  - [ ] Write docstrings for all public methods (Purpose/How/Inputs/Outputs/Warnings)
  - [ ] Docstring examples
  
- [ ] **M11: README & User Guide**
  - [ ] Write README.md (all required sections)
  - [ ] Write configuration guide
  - [ ] Write troubleshooting guide
  
- [ ] **M12: Comprehensive Test Suite**
  - [ ] Unit tests (profiler, inferencer, scorer, engine, factory, composer)
  - [ ] Integration tests (end-to-end)
  - [ ] Golden file tests (3+ datasets)
  - [ ] Regression tests (failure modes)
  - [ ] Achieve >90% coverage
  
- [ ] **M13: Example Notebooks**
  - [ ] 01_quickstart.ipynb (basic pipeline)
  - [ ] 02_tool_usage.ipynb (individual tools)
  - [ ] 03_configuration.ipynb (toggles walkthrough)
  - [ ] 04_advanced.ipynb (custom rules, etc.)
  
- [ ] **M14: Polish & Release**
  - [ ] Code review & refactoring
  - [ ] Static analysis (flake8, mypy)
  - [ ] Final integration test
  - [ ] Draft CHANGELOG.md
  - [ ] Tag v0.1.0

```

---

**This blueprint provides a complete, modular architecture for the VizPipeline package. Each part is independent and can be developed in parallel. The design emphasizes:**

1. **Modularity**: Each tool (Profiler, Inferencer, Scorer, Engine, Factory, Composer) has a single responsibility.
2. **Transparency**: Audit logs document every decision.
3. **Configurability**: Feature toggles and limits are centralized.
4. **Testability**: Clear data structures enable golden-file and regression testing.
5. **Reproducibility**: Seed-based determinism is built in.

