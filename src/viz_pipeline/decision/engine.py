"""
DecisionEngine - Plot Selection & Ranking Heuristics

Purpose:
    Central rule block for selecting and prioritizing plots.
    Implements univariate, bivariate, and multivariate selection.
"""

from typing import Dict, List, Tuple
import pandas as pd
from ..core.types import (
    PlotPlan, PlotItem, PlotType, InferredType, ColumnType,
    RelationshipScore
)
from ..core.config import VizConfig
from ..diagnostics.logging import LogManager


class DecisionEngine:
    """
    Heuristic-based plot selection and ranking.

    Purpose:
        Decide which plots to generate based on:
        - Column types
        - Relationship strengths
        - Target analysis preferences
        - Configuration limits

    How to use:
        >>> engine = DecisionEngine()
        >>> plan = engine.select_and_rank(
        ...     df, type_assignment, score_dict, profile,
        ...     target_cols, config, log
        ... )
        >>> print(f"Selected {len(plan.items)} plots")

    Attributes:
        None (stateless)
    """

    def select_and_rank(
            self,
            df: pd.DataFrame,
            type_assignment: Dict[str, InferredType],
            score_dict: Dict[Tuple[str, str], RelationshipScore],
            profile,
            target_cols: List[str],
            config: VizConfig,
            log: LogManager,
    ) -> PlotPlan:
        """
        Select and rank plots across all dimensionalities.

        Inputs:
            df, type_assignment, score_dict, profile: From prior pipeline steps
            target_cols: Column names for target analysis
            config: VizConfig with limits and toggles
            log: LogManager for audit trail

        What output:
            PlotPlan with ranked PlotItems
        """
        plan = PlotPlan()
        plot_id_counter = 0

        # ========== UNIVARIATE PLOTS ==========
        univariate_items = self._select_univariate(
            type_assignment, df, config, log
        )
        for item in univariate_items[:config.max_univariate_plots]:
            item.plot_id = f"UNI_{plot_id_counter:03d}"
            item.rank = plot_id_counter
            plan.items.append(item)
            plot_id_counter += 1
        plan.univariate_count = len(univariate_items)

        # ========== BIVARIATE PLOTS ==========
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

        # ========== MULTIVARIATE PLOTS ==========
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
                plot_id="",
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
            score_dict: Dict[Tuple[str, str], RelationshipScore],
            target_cols: List[str],
            config: VizConfig,
            log: LogManager,
    ) -> List[PlotItem]:
        """Select bivariate plots, prioritizing target relationships."""
        items = []

        target_pairs = [
            (score, col_a, col_b)
            for (col_a, col_b), score in score_dict.items()
            if col_b in target_cols and col_a not in target_cols
        ]
        target_pairs.sort(key=lambda x: abs(x[0].primary_score), reverse=True)

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
            score_dict: Dict[Tuple[str, str], RelationshipScore],
            config: VizConfig,
            log: LogManager,
    ) -> List[PlotItem]:
        """Select bivariate plots, ranked by relationship strength."""
        items = []

        non_redundant = [
            (score, col_a, col_b)
            for (col_a, col_b), score in score_dict.items()
            if not score.is_redundant
        ]

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
        """Select appropriate bivariate plot type."""

        t_a = type_a.inferred_type
        t_b = type_b.inferred_type

        if t_a == ColumnType.NUMERIC and t_b == ColumnType.NUMERIC:
            return PlotType.SCATTER
        elif t_a in [ColumnType.NUMERIC, ColumnType.HIGH_CARDINALITY] and \
                t_b in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]:
            return PlotType.BOX_STRIP
        elif t_b in [ColumnType.NUMERIC, ColumnType.HIGH_CARDINALITY] and \
                t_a in [ColumnType.CATEGORICAL, ColumnType.BOOLEAN]:
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
        """Select multivariate plots."""
        if len(bivariate_items) >= 3:
            return [PlotItem(
                plot_id="",
                plot_type=PlotType.CORRELATION_HEATMAP,
                column_a="all_numeric",
                reason="Multivariate: Correlation heatmap",
            )]
        return []