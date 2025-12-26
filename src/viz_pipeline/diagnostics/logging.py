"""
Logging and audit trail system for VizPipeline.

Centralized logging for:
- Warnings (non-blocking issues)
- Errors (blocking or critical issues)
- Decision/rule firing (audit trail)

All logs are collected and included in the final Report.
"""

from typing import Dict, List, Any
from collections import defaultdict


class LogManager:
    """
    Central logging manager for warnings, errors, and audit decisions.
    
    Purpose:
        Track all pipeline decisions and issues in a single, queryable object.
        Enables transparency and debugging of plot selection logic.
    
    How to use:
        >>> log = LogManager(enabled=True, enable_warnings=True)
        >>> log.warning("Potential issue with column X")
        >>> log.error("Critical: Missing target column")
        >>> log.log_decision("RULE_UNI_NUMERIC", {"column": "age", "action": "histogram"})
        >>> audit = log.get_audit_log()
        >>> warnings = log.get_warnings()
    
    Attributes:
        enabled: If False, log_decision() calls are ignored.
        enable_warnings: If False, warning() calls are ignored.
        _warnings: List of warning messages.
        _errors: List of error messages.
        _decisions: Dict[rule_id -> List[details]] of all decisions.
    """
    
    def __init__(self, enabled: bool = True, enable_warnings: bool = True):
        """
        Initialize LogManager.
        
        Inputs:
            enabled (bool): Enable audit logging (default: True).
            enable_warnings (bool): Enable warning logging (default: True).
        
        What output:
            LogManager instance with empty logs.
        
        How to use:
            >>> log = LogManager(enabled=True)
        """
        self.enabled = enabled
        self.enable_warnings = enable_warnings
        self._warnings: List[str] = []
        self._errors: List[str] = []
        self._decisions: Dict[str, List[Any]] = defaultdict(list)
    
    def warning(self, message: str) -> None:
        """
        Log a non-blocking warning.
        
        Purpose:
            Record issues that don't stop execution but should be visible.
            Examples: constant columns, high missingness, degenerate cases.
        
        Inputs:
            message (str): Human-readable warning text.
        
        What output:
            None (side effect: appends to internal warning list).
        
        How to use:
            >>> log.warning("Column 'age' is constant")
            >>> log.warning("90% of target values are missing")
        
        Warnings/Failure modes:
            - IF enable_warnings=False: Message is silently discarded.
        """
        if self.enable_warnings:
            self._warnings.append(message)
    
    def error(self, message: str) -> None:
        """
        Log a blocking or critical error.
        
        Purpose:
            Record issues that may prevent proper execution or signal data problems.
            Examples: invalid input, incompatible column types, resource errors.
        
        Inputs:
            message (str): Human-readable error text.
        
        What output:
            None (side effect: appends to internal error list).
        
        How to use:
            >>> log.error("DataFrame has < 10 rows")
            >>> log.error("Target column not found in data")
        
        Warnings/Failure modes:
            - Errors are always logged (cannot be disabled).
        """
        self._errors.append(message)
    
    def log_decision(self, rule_id: str, details: Dict[str, Any]) -> None:
        """
        Log a pipeline decision/rule firing.
        
        Purpose:
            Record which rules fired, what they decided, and why.
            Enables post-hoc analysis of plot selection logic.
        
        Inputs:
            rule_id (str): Identifier for the rule/decision point.
                Examples: "RULE_PROFILING_001", "RULE_TYPE_BOOLEAN", "RULE_UNI_NUMERIC_SELECT".
            details (Dict[str, Any]): Arbitrary details about the decision.
                Examples: {"column": "age", "action": "skip", "reason": "constant"}
                         {"col_a": "x", "col_b": "y", "score": 0.87, "action": "select"}
        
        What output:
            None (side effect: appends details to audit log).
        
        How to use:
            >>> log.log_decision(
            ...     "RULE_PROFILING_COMPLETE",
            ...     {"n_rows": 150, "n_cols": 4, "issues_detected": 2}
            ... )
            >>> log.log_decision(
            ...     "RULE_TYPE_INFERENCE",
            ...     {
            ...         "column": "sepal_length",
            ...         "inferred_type": "numeric",
            ...         "confidence": 0.99,
            ...         "rule_fired": "R_NUMERIC_001"
            ...     }
            ... )
        
        Warnings/Failure modes:
            - IF enabled=False: Decision is silently discarded.
            - Multiple calls with same rule_id append to the list (not overwrite).
        """
        if self.enabled:
            self._decisions[rule_id].append(details)
    
    def get_warnings(self) -> List[str]:
        """
        Retrieve all logged warnings.
        
        Inputs: None
        
        What output:
            List[str]: All warning messages in order of logging.
        
        How to use:
            >>> warnings = log.get_warnings()
            >>> for w in warnings:
            ...     print(f"⚠️  {w}")
        """
        return self._warnings
    
    def get_errors(self) -> List[str]:
        """
        Retrieve all logged errors.
        
        Inputs: None
        
        What output:
            List[str]: All error messages in order of logging.
        
        How to use:
            >>> errors = log.get_errors()
            >>> if errors:
            ...     print(f"Found {len(errors)} errors")
            ...     for e in errors:
            ...         print(f"❌ {e}")
        """
        return self._errors
    
    def get_audit_log(self) -> Dict[str, List[Any]]:
        """
        Retrieve complete audit log of all decisions.
        
        Inputs: None
        
        What output:
            Dict[rule_id -> List[details]]: Nested dictionary of all decisions.
            Can be serialized to JSON for inspection or reporting.
        
        How to use:
            >>> audit = log.get_audit_log()
            >>> import json
            >>> print(json.dumps(audit, indent=2))
        """
        return dict(self._decisions)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get quick summary of all logging activity.
        
        Inputs: None
        
        What output:
            dict with keys:
                - "warnings_count": Number of warnings logged
                - "errors_count": Number of errors logged
                - "decision_rules_fired": Number of unique decision rules
                - "total_decision_logs": Total decision log entries
        
        How to use:
            >>> summary = log.get_summary()
            >>> print(f"Warnings: {summary['warnings_count']}, Errors: {summary['errors_count']}")
        """
        return {
            "warnings_count": len(self._warnings),
            "errors_count": len(self._errors),
            "decision_rules_fired": len(self._decisions),
            "total_decision_logs": sum(len(v) for v in self._decisions.values()),
        }
    
    def clear(self) -> None:
        """
        Clear all logs.
        
        Inputs: None
        
        What output:
            None (side effect: resets all internal lists and dicts).
        
        How to use:
            >>> log.clear()
            >>> # LogManager is now in initial state
        """
        self._warnings.clear()
        self._errors.clear()
        self._decisions.clear()
