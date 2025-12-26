# 📓 VizPipeline - Jupyter Notebook Integration Guide

## 🎯 OVERVIEW

Diese Anleitung zeigt dir, wie du **VizPipeline vollständig in Jupyter Notebooks** einbindest und verwendest.

---

## 📋 INHALTSVERZEICHNIS

1. Setup & Installation
2. Imports & Configuration
3. Basic Usage in Notebooks
4. Advanced Workflows
5. Output Rendering
6. Capabilities & Limitations
7. Troubleshooting
8. Best Practices

---

## 1️⃣ SETUP & INSTALLATION

### 1.1 Prerequisites

```bash
# Jupyter installieren (falls nicht vorhanden)
pip install jupyter jupyterlab

# VizPipeline installieren
cd /path/to/viz-pipeline
pip install -e ".[dev]"

# Notebooks starten
jupyter notebook
# oder
jupyter lab
```

### 1.2 Verify Installation

```python
# Neue Zelle in Jupyter
import sys
print(f"Python: {sys.version}")

import pandas as pd
print(f"Pandas: {pd.__version__}")

import matplotlib
print(f"Matplotlib: {matplotlib.__version__}")

from viz_pipeline import VizPipeline
print("✅ VizPipeline installed successfully!")
```

---

## 2️⃣ IMPORTS & CONFIGURATION

### 2.1 Standard Imports

```python
# Data manipulation
import pandas as pd
import numpy as np

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns

# VizPipeline
from viz_pipeline import (
    VizPipeline,
    VizConfig,
    DEFAULT_CONFIG,
    DataframeProfiler,
    ColumnTypeInferencer,
    RelationshipScorer,
    DecisionEngine,
    PlotFactory,
    ReportComposer,
    LogManager,
)
from viz_pipeline.core.types import ColumnType, PlotType

# Utilities
import json
from pathlib import Path
```

### 2.2 Notebook Configuration

```python
# Magic commands für bessere Output-Rendering
%matplotlib inline
%load_ext autoreload
%autoreload 2

# Display settings
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 150)

# Matplotlib default style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
```

### 2.3 Create Helper Functions

```python
def load_and_prepare_data(filepath, **kwargs):
    """Helper function für Datenladen"""
    df = pd.read_csv(filepath, **kwargs)
    print(f"✅ Loaded {filepath}")
    print(f"   Shape: {df.shape}")
    print(f"   Dtypes: {df.dtypes.unique()}")
    return df


def summarize_report(report):
    """Quick summary of VizPipeline report"""
    print("📊 REPORT SUMMARY")
    print(f"├─ Plots generated: {len(report.plot_plan.items)}")
    print(f"│  ├─ Univariate: {report.plot_plan.univariate_count}")
    print(f"│  ├─ Bivariate: {report.plot_plan.bivariate_count}")
    print(f"│  └─ Multivariate: {report.plot_plan.multivariate_count}")
    print(f"├─ Warnings: {len(report.warnings)}")
    print(f"└─ Errors: {len(report.errors)}")
    
    if report.warnings:
        print("\n⚠️  WARNINGS:")
        for w in report.warnings[:3]:
            print(f"  - {w}")
```

---

## 3️⃣ BASIC USAGE IN NOTEBOOKS

### 3.1 Minimal Example

```python
# Load data
df = pd.read_csv('data.csv')

# Run VizPipeline
report = VizPipeline.run(df)

# Summary
summarize_report(report)
```

### 3.2 With Target Variable

```python
df = load_and_prepare_data('data.csv')

# Run with target analysis
report = VizPipeline.run(
    df,
    target_cols=['churn'],  # Prioritize churn-related plots
    config=VizConfig(
        max_univariate_plots=15,
        max_bivariate_pairs=10,
        seed=42
    )
)

summarize_report(report)
```

### 3.3 Accessing Results

```python
# DataFrame shape & profile
print("📋 Data Profile:")
profile = report.data_profile
print(f"Shape: {profile.shape}")
print(f"Missing %: {profile.missing_pct}")
print(f"Quality issues: {len(profile.quality_issues)}")

# Column types
print("\n🔍 Column Types:")
for col, inferred_type in report.type_assignment.items():
    print(f"  {col:20} → {inferred_type.column_type.value:15} "
          f"(confidence: {inferred_type.confidence:.2f})")

# Selected plots
print("\n📊 Selected Plots:")
for i, item in enumerate(report.plot_plan.items[:5], 1):
    print(f"  {i}. {item.plot_type.value} ({item.columns})")
```

### 3.4 Displaying HTML Report

