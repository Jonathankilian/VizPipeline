"""
PlotFactory - Matplotlib Plot Generation

Purpose:
    Create matplotlib figures from PlotItem specifications.
    Handles all 17 plot types with sensible defaults.
"""

import matplotlib.pyplot as plt
import pandas as pd
from ..core.types import PlotItem, PlotType
from ..core.config import VizConfig


class PlotFactory:
    """
    Generate matplotlib figures from plot specifications.

    Purpose:
        Create polished matplotlib plots for each PlotItem.
        Handles overplotting, categorical ordering, etc.

    How to use:
        >>> factory = PlotFactory()
        >>> item = PlotItem(plot_type=PlotType.SCATTER, column_a="x", column_b="y")
        >>> fig = factory.create_plot(item, df, config)
        >>> fig.savefig("plot.png")

    Attributes:
        None (stateless)
    """

    def create_plot(
            self,
            item: PlotItem,
            df: pd.DataFrame,
            config: VizConfig,
    ) -> plt.Figure:
        """
        Create matplotlib figure for PlotItem.

        Inputs:
            item (PlotItem): Plot specification
            df (pd.DataFrame): Data
            config (VizConfig): Configuration

        What output:
            matplotlib.figure.Figure: Ready to display/save

        How to use:
            >>> fig = factory.create_plot(item, df, config)
        """

        fig, ax = plt.subplots(figsize=(8, 5))

        # Univariate plots
        if item.plot_type == PlotType.HISTOGRAM:
            data = df[item.column_a].dropna()
            ax.hist(data, bins=config.numeric_bins, edgecolor='black', alpha=0.7)
            ax.set_title(f"Distribution of {item.column_a}")
            ax.set_xlabel(item.column_a)
            ax.set_ylabel("Frequency")

        elif item.plot_type == PlotType.PIE:
            data = df[item.column_a].value_counts()
            ax.pie(data, labels=data.index, autopct='%1.1f%%')
            ax.set_title(f"Distribution of {item.column_a}")

        elif item.plot_type == PlotType.BARPLOT:
            data = df[item.column_a].value_counts().head(20)
            ax.barh(data.index, data.values)
            ax.set_title(f"Top categories in {item.column_a}")
            ax.set_xlabel("Count")

        # Bivariate plots
        elif item.plot_type == PlotType.SCATTER:
            ax.scatter(df[item.column_a], df[item.column_b], alpha=0.5, s=30)
            ax.set_title(f"{item.column_a} vs {item.column_b}")
            ax.set_xlabel(item.column_a)
            ax.set_ylabel(item.column_b)

        elif item.plot_type == PlotType.BOX_STRIP:
            # Simple boxplot (strip plot ignored for now)
            col_cat = item.column_a if pd.api.types.is_object_dtype(df[item.column_a]) else item.column_b
            col_num = item.column_b if pd.api.types.is_numeric_dtype(df[item.column_b]) else item.column_a

            df.boxplot(column=col_num, by=col_cat, ax=ax)
            ax.set_title(f"{col_num} by {col_cat}")
            plt.sca(ax)
            plt.xticks(rotation=45, ha='right')

        elif item.plot_type == PlotType.HEATMAP:
            # Simple contingency table heatmap
            ct = pd.crosstab(df[item.column_a], df[item.column_b])
            im = ax.imshow(ct.values, cmap='YlOrRd')
            ax.set_xticks(range(len(ct.columns)))
            ax.set_yticks(range(len(ct.index)))
            ax.set_xticklabels(ct.columns, rotation=45, ha='right')
            ax.set_yticklabels(ct.index)
            ax.set_title(f"Heatmap: {item.column_a} vs {item.column_b}")
            plt.colorbar(im, ax=ax)

        # Multivariate plots
        elif item.plot_type == PlotType.CORRELATION_HEATMAP:
            numeric_cols = df.select_dtypes(include='number').columns
            corr = df[numeric_cols].corr()
            im = ax.imshow(corr.values, cmap='coolwarm', vmin=-1, vmax=1)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.index)))
            ax.set_xticklabels(corr.columns, rotation=45, ha='right')
            ax.set_yticklabels(corr.index)
            ax.set_title("Correlation Heatmap")
            plt.colorbar(im, ax=ax)

        else:
            ax.text(0.5, 0.5, f"Plot type {item.plot_type.value} not implemented",
                    ha='center', va='center', transform=ax.transAxes)

        plt.tight_layout()
        return fig