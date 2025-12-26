"""
RelationshipScorer - Bivariate Relationship Analysis

Purpose:
    Score all pairs of columns for statistical relationships.
    Detects redundant (correlated) pairs and effect sizes.
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, chi2_contingency
from ..core.types import InferredType, RelationshipScore, RelationshipType, ColumnType


class RelationshipScorer:
    """
    Score all bivariate relationships in DataFrame.

    Purpose:
        Compute relationship strength between all column pairs using
        appropriate statistics (Pearson, Spearman, Cramér's V).
        Identify redundant (highly correlated) pairs.

    How to use:
        >>> scorer = RelationshipScorer()
        >>> scores = scorer.score_all_pairs(df, type_assignment)
        >>> for (col_a, col_b), score in scores.items():
        ...     if not score.is_redundant:
        ...         print(f"{col_a} vs {col_b}: r={score.primary_score:.2f}")

    Attributes:
        None (stateless)
    """

    def score_all_pairs(
            self,
            df: pd.DataFrame,
            type_assignment: Dict[str, InferredType],
    ) -> Dict[Tuple[str, str], RelationshipScore]:
        """
        Score all bivariate relationships.

        Inputs:
            df (pd.DataFrame): Input DataFrame
            type_assignment (Dict): Column type assignments

        What output:
            Dict[(col_a, col_b) -> RelationshipScore]
        """
        score_dict = {}
        columns = list(df.columns)

        for i, col_a in enumerate(columns):
            for col_b in columns[i + 1:]:
                # Skip ID-like columns
                if type_assignment[col_a].inferred_type == ColumnType.ID_LIKE:
                    continue
                if type_assignment[col_b].inferred_type == ColumnType.ID_LIKE:
                    continue

                rel_type = self._infer_relationship_type(
                    type_assignment[col_a],
                    type_assignment[col_b]
                )

                score = self._compute_score(
                    df[col_a],
                    df[col_b],
                    rel_type
                )

                score_dict[(col_a, col_b)] = score

        return score_dict

    def _infer_relationship_type(
            self,
            type_a: InferredType,
            type_b: InferredType,
    ) -> RelationshipType:
        """Determine relationship type based on column types."""

        t_a = type_a.inferred_type
        t_b = type_b.inferred_type

        # Numeric x Numeric
        if t_a == ColumnType.NUMERIC and t_b == ColumnType.NUMERIC:
            return RelationshipType.NUMERIC_NUMERIC

        # Numeric x Categorical
        if (t_a == ColumnType.NUMERIC and t_b in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]) or \
                (t_b == ColumnType.NUMERIC and t_a in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]):
            return RelationshipType.NUMERIC_CATEGORICAL

        # Categorical x Categorical
        if t_a in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN] and \
                t_b in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]:
            return RelationshipType.CATEGORICAL_CATEGORICAL

        # Datetime x others
        if t_a == ColumnType.DATETIME and t_b == ColumnType.NUMERIC:
            return RelationshipType.DATETIME_NUMERIC
        if t_b == ColumnType.DATETIME and t_a == ColumnType.NUMERIC:
            return RelationshipType.DATETIME_NUMERIC

        return RelationshipType.UNKNOWN

    def _compute_score(
            self,
            col_a: pd.Series,
            col_b: pd.Series,
            rel_type: RelationshipType,
    ) -> RelationshipScore:
        """Compute score based on relationship type."""

        try:
            if rel_type == RelationshipType.NUMERIC_NUMERIC:
                # Spearman correlation (rank-based, robust)
                corr, pval = spearmanr(col_a.dropna(), col_b.dropna())
                return RelationshipScore(
                    col_a=col_a.name,
                    col_b=col_b.name,
                    relationship_type=rel_type,
                    primary_score=abs(corr) if not np.isnan(corr) else 0.0,
                    secondary_score=pval if not np.isnan(pval) else 1.0,
                    is_redundant=abs(corr) > 0.95 if not np.isnan(corr) else False,
                    effect_size_interpretation=self._interpret_effect_size(abs(corr) if not np.isnan(corr) else 0.0),
                )

            elif rel_type == RelationshipType.CATEGORICAL_CATEGORICAL:
                # Cramér's V
                ct = pd.crosstab(col_a, col_b)
                chi2, pval, dof, expected = chi2_contingency(ct)
                n = ct.sum().sum()
                cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1))) if n > 0 else 0.0

                return RelationshipScore(
                    col_a=col_a.name,
                    col_b=col_b.name,
                    relationship_type=rel_type,
                    primary_score=cramers_v,
                    secondary_score=pval,
                    is_redundant=cramers_v > 0.95,
                    effect_size_interpretation=self._interpret_effect_size(cramers_v),
                )

            else:
                # Generic low score for other types
                return RelationshipScore(
                    col_a=col_a.name,
                    col_b=col_b.name,
                    relationship_type=rel_type,
                    primary_score=0.0,
                    secondary_score=None,
                    is_redundant=False,
                    effect_size_interpretation="unknown",
                )

        except Exception as e:
            # If scoring fails, return neutral score
            return RelationshipScore(
                col_a=col_a.name,
                col_b=col_b.name,
                relationship_type=rel_type,
                primary_score=0.0,
                secondary_score=None,
                is_redundant=False,
                effect_size_interpretation="unknown",
            )

    def _interpret_effect_size(self, score: float) -> str:
        """Interpret effect size (rough heuristic)."""
        if score < 0.3:
            return "small"
        elif score < 0.7:
            return "medium"
        else:
            return "large"