```python
from IPython.display import HTML, display

# Display HTML report in notebook
display(HTML(report.html_report))

# Or render in separate cell
HTML(report.html_report)
```

---

## 4️⃣ ADVANCED WORKFLOWS

### 4.1 Multi-Dimensional Analysis

```python
# Scenario: Analyze different target variables
targets = ['churn', 'revenue', 'satisfaction']

results = {}
for target in targets:
    print(f"\n🎯 Analyzing {target}...")
    report = VizPipeline.run(
        df,
        target_cols=[target],
        config=VizConfig(
            enable_target_analysis=True,
            target_top_k_features=8,
            seed=42
        )
    )
    results[target] = report
    print(f"   ✅ {len(report.plot_plan.items)} plots selected")

# Compare results
print("\n📊 Comparison:")
for target, report in results.items():
    print(f"{target:15} → {len(report.plot_plan.items)} plots")
```

### 4.2 Step-by-Step Pipeline Inspection

```python
# Run each step individually for inspection
print("🔍 STEP-BY-STEP PIPELINE INSPECTION\n")

# Step 1: Profiling
profiler = DataframeProfiler()
profile = profiler.profile(df)
print(f"1. PROFILING ✅")
print(f"   Shape: {profile.shape}")
print(f"   Memory: {profile.memory_mb:.2f} MB")

# Step 2: Type Inference
inferencer = ColumnTypeInferencer()
types = inferencer.infer_types(df, id_cols=['id'])
print(f"\n2. TYPE INFERENCE ✅")
for col, inferred in list(types.items())[:5]:
    print(f"   {col:20} → {inferred.column_type.value}")

# Step 3: Relationship Scoring
scorer = RelationshipScorer()
scores = scorer.score_all_pairs(df, types)
print(f"\n3. RELATIONSHIP SCORING ✅")
print(f"   Relationships scored: {len(scores)}")
top_pairs = sorted(scores.items(), 
                  key=lambda x: x[1].strength, 
                  reverse=True)[:3]
for (col_a, col_b), score in top_pairs:
    print(f"   {col_a:15} ↔ {col_b:15} : {score.strength:.3f}")

# Step 4: Decision Engine
engine = DecisionEngine()
plan = engine.select_and_rank(df, types, scores)
print(f"\n4. DECISION ENGINE ✅")
print(f"   Plots selected: {len(plan.items)}")
print(f"   ├─ Univariate: {plan.univariate_count}")
print(f"   ├─ Bivariate: {plan.bivariate_count}")
print(f"   └─ Multivariate: {plan.multivariate_count}")
```

### 4.3 Custom Configuration Comparison

```python
# Compare different configurations
configs = {
    'aggressive': VizConfig(
        max_univariate_plots=30,
        max_bivariate_pairs=20,
    ),
    'balanced': VizConfig(
        max_univariate_plots=20,
        max_bivariate_pairs=12,
    ),
    'conservative': VizConfig(
        max_univariate_plots=10,
        max_bivariate_pairs=5,
    ),
}

comparison = {}
for name, config in configs.items():
    report = VizPipeline.run(df, config=config)
    comparison[name] = {
        'univariate': report.plot_plan.univariate_count,
        'bivariate': report.plot_plan.bivariate_count,
        'total': len(report.plot_plan.items),
    }

# Display comparison
comparison_df = pd.DataFrame(comparison).T
print("\n📊 Configuration Comparison:")
print(comparison_df)
```

### 4.4 Audit Trail Analysis

```python
# Deep dive into decision-making
report = VizPipeline.run(df, config=VizConfig(
    enable_audit_log=True,
    seed=42
))

# Examine audit log
audit = report.audit_log
print("📋 AUDIT LOG ENTRIES:")
for i, (step, entries) in enumerate(audit.items(), 1):
    print(f"\n{i}. {step.upper()}")
    if isinstance(entries, list):
        for entry in entries[:3]:
            print(f"   - {entry}")
    elif isinstance(entries, dict):
        for key, val in list(entries.items())[:3]:
            print(f"   - {key}: {val}")
```

---

## 5️⃣ OUTPUT RENDERING

### 5.1 HTML Report Display

```python
from IPython.display import HTML, display, IFrame
from pathlib import Path

# Save and display HTML
report = VizPipeline.run(df)
html_file = Path('/tmp/report.html')

with open(html_file, 'w') as f:
    f.write(report.html_report)

# Option 1: Display inline
display(HTML(report.html_report))

# Option 2: Display in iframe (if HTML is large)
display(IFrame(str(html_file), width=1000, height=600))

# Option 3: Create download link
from IPython.display import FileLink
display(FileLink(str(html_file)))
```

