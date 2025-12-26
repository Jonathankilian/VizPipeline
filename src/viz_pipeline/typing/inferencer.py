"""
ColumnTypeInferencer - Robust Type Detection

Purpose:
    Infer column types (numeric, categorical, datetime, boolean, etc.)
    with confidence scores and audit trail. Handles edge cases.
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from ..core.types import ColumnType, InferredType


class ColumnTypeInferencer:
    """
    Robust column type inference with audit trail.

    Purpose:
        Infer column types using rule-based system with confidence scores.
        Handles: boolean, ID-like, datetime, numeric, high-cardinality,
        categorical, text, unknown.

    How to use:
        >>> inferrer = ColumnTypeInferencer()
        >>> types = inferrer.infer_types(df, id_cols=["id"])
        >>> for col, inferred in types.items():
        ...     print(f"{col}: {inferred.inferred_type.value}")

    Attributes:
        None (stateless)
    """

    def infer_types(
            self,
            df: pd.DataFrame,
            id_cols: List[str] = None,
    ) -> Dict[str, InferredType]:
        """
        Infer types for all columns.

        Inputs:
            df (pd.DataFrame): Input DataFrame
            id_cols (List[str], optional): Columns to mark as ID-like

        What output:
            Dict[str, InferredType]: Column name -> InferredType
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
        """Infer type for single column using rules."""

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
                reason=f"Column name '{col_name}' matches ID pattern",
            )

        # Rule 3: Datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.DATETIME,
                confidence=0.99,
                rule_id="R_DATETIME_001",
                reason="dtype is datetime64",
            )

        # Try to parse as datetime
        if series.dtype == "object":
            try:
                parsed = pd.to_datetime(series, errors='coerce')
                if parsed.notna().mean() > 0.8:
                    return InferredType(
                        column_name=col_name,
                        inferred_type=ColumnType.DATETIME,
                        confidence=0.8,
                        rule_id="R_DATETIME_002",
                        reason="Successfully parsed 80%+ as datetime",
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
                reason="dtype is numeric (int/float)",
            )

        # Rule 5 & 6: High-cardinality vs Categorical (threshold: 50)
        n_unique = series.nunique()
        if n_unique > 50:
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.HIGH_CARDINALITY,
                confidence=0.9,
                rule_id="R_HIGHCARD_001",
                reason=f"{n_unique} unique values > 50 threshold",
            )
        else:
            return InferredType(
                column_name=col_name,
                inferred_type=ColumnType.CATEGORICAL,
                confidence=0.9,
                rule_id="R_CATEGORICAL_001",
                reason=f"{n_unique} unique values <= 50 threshold",
            )