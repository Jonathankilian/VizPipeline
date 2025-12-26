# Code for VizPiplin
"""
VizPipeline: Generalistic Visualization Pipeline for Pandas DataFrames

A modular, orchestratable Python package for exploratory data visualization
with automated type inference, plot selection, and guardrails.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "you@example.com"
__license__ = "MIT"

from .core.orchestrator import VizPipeline
from .core.config import VizConfig, DEFAULT_CONFIG
from .core.types import (
    ColumnType,
    PlotType,
    RelationshipType,
    Report,
    PlotPlan,
    PlotItem,
    DataProfile,
    InferredType,
    DataQualityIssue,
    RelationshipScore,
)

__all__ = [
    "VizPipeline",
    "VizConfig",
    "DEFAULT_CONFIG",
    "ColumnType",
    "PlotType",
    "RelationshipType",
    "Report",
    "PlotPlan",
    "PlotItem",
    "DataProfile",
    "InferredType",
    "DataQualityIssue",
    "RelationshipScore",
]