### 5.2 JSON Summary Visualization

```python
import json
from IPython.display import JSON

# Display JSON summary
report = VizPipeline.run(df)

# Option 1: Pretty print
print("📄 JSON Summary:")
print(json.dumps(report.json_summary, indent=2))

# Option 2: Interactive JSON display
display(JSON(report.json_summary))

# Option 3: Save and load
with open('summary.json', 'w') as f:
    json.dump(report.json_summary, f, indent=2)
```

### 5.3 Type Assignment Visualization

```python
import pandas as pd

# Create DataFrame from type assignment
types_df = pd.DataFrame([
    {
        'Column': col,
        'Type': inferred.column_type.value,
        'Confidence': f"{inferred.confidence:.2%}",
        'Rule': inferred.rule_id,
    }
    for col, inferred in report.type_assignment.items()
])

print("🔍 Type Assignments:")
display(types_df)

# Visualize confidence
fig, ax = plt.subplots(figsize=(12, 4))
types_df['Confidence'] = types_df['Confidence'].str.rstrip('%').astype(float)
types_df.set_index('Column')['Confidence'].plot(kind='barh', ax=ax)
ax.set_xlabel('Confidence Score')
ax.set_title('Type Inference Confidence')
plt.tight_layout()
plt.show()
```

### 5.4 Plot Plan Visualization

```python
# Visualize selected plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Plot type distribution
plot_types = [item.plot_type.value for item in report.plot_plan.items]
plot_counts = pd.Series(plot_types).value_counts()
plot_counts.plot(kind='barh', ax=ax1)
ax1.set_xlabel('Count')
ax1.set_title('Plot Type Distribution')

# Dimensionality distribution
dims = ['Univariate'] * report.plot_plan.univariate_count + \
       ['Bivariate'] * report.plot_plan.bivariate_count + \
       ['Multivariate'] * report.plot_plan.multivariate_count
dim_counts = pd.Series(dims).value_counts()
dim_counts.plot(kind='bar', ax=ax2, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax2.set_ylabel('Count')
ax2.set_title('Dimensionality Distribution')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)

plt.tight_layout()
plt.show()
```

---

## 6️⃣ CAPABILITIES & LIMITATIONS

### ✅ CAPABILITIES (Was funktioniert)

```python
# ✅ Automatic type detection
report = VizPipeline.run(df)
# → Erkennt 8 verschiedene Spaltentypen

# ✅ Relationship scoring
# → Spearman für numerisch, Cramér's V für kategorisch

# ✅ Plot selection
# → Intelligente Auswahl basierend auf Datentypen

# ✅ Target-aware analysis
report = VizPipeline.run(df, target_cols=['target'])
# → Priorisiert Features related to target

# ✅ HTML & JSON export
with open('report.html', 'w') as f:
    f.write(report.html_report)
with open('summary.json', 'w') as f:
    json.dump(report.json_summary, f)

# ✅ Audit trail
for entry in report.audit_log['decisions'][:5]:
    print(entry)

# ✅ Configurable behavior
config = VizConfig(max_univariate_plots=15, seed=42)
report = VizPipeline.run(df, config=config)

# ✅ Full type hints & docstrings
help(VizPipeline.run)
```

### ❌ LIMITATIONS (Was funktioniert NICHT in Phase 2)

```python
# ❌ NO seaborn styling yet
# → Plots sind basic matplotlib (Phase 3)

# ❌ NO interactive plots (Plotly)
# → Nur statische matplotlib figures (Phase 3)

# ❌ NO 3D plots
# → Nur 2D + correlation heatmap (Phase 3)

# ❌ NO statistical test outputs
# → Keine p-values oder Confidence Intervals (Phase 3)

# ❌ NO Jupyter-specific displays
# → Keine custom widgets oder callbacks (Phase 3)

# ❌ NO real-time streaming
# → Für batch-Verarbeitung, nicht streaming

# ❌ NO custom plot types
# → Nur die 20 eingebauten Plot-Typen

# ❌ BASIC matplotlib plots
# → Einfache Visualisierung, keine komplexen Layouts
```

### 📊 PHASE ROADMAP

```
Phase 2 ✅ (Current)
├─ Core infrastructure
├─ Type inference
├─ Relationship scoring
├─ Basic plot generation
└─ HTML/JSON export

Phase 3 🔄 (Planned)
├─ Seaborn styling
├─ Interactive Plotly plots
├─ 3D visualizations
├─ Statistical tests
├─ Jupyter widgets
└─ Performance optimization

Phase 4 📅 (Vision)
├─ Custom plot plugins
├─ Real-time streaming
├─ Cloud integration
└─ Production dashboards
```

