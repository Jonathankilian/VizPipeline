"""
DataframeProfiler - Fast Data Quality Assessment

Purpose:
    Quickly scan DataFrame for shape, dtypes, missingness, duplicates,
    and data quality issues. Produces DataProfile + quality warnings.
"""

from typing import List
import pandas as pd
import numpy as np
from ..core.types import DataProfile, DataQualityIssue


class DataframeProfiler:
    """
    Quick profiling of pandas DataFrames.

    Purpose:
        Generate summary statistics about data shape, dtypes, missing values,
        and detect common quality issues (duplicates, constant columns, etc.)

    How to use:
        >>> profiler = DataframeProfiler()
        >>> profile = profiler.profile(df)
        >>> issues = profiler.detect_quality_issues(df)
        >>> print(f"Dataset: {profile.n_rows} rows, {profile.memory_mb:.1f} MB")

    Attributes:
        None (stateless)
    """

    def profile(self, df: pd.DataFrame) -> DataProfile:
        """
        Generate DataProfile from DataFrame.

        Inputs:
            df (pd.DataFrame): Input DataFrame

        What output:
            DataProfile: shape, dtypes, memory, missing %, unique counts

        How to use:
            >>> profile = profiler.profile(df)
            >>> print(profile.n_rows)
        """
        return DataProfile(
            n_rows=df.shape[0],
            n_cols=df.shape[1],
            memory_mb=df.memory_usage(deep=True).sum() / (1024 ** 2),
            dtypes_distribution=dict(df.dtypes.value_counts()),
            missing_by_col={col: df[col].isna().mean() for col in df.columns},
            unique_by_col={col: df[col].nunique() for col in df.columns},
        )

    def detect_quality_issues(self, df: pd.DataFrame) -> List[DataQualityIssue]:
        """
        Detect common data quality issues.

        Inputs:
            df (pd.DataFrame): Input DataFrame

        What output:
            List[DataQualityIssue]: Quality warnings/errors
        """
        issues = []

        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            issues.append(DataQualityIssue(
                severity="WARNING",
                column=None,
                message=f"Dataset has {dup_count} duplicate rows",
                metric_name="duplicate_rows",
                metric_value=dup_count,
            ))

        # Check for constant columns
        for col in df.columns:
            if df[col].nunique() <= 1:
                issues.append(DataQualityIssue(
                    severity="WARNING",
                    column=col,
                    message=f"Column '{col}' is constant",
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
                    message=f"Column '{col}' has {missing_pct * 100:.1f}% missing",
                    metric_name="high_missingness",
                    metric_value=missing_pct,
                ))

        return issues