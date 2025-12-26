"""
VizPipeline: Generalistic Visualization Pipeline for Pandas DataFrames

Main package entry point. Exports public API for end-users.
(UPDATED FOR PHASE 2 - VizPipeline class now available)
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "Generalistic visualization pipeline for pandas DataFrames"

# Core orchestrator (available in Phase 2)
from .core.orchestrator import VizPipeline

# Configuration
from .core.config import VizConfig, DEFAULT_CONFIG

# Types (enums and dataclasses)
from .core.types import (
    ColumnType,
    PlotType,
    RelationshipType,
    InferredType,
    DataQualityIssue,
    DataProfile,
    RelationshipScore,
    PlotItem,
    PlotPlan,
    Report,
)

# Diagnostics
from .diagnostics.logging import LogManager

# Tools (Phase 2)
from .profiling import DataframeProfiler
from .typing import ColumnTypeInferencer
from .scoring import RelationshipScorer
from .decision import DecisionEngine
from .plotting import PlotFactory
from .reporting import ReportComposer
from .export import ExportEngine

# Public API
__all__ = [
    # Version
    "__version__",
    "__author__",
    "__description__",

    # Core Orchestrator
    "VizPipeline",

    # Configuration
    "VizConfig",
    "DEFAULT_CONFIG",

    # Types & Enums
    "ColumnType",
    "PlotType",
    "RelationshipType",
    "InferredType",
    "DataQualityIssue",
    "DataProfile",
    "RelationshipScore",
    "PlotItem",
    "PlotPlan",
    "Report",

    # Diagnostics
    "LogManager",

    # Tools
    "DataframeProfiler",
    "ColumnTypeInferencer",
    "RelationshipScorer",
    "DecisionEngine",
    "PlotFactory",
    "ReportComposer",
    "ExportEngine",
]