---

## 7️⃣ TROUBLESHOOTING

### Problem: ImportError mit VizPipeline

```python
# ❌ Fehler: ModuleNotFoundError: No module named 'viz_pipeline'

# ✅ Lösung:
# 1. Sicherstellen, dass Installation komplett ist:
#    cd /path/to/viz-pipeline
#    pip install -e ".[dev]"

# 2. Kernel neu starten (Jupyter Menu → Kernel → Restart)

# 3. Path überprüfen:
import sys
print(sys.path)
# Sollte VizPipeline Verzeichnis enthalten
```

### Problem: Slow Performance

```python
# ❌ Pipeline ist langsam bei großen DataFrames

# ✅ Lösungen:

# Option 1: Sampling aktivieren
config = VizConfig(enable_sampling=True, sample_limit=5000)
report = VizPipeline.run(df, config=config)

# Option 2: Limits reduzieren
config = VizConfig(
    max_univariate_plots=10,
    max_bivariate_pairs=5,
)
report = VizPipeline.run(df, config=config)

# Option 3: Feature-Subset verwenden
df_subset = df[['feature1', 'feature2', 'target']]
report = VizPipeline.run(df_subset)

# Option 4: Multivariate deaktivieren
config = VizConfig(enable_multivariate=False)
report = VizPipeline.run(df, config=config)
```

### Problem: Memory Error

```python
# ❌ MemoryError bei sehr großen DataFrames

# ✅ Lösungen:

# Reduziere Daten
df = df.sample(frac=0.5)  # 50% der Daten

# Oder verwende chunks
for chunk in pd.read_csv('large.csv', chunksize=10000):
    report = VizPipeline.run(chunk)
    # Process chunk-by-chunk
```

### Problem: Matplotlib Display nicht sichtbar

```python
# ❌ Plots werden nicht angezeigt

# ✅ Lösungen:

# 1. Magic command:
%matplotlib inline

# 2. Explizit zeigen:
import matplotlib.pyplot as plt
plt.show()

# 3. In Notebook ausführen (nicht in .py file)
```

---

## 8️⃣ BEST PRACTICES

### 8.1 Notebook Structure

```python
# 📓 Empfohlener Notebook-Aufbau:

# Cell 1: Setup & Imports
%matplotlib inline
from viz_pipeline import VizPipeline, VizConfig
import pandas as pd

# Cell 2: Load Data
df = pd.read_csv('data.csv')
print(f"Loaded {df.shape}")

# Cell 3: Run VizPipeline
report = VizPipeline.run(df, target_cols=['target'])

# Cell 4: Explore Results
print(f"Generated {len(report.plot_plan.items)} plots")

# Cell 5: Export Reports
with open('report.html', 'w') as f:
    f.write(report.html_report)

# Cell 6: Detailed Analysis
# Deep dive into specific aspects
```

### 8.2 Reproducibility

```python
# Nutze seed für reproducible results
config = VizConfig(seed=42)
report = VizPipeline.run(df, config=config)

# Save config für später
import json
config_dict = config.to_dict()
with open('config.json', 'w') as f:
    json.dump(config_dict, f)

# Später reloaden
from viz_pipeline import VizConfig
loaded_config = VizConfig.from_dict(config_dict)
report = VizPipeline.run(df, config=loaded_config)
```

### 8.3 Error Handling

```python
# Robustly handle errors
try:
    report = VizPipeline.run(df, target_cols=['target'])
    print(f"✅ {len(report.plot_plan.items)} plots generated")
except KeyError as e:
    print(f"❌ Column not found: {e}")
except ValueError as e:
    print(f"❌ Invalid input: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

# Check for warnings
if report.warnings:
    print(f"\n⚠️  {len(report.warnings)} warnings:")
    for w in report.warnings[:5]:
        print(f"  - {w}")

# Check for errors
if report.errors:
    print(f"\n❌ {len(report.errors)} errors:")
    for e in report.errors:
        print(f"  - {e}")
```

### 8.4 Large DataFrames

```python
# Für große DataFrames:

# ✅ DO: Sampling verwenden
config = VizConfig(
    enable_sampling=True,
    sample_limit=10000,
)
report = VizPipeline.run(df, config=config)

# ✅ DO: Feature selection
important_cols = ['col1', 'col2', 'col3', 'target']
df_subset = df[important_cols]
report = VizPipeline.run(df_subset)

# ✅ DO: Reduce limits
config = VizConfig(
    max_univariate_plots=10,
    max_bivariate_pairs=8,
)
report = VizPipeline.run(df, config=config)

# ❌ DON'T: Run on entire large dataset without limits
```

### 8.5 Debugging Tips

```python
# Nutze individual tools für debugging

# Debug Type Inference
from viz_pipeline.typing import ColumnTypeInferencer
inferencer = ColumnTypeInferencer()
types = inferencer.infer_types(df)
print(types)  # See type assignments

# Debug Relationship Scoring
from viz_pipeline.scoring import RelationshipScorer
scorer = RelationshipScorer()
scores = scorer.score_all_pairs(df, types)
top_pairs = sorted(scores.items(), 
                  key=lambda x: abs(x[1].strength), 
                  reverse=True)[:5]
for (a, b), score in top_pairs:
    print(f"{a} ↔ {b}: {score.strength:.3f}")

# Debug Plot Selection
from viz_pipeline.decision import DecisionEngine
engine = DecisionEngine()
plan = engine.select_and_rank(df, types, scores)
for item in plan.items[:5]:
    print(f"{item.plot_type.value}: {item.columns}")
```

---

## 📚 COMPLETE NOTEBOOK TEMPLATE

```python
"""
VizPipeline Exploratory Data Analysis
=====================================
Automated visualization pipeline for pandas DataFrames
"""

# ============================================================================
# 1. SETUP
# ============================================================================
%matplotlib inline
%load_ext autoreload
%autoreload 2

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from IPython.display import HTML, display, JSON

from viz_pipeline import VizPipeline, VizConfig, DEFAULT_CONFIG

# ============================================================================
# 2. CONFIGURATION
# ============================================================================
pd.set_option('display.max_columns', 20)
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

OUTPUT_DIR = Path('reports')
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# 3. LOAD DATA
# ============================================================================
df = pd.read_csv('data.csv')
print(f"✅ Loaded {df.shape[0]} rows × {df.shape[1]} columns")
print(f"Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
display(df.head())

# ============================================================================
# 4. RUN VIZPIPELINE
# ============================================================================
config = VizConfig(
    max_univariate_plots=20,
    max_bivariate_pairs=12,
    enable_target_analysis=True,
    seed=42
)

print("\n⏳ Running VizPipeline...")
report = VizPipeline.run(
    df,
    target_cols=['target'],
    id_cols=['id'],
    config=config
)
print(f"✅ Complete!\n")

# ============================================================================
# 5. SUMMARY
# ============================================================================
print("📊 REPORT SUMMARY")
print(f"├─ Plots: {len(report.plot_plan.items)}")
print(f"│  ├─ Univariate: {report.plot_plan.univariate_count}")
print(f"│  ├─ Bivariate: {report.plot_plan.bivariate_count}")
print(f"│  └─ Multivariate: {report.plot_plan.multivariate_count}")
print(f"├─ Warnings: {len(report.warnings)}")
print(f"└─ Errors: {len(report.errors)}")

# ============================================================================
# 6. EXPORT
# ============================================================================
html_path = OUTPUT_DIR / 'report.html'
json_path = OUTPUT_DIR / 'summary.json'

with open(html_path, 'w') as f:
    f.write(report.html_report)

with open(json_path, 'w') as f:
    json.dump(report.json_summary, f, indent=2)

print(f"\n✅ Saved reports:")
print(f"   HTML: {html_path}")
print(f"   JSON: {json_path}")

# ============================================================================
# 7. DISPLAY RESULTS
# ============================================================================
display(HTML(report.html_report))
```

---

## 🚀 NEXT STEPS

1. **Install VizPipeline** - Follow installation guide
2. **Create Jupyter Notebook** - Use template above
3. **Load Your Data** - DataFrame with 10+ rows
4. **Run Pipeline** - One-liner: `VizPipeline.run(df)`
5. **Explore Results** - HTML report + JSON export
6. **Iterate** - Adjust config, try different targets

---

## 📞 SUPPORT

- **Dokumentation:** [IMPLEMENTATION_DOCUMENTATION.md](../IMPLEMENTATION_DOCUMENTATION.md)
- **Installation:** [PHASE2_INSTALLATION_GUIDE.txt](../PHASE2_INSTALLATION_GUIDE.txt)
- **Code Docstrings:** `help(VizPipeline.run)`
- **Issues:** Check GitHub Issues

---

**Ready to explore your data? Start with Cell 1 of the template! 🎉**
