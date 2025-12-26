"""
Core data structures for VizPipeline.

Defines all dataclasses and enums used throughout the pipeline:
- ColumnType, PlotType, RelationshipType enums
- InferredType, DataQualityIssue, DataProfile
- RelationshipScore, PlotItem, PlotPlan
- Report (final output)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import pandas as pd


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
    """
    Result of column type inference.

    Attributes:
        column_name: Name of the column
        inferred_type: Classified ColumnType
        confidence: Confidence score (0.0-1.0)
        rule_id: Which rule fired (e.g., "R_BOOLEAN_001")
        reason: Human-readable explanation
        metadata: Additional context dictionary
    """
    column_name: str
    inferred_type: ColumnType
    confidence: float
    rule_id: str
    reason: str
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
    """
    A single data quality problem detected during profiling.

    Attributes:
        severity: "ERROR", "WARNING", or "INFO"
        column: Column name (None if dataset-level issue)
        message: Human-readable description
        metric_name: Technical metric identifier
        metric_value: Numeric or other value of the metric
    """
    severity: str
    column: Optional[str]
    message: str
    metric_name: str
    metric_value: Optional[Any] = None


@dataclass
class DataProfile:
    """
    High-level statistical summary of the entire dataset.

    Attributes:
        n_rows: Number of observations
        n_cols: Number of columns
        memory_mb: Total memory usage in MB
        dtypes_distribution: {dtype: count} histogram
        missing_by_col: {column_name: pct_missing} (0.0-1.0)
        unique_by_col: {column_name: n_unique}
        quality_issues: List of detected issues
    """
    n_rows: int
    n_cols: int
    memory_mb: float
    dtypes_distribution: Dict[str, int]
    missing_by_col: Dict[str, float]
    unique_by_col: Dict[str, int]
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
    """
    Numeric score quantifying a bivariate relationship.

    Attributes:
        col_a, col_b: Column names
        relationship_type: Inferred relationship type
        primary_score: Main correlation/association metric
        secondary_score: P-value or other secondary metric
        is_redundant: True if |score| > redundancy_threshold
        effect_size_interpretation: "small", "medium", "large", or "unknown"
        metadata: Additional scoring context
    """
    col_a: str
    col_b: str
    relationship_type: RelationshipType
    primary_score: float
    secondary_score: Optional[float] = None
    is_redundant: bool = False
    effect_size_interpretation: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
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
    """
    A single plot to be generated.

    Attributes:
        plot_id: Unique identifier (e.g., "UNI_001", "BIV_005")
        plot_type: Type of visualization
        column_a: Primary column (x-axis or focus)
        column_b: Secondary column (y-axis), None for univariate
        column_c: Tertiary column (z-axis), None unless 3D
        rank: Priority/ordering rank in final plan
        score: Relevance score from RelationshipScorer
        reason: Human-readable justification for selection
        params: Plot-specific parameters (bins, alpha, etc.)
        figure: Matplotlib figure object (populated after plotting)
    """
    plot_id: str
    plot_type: PlotType
    column_a: str
    column_b: Optional[str] = None
    column_c: Optional[str] = None
    rank: int = 0
    score: Optional[float] = None
    reason: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    figure: Optional[Any] = None

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
    """
    The complete plan of visualizations to generate.

    Attributes:
        items: List of PlotItem objects, ordered by rank
        univariate_count: Number of univariate plots selected
        bivariate_count: Number of bivariate plots selected
        multivariate_count: Number of multivariate plots selected
        audit_log: Dictionary of selection decisions
    """
    items: List[PlotItem] = field(default_factory=list)
    univariate_count: int = 0
    bivariate_count: int = 0
    multivariate_count: int = 0
    audit_log: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "univariate_count": self.univariate_count,
            "bivariate_count": self.bivariate_count,
            "multivariate_count": self.multivariate_count,
            "total_count": len(self.items),
            "items": [item.to_dict() for item in self.items],
            "audit_log": self.audit_log,
        }


@dataclass
class Report:
    """
    Complete output of VizPipeline.run().

    The Report is the primary return value containing all results,
    metadata, warnings, and machine-readable summaries.

    Attributes:
        plot_plan: PlotPlan with ranked visualization items
        data_profile: DataProfile with shape and quality info
        type_assignment: Dict[column_name -> InferredType]
        html_report: Complete HTML document (if enabled)
        json_summary: Machine-readable JSON summary
        audit_log: Dictionary of all decision traces
        warnings: List of non-blocking issues
        errors: List of blocking issues encountered
        metadata: Version, timestamp, seed, config used
    """
    plot_plan: PlotPlan
    data_profile: DataProfile
    type_assignment: Dict[str, InferredType]
    html_report: Optional[str] = None
    json_summary: Optional[Dict[str, Any]] = None
    audit_log: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

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