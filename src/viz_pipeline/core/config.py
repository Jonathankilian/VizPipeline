"""
Configuration system for VizPipeline.

Central configuration dataclass with feature toggles, limits, and thresholds.
Supports JSON import/export for reproducibility and configuration management.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class VizConfig:
    """
    Central configuration for VizPipeline orchestrator.

    Purpose:
        Define all toggles, limits, and thresholds in one place.
        Enables reproducible, configurable pipeline execution.

    How to use:
        >>> config = VizConfig(max_univariate_plots=15, seed=123)
        >>> report = VizPipeline.run(df, config=config)

    Attributes (Data Thresholds):
        high_card_threshold: Unique values > this = high-cardinality (default: 50)
        sample_limit: Downsample if n_rows > this (default: 10000)
        missing_allowed_pct: Warn if missing % > this (default: 0.2)

    Attributes (Limits/Guardrails):
        max_univariate_plots: Maximum univariate visualizations (default: 25)
        max_bivariate_pairs: Maximum bivariate relationships (default: 15)
        max_multivariate_views: Maximum multivariate plots (default: 3)
        target_top_k_features: Top-K features for target analysis (default: 5)

    Attributes (Plot Parameters):
        numeric_bins: Number of bins for histograms (default: 20)
        text_sample_n: Sample size for text analysis (default: 100)
        overplot_threshold_n: Switch to hexbin if n > this (default: 1000)

    Attributes (Feature Toggles):
        enable_target_analysis: Prioritize target relationships (default: True)
        enable_multivariate: Include 3D/correlation plots (default: True)
        enable_datetime_views: Visualize datetime columns (default: True)
        enable_text_summary: Generate text summaries (default: True)
        enable_export_html: Generate HTML report (default: True)
        enable_sampling: Downsample large datasets (default: True)
        enable_audit_log: Track all decisions (default: True)
        enable_warnings: Log warnings (default: True)

    Attributes (Reproducibility):
        seed: Random seed for deterministic behavior (default: 42)

    Attributes (Export):
        export_format: "html", "json", or "both" (default: "html")
        export_dir: Directory for exported files (default: None = in-memory)

    Attributes (Advanced):
        correlation_redundancy_threshold: Correlation > this = redundant (default: 0.95)
        numeric_only_correlation: Only correlate numeric columns (default: False)
    """

    # --- Data Thresholds ---
    high_card_threshold: int = 50
    sample_limit: int = 10000
    missing_allowed_pct: float = 0.2

    # --- Limits (Guardrails) ---
    max_univariate_plots: int = 25
    max_bivariate_pairs: int = 15
    max_multivariate_views: int = 3
    target_top_k_features: int = 5

    # --- Plot Parameters ---
    numeric_bins: int = 20
    text_sample_n: int = 100
    overplot_threshold_n: int = 1000

    # --- Feature Toggles ---
    enable_target_analysis: bool = True
    enable_multivariate: bool = True
    enable_datetime_views: bool = True
    enable_text_summary: bool = True
    enable_export_html: bool = True
    enable_sampling: bool = True
    enable_audit_log: bool = True
    enable_warnings: bool = True

    # --- Reproducibility ---
    seed: int = 42

    # --- Export ---
    export_format: str = "html"
    export_dir: Optional[str] = None

    # --- Advanced ---
    correlation_redundancy_threshold: float = 0.95
    numeric_only_correlation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Inputs: None

        What output:
            dict: All configuration parameters as key-value pairs.

        How to use:
            >>> config = VizConfig()
            >>> d = config.to_dict()
            >>> print(d["max_univariate_plots"])
            25
        """
        return {k: v for k, v in self.__dict__.items()}

    @staticmethod
    def from_dict(config_dict: Dict[str, Any]) -> "VizConfig":
        """
        Create config from dictionary.

        Inputs:
            config_dict (Dict[str, Any]): Dictionary of config values.
                Only keys matching VizConfig attributes are used.

        What output:
            VizConfig: Instantiated configuration object.

        How to use:
            >>> d = {"max_univariate_plots": 10, "seed": 99}
            >>> config = VizConfig.from_dict(d)

        Warnings/Failure modes:
            - IF config_dict has unknown keys: They are silently ignored.
            - IF required fields are missing: Uses defaults.
        """
        # Filter only valid VizConfig fields
        valid_fields = {f for f in VizConfig.__dataclass_fields__.keys()}
        filtered = {k: v for k, v in config_dict.items() if k in valid_fields}
        return VizConfig(**filtered)

    def to_json(self, filepath: str) -> None:
        """
        Save configuration to JSON file.

        Inputs:
            filepath (str): Path to output JSON file (e.g., "config.json").

        What output:
            None (writes file side effect).

        How to use:
            >>> config = VizConfig(max_univariate_plots=10)
            >>> config.to_json("my_config.json")

        Warnings/Failure modes:
            - IF filepath is invalid: Raises FileNotFoundError or PermissionError.
            - IF directory doesn't exist: Raises FileNotFoundError.
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def from_json(filepath: str) -> "VizConfig":
        """
        Load configuration from JSON file.

        Inputs:
            filepath (str): Path to JSON config file.

        What output:
            VizConfig: Loaded configuration object.

        How to use:
            >>> config = VizConfig.from_json("my_config.json")
            >>> report = VizPipeline.run(df, config=config)

        Warnings/Failure modes:
            - IF file doesn't exist: Raises FileNotFoundError.
            - IF JSON is invalid: Raises json.JSONDecodeError.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return VizConfig.from_dict(data)


# Default configuration singleton
DEFAULT_CONFIG = VizConfig()