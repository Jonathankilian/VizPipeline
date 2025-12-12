"""
Core data contracts (types) for VizPipeline.

Purpose
-------
Defines the stable, testable data structures that every module uses:
profiling, type inference, relationship scoring, decision engine,
reporting, and exporting.

How to use
----------
- Import these types in other modules to avoid ad-hoc dict structures.
- Treat these dataclasses as immutable "contracts" between components.

What output
-----------
This module contains only types and helpers. It produces no plots, files,
or side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


# -----------------------------
# Enums
# -----------------------------

class Severity(str, Enum):
    """
    Severity levels for diagnostics and issues.

    How to use
    ----------
    - Use Severity.ERROR for blocking problems.
    - Use Severity.WARNING for non-blocking but important issues.
    - Use Severity.INFO for informational notes.

    What output
    -----------
    - String-valued enum suitable for JSON export.
    """
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ColumnKind(str, Enum):
    """
    Canonical column type taxonomy used across the pipeline.

    How to use
    ----------
    - Assign one ColumnKind per column via the type inference module.
    - Downstream components (scoring/decision) branch on ColumnKind.

    What output
    -----------
    - String-valued enum suitable for JSON export.
    """
    NUMERIC = "NUMERIC"
    CATEGORICAL = "CATEGORICAL"
    HIGH_CARDINALITY = "HIGH_CARDINALITY"
    DATETIME = "DATETIME"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    ID = "ID"
    UNKNOWN = "UNKNOWN"


class PlotScope(str, Enum):
    """
    Granularity of a visualization item.

    How to use
    ----------
    - UNIVARIATE: one column
    - BIVARIATE: two columns
    - MULTIVARIATE: >=3 columns

    What output
    -----------
    - String-valued enum suitable for JSON export.
    """
    UNIVARIATE = "UNIVARIATE"
    BIVARIATE = "BIVARIATE"
    MULTIVARIATE = "MULTIVARIATE"


# -----------------------------
# Diagnostics / Issues
# -----------------------------

@dataclass(frozen=True)
class QualityIssue:
    """
    A structured diagnostic emitted by profiling, inference, scoring, etc.

    How to use
    ----------
    - Create issues instead of raising for non-blocking problems.
    - Collect issues and show them in the "Limitations & Warnings" report chapter.

    Inputs
    ------
    severity:
        Severity level (ERROR/WARNING/INFO).
    message:
        Human-readable message.
    column:
        Optional column name the issue refers to.
    details:
        Optional key/value details safe for JSON export (e.g., counts, thresholds).

    What output
    -----------
    - A JSON-serializable object (enums are strings).
    """
    severity: Severity
    message: str
    column: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


# -----------------------------
# Profiling
# -----------------------------

@dataclass(frozen=True)
class DataProfile:
    """
    Lightweight dataset profile used for decisions and reporting.

    How to use
    ----------
    - Produced by the DataframeProfiler.
    - Consumed by TypeInferrer and DecisionEngine to apply guardrails and limits.

    Inputs
    ------
    n_rows, n_cols:
        Basic shape.
    dtypes:
        Mapping column -> dtype string (as reported by pandas).
    missing_rate:
        Mapping column -> fraction in [0, 1].
    unique_count:
        Mapping column -> integer number of unique values (incl. NaN handling by profiler policy).
    constant_cols:
        Columns detected as constant / near-constant by profiler policy.
    duplicate_row_count:
        Number of duplicated rows (policy-defined).
    notes:
        Free-form notes (e.g., "sampled", "large dataset") suitable for report.

    What output
    -----------
    - Immutable snapshot of dataset diagnostics.
    """
    n_rows: int
    n_cols: int
    dtypes: Mapping[str, str]
    missing_rate: Mapping[str, float]
    unique_count: Mapping[str, int]
    constant_cols: Tuple[str, ...] = ()
    duplicate_row_count: int = 0
    notes: Tuple[str, ...] = ()


# -----------------------------
# Type Inference
# -----------------------------

@dataclass(frozen=True)
class InferredColumnType:
    """
    Result of type inference for a single column.

    How to use
    ----------
    - Created by ColumnTypeInferrer.
    - Use 'kind' for branching; keep 'reason' for audit/report transparency.

    Inputs
    ------
    kind:
        ColumnKind classification.
    confidence:
        Float in [0, 1] indicating heuristic confidence (not a statistical probability).
    rule_id:
        Identifier of the rule/heuristic that assigned this type (for audit logs).
    reason:
        Short human-readable explanation (for report).

    What output
    -----------
    - Immutable, JSON-friendly object.
    """
    kind: ColumnKind
    confidence: float
    rule_id: str
    reason: str


@dataclass(frozen=True)
class TypeAssignment:
    """
    Collection of inferred column types.

    How to use
    ----------
    - Produced by ColumnTypeInferrer.infer_types(...)
    - Pass around as a single object to prevent drift and missing columns.

    What output
    -----------
    - Mapping-like container with helper accessors.
    """
    types: Mapping[str, InferredColumnType]

    def kind_of(self, column: str) -> ColumnKind:
        """Return ColumnKind for a column (UNKNOWN if missing)."""
        t = self.types.get(column)
        return t.kind if t is not None else ColumnKind.UNKNOWN

    def columns_of_kind(self, kind: ColumnKind) -> Tuple[str, ...]:
        """Return all columns assigned to a given ColumnKind."""
        return tuple(col for col, t in self.types.items() if t.kind == kind)


# -----------------------------
# Relationship Scoring (generic contract)
# -----------------------------

@dataclass(frozen=True)
class RelationshipScore:
    """
    Generic relationship score between columns.

    How to use
    ----------
    - Produced by RelationshipScorer for candidate pairs (or subsets).
    - DecisionEngine uses 'strength' for ranking and 'method' for transparency.

    Inputs
    ------
    strength:
        Normalized strength in [0, 1] (policy-defined; not necessarily correlation).
    method:
        Name of scoring method (e.g., 'spearman', 'cramers_v', 'eta').
    details:
        Additional method-specific values (e.g., raw coefficients, group sizes).
    caveats:
        Human-readable caveats (e.g., "n too small", "many missing").

    What output
    -----------
    - Immutable, JSON-serializable score object.
    """
    strength: float
    method: str
    details: Dict[str, Any] = field(default_factory=dict)
    caveats: Tuple[str, ...] = ()


# -----------------------------
# Plot planning (no rendering here)
# -----------------------------

@dataclass(frozen=True)
class PlotItem:
    """
    A planned visualization (decision-layer output), without rendering details.

    How to use
    ----------
    - DecisionEngine creates PlotItems (what to plot and why).
    - Plotting/rendering layer consumes PlotItems and decides how to render.

    Inputs
    ------
    scope:
        PlotScope (univariate/bivariate/multivariate).
    columns:
        Tuple of involved column names (len depends on scope).
    plot_kind:
        Abstract plot type identifier (e.g., 'distribution', 'scatter', 'heatmap').
        Keep this stable; renderer maps it to concrete libraries.
    reason:
        Human-readable explanation for selection.
    priority:
        Higher means more important (used for ordering).
    related_to_target:
        Whether this plot is target-aware (helps report structure).
    score:
        Optional RelationshipScore for bivariate/multivariate ranking transparency.
    meta:
        Optional additional info (e.g., 'sampled': True, 'top_k': 20). Must be JSON-safe.

    What output
    -----------
    - Immutable description of a plot decision. No figures, no files.
    """
    scope: PlotScope
    columns: Tuple[str, ...]
    plot_kind: str
    reason: str
    priority: float = 0.0
    related_to_target: bool = False
    score: Optional[RelationshipScore] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlotPlan:
    """
    Full plot plan produced by DecisionEngine.

    How to use
    ----------
    - The pipeline returns PlotPlan as part of the final Report object.
    - Renderers iterate plan.items in order and create visuals.

    Inputs
    ------
    items:
        Ordered list of PlotItem.
    limits_applied:
        Records which guardrails/limits were applied (e.g., max_bivariate_pairs).
    audit:
        High-level audit log (counts, rules fired, reasons) safe for JSON.

    What output
    -----------
    - Immutable plan and metadata, suitable for golden-file tests.
    """
    items: Tuple[PlotItem, ...]
    limits_applied: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)

    @property
    def n_items(self) -> int:
        """How many PlotItems are in this plan."""
        return len(self.items)

    def by_scope(self, scope: PlotScope) -> Tuple[PlotItem, ...]:
        """Return items matching a given PlotScope."""
        return tuple(i for i in self.items if i.scope == scope)
