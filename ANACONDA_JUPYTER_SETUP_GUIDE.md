# 📓 ANACONDA + JUPYTER NOTEBOOK - COMPLETE SETUP GUIDE

## 🎯 OVERVIEW

Dieser Guide zeigt dir **Schritt für Schritt**, wie du VizPipeline in **Anaconda + Jupyter Notebook** einbindest und nutzt.

---

## 📋 INHALTSVERZEICHNIS

1. Anaconda Environment Setup
2. VizPipeline Installation im Environment
3. Jupyter Notebook Launch
4. First Notebook Creation
5. Complete Working Example
6. Troubleshooting
7. Best Practices

---

## 1️⃣ ANACONDA ENVIRONMENT SETUP

### 1.1 Check Anaconda Installation

```bash
# Terminal/CMD öffnen und überprüfen
conda --version
python --version

# Sollte zeigen:
# conda 23.x.x (oder höher)
# Python 3.9+ (empfohlen 3.10 oder 3.11)
```

### 1.2 Create New Environment for VizPipeline

```bash
# IMPORTANT: Neues Environment für VizPipeline erstellen
# (Nicht in base environment installieren!)

conda create -n vizpipeline python=3.11

# Wenn gefragt: y (yes) eingeben und Enter

# Output sollte so aussehen:
# ...
# Proceed ([y]/n)? y
# ...
# done.
```

### 1.3 Activate Environment

```bash
# Environment aktivieren
conda activate vizpipeline

# Wenn erfolgreich, sieht deine Kommandozeile so aus:
# (vizpipeline) C:\Users\YourName\...>   (Windows)
# (vizpipeline) user@MacBook ... $         (Mac)
# (vizpipeline) user@linux ... $           (Linux)
```

**⚠️ WICHTIG:** Das `(vizpipeline)` Prefix zeigt an, dass dein Environment aktiv ist!

---

## 2️⃣ VIZPIPELINE INSTALLATION IM ENVIRONMENT

### 2.1 Navigate to VizPipeline Project

```bash
# Zu deinem VizPipeline Verzeichnis navigieren
cd /path/to/VizPipeline

# Beispiele:
# Windows: cd C:\Users\YourName\Documents\VizPipeline
# Mac:     cd /Users/yourname/Documents/VizPipeline
# Linux:   cd ~/Documents/VizPipeline

# Überprüfen, dass du im richtigen Verzeichnis bist
ls  # Mac/Linux
dir # Windows

# Sollte zeigen:
# src/
# docs/
# README.md
# pyproject.toml
# ...
```

### 2.2 Install VizPipeline in Development Mode

```bash
# Sichere dich ab: Environment ist aktiv!
# Du solltest (vizpipeline) sehen

# Install in development mode
pip install -e ".[dev]"

# Dies wird 1-2 Minuten dauern
# Du solltest sehen:
# Successfully installed viz-pipeline ...
# Processing dependencies...
# ...
```

**Was bedeutet `-e ".[dev]"`?**
- `-e` = editable (Änderungen am Code werden sofort sichtbar)
- `.` = install current directory
- `[dev]` = install development dependencies (testing, etc.)

### 2.3 Verify Installation

```bash
# Überprüfe, dass Installation funktioniert
python -c "from viz_pipeline import VizPipeline; print('✅ VizPipeline is ready!')"

# Sollte ausgeben:
# ✅ VizPipeline is ready!

# Falls Fehler:
# → Überprüfe, dass du im VizPipeline Verzeichnis bist
# → Überprüfe, dass Environment aktiv ist
# → Versuche: pip install -e ".[dev]" nochmal
```

### 2.4 Install Additional Jupyter Dependencies

```bash
# Jupyter ist wahrscheinlich schon installiert, aber sichergehen
conda install -c conda-forge jupyterlab notebook

# Alternative (wenn conda nicht funktioniert):
pip install jupyter jupyterlab

# Überprüfe Installation
jupyter --version

# Sollte ausgeben:
# Selected Jupyter core packages ...
# IPython: ...
# jupyter_client: ...
```

---

## 3️⃣ JUPYTER NOTEBOOK LAUNCH

### 3.1 Aktiviere Environment (falls noch nicht aktiv)

```bash
# Überprüfe, dass Environment aktiv ist
# Terminal sollte zeigen: (vizpipeline) ...

# Wenn nicht aktiv:
conda activate vizpipeline
```

### 3.2 Navigate to Working Directory

```bash
# Zu deinem Arbeitsverzeichnis gehen (wo Notebooks sein sollen)
# Optionen:

# Option 1: Im VizPipeline Verzeichnis bleiben
cd /path/to/VizPipeline

# Option 2: Separates Verzeichnis für Notebooks
cd /path/to/MyNotebooks
# oder erstelle ein neues:
mkdir MyJupyterNotebooks
cd MyJupyterNotebooks
```

### 3.3 Start Jupyter Notebook

```bash
# WICHTIG: Environment muss aktiv sein (vizpipeline)!

# Starte Jupyter
jupyter notebook

# Oder mit diesem Befehl (JupyterLab, modernere Version):
jupyter lab

# WICHTIG: NICHT Ctrl+C drücken!
# Das würde Jupyter beenden!

# Output sollte so aussehen:
# [I 2025-12-26 13:10:00.000 NotebookApp] Starting Jupyter...
# [I 2025-12-26 13:10:01.000 NotebookApp] Jupyter Server is running...
# [I 2025-12-26 13:10:02.000 NotebookApp] http://localhost:8888/?token=abc123...
```

### 3.4 Access Jupyter in Browser

```
Jupyter sollte automatisch öffnen.
Wenn nicht: Kopiere die URL aus Terminal (http://localhost:...)
und öffne sie in deinem Browser.

Du solltest sehen:
- Dateibrowser auf der linken Seite
- "New" Button (oben rechts)
- Existing notebooks/files
```

**Hinweis:** Wenn du mehrere Notebooks offen hast:
- Jedes Notebook hat sein eigenes Tab
- Terminal bleibt offen (zeigt Logs)
- Schließe Terminal nicht!

---

## 4️⃣ FIRST NOTEBOOK CREATION

### 4.1 Create New Notebook

```
Im Jupyter Browser:
1. Klick auf "New" Button (oben rechts)
2. Wähle "Python 3" (nicht Python 2!)
3. Warte kurz
4. Neuer Tab öffnet sich mit leerer Notebook
```

### 4.2 Rename Notebook (Optional but Recommended)

```
1. Oben siehst du "Untitled" oder eine Nummer
2. Rechtsklick darauf (oder klick auf Text)
3. Eingeben: "VizPipeline_Test" oder ein Name
4. Enter drücken
5. Notebook wird umbenannt
```

### 4.3 First Cell - Verify Environment

```python
# Kopiere dies in die erste Zelle (Code Cell)
import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")

# Ctrl+Enter drücken zum Ausführen (oder "Run" Button oben)

# Output sollte zeigen:
# Python: 3.11.x ... 
# Executable: /path/to/envs/vizpipeline/bin/python
```

**Hinweis:** Wenn Executable einen anderen Pfad zeigt (nicht vizpipeline):
→ Kernel ist falsch! Siehe Troubleshooting unten.

### 4.4 Second Cell - Import VizPipeline

```python
# Neue Zelle hinzufügen (+ Button oben)
from viz_pipeline import VizPipeline, VizConfig
import pandas as pd
import numpy as np

print("✅ All imports successful!")
```

**Run:** Ctrl+Enter

Sollte ausgeben: `✅ All imports successful!`

---

## 5️⃣ COMPLETE WORKING EXAMPLE

### 5.1 Create Sample Data

```python
# Neue Zelle
import pandas as pd
import numpy as np

# Erstelle Sample Dataset
np.random.seed(42)
df = pd.DataFrame({
    'age': np.random.randint(18, 80, 100),
    'income': np.random.randint(20000, 150000, 100),
    'score': np.random.random(100) * 100,
    'churn': np.random.choice([0, 1], 100),
    'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
})

print(df.head())
print(f"\nShape: {df.shape}")
print(f"\nDtypes:\n{df.dtypes}")
```

**Run:** Ctrl+Enter

Output zeigt first 5 rows + shape + dtypes

### 5.2 Configure VizPipeline

```python
# Neue Zelle
from viz_pipeline import VizConfig

config = VizConfig(
    max_univariate_plots=15,
    max_bivariate_pairs=10,
    enable_target_analysis=True,
    seed=42
)

print("✅ Configuration created!")
print(f"Max univariate plots: {config.max_univariate_plots}")
print(f"Seed: {config.seed}")
```

### 5.3 Run VizPipeline

```python
# Neue Zelle - WICHTIG: Dies dauert ~10-30 Sekunden!
from viz_pipeline import VizPipeline

print("⏳ Running VizPipeline... (this may take a moment)")

report = VizPipeline.run(
    df,
    target_cols=['churn'],
    config=config
)

print("✅ VizPipeline completed!")
```

### 5.4 Explore Results

```python
# Neue Zelle
print("📊 REPORT SUMMARY")
print(f"├─ Plots generated: {len(report.plot_plan.items)}")
print(f"│  ├─ Univariate: {report.plot_plan.univariate_count}")
print(f"│  ├─ Bivariate: {report.plot_plan.bivariate_count}")
print(f"│  └─ Multivariate: {report.plot_plan.multivariate_count}")
print(f"├─ Warnings: {len(report.warnings)}")
print(f"└─ Errors: {len(report.errors)}")
```

### 5.5 Display HTML Report

```python
# Neue Zelle
from IPython.display import HTML, display

# Display HTML report inline in notebook
display(HTML(report.html_report))

# Oder: Speichern als Datei
with open('viz_report.html', 'w') as f:
    f.write(report.html_report)
    
print("✅ Report saved as viz_report.html")
```

### 5.6 Export JSON Summary

```python
# Neue Zelle
import json

# Save JSON summary
with open('viz_summary.json', 'w') as f:
    json.dump(report.json_summary, f, indent=2)

print("✅ JSON summary saved as viz_summary.json")

# Show first 500 chars
summary_str = json.dumps(report.json_summary, indent=2)
print("\n" + summary_str[:500] + "\n...")
```

### 5.7 Visualize Type Assignments

```python
# Neue Zelle
import pandas as pd

# Create DataFrame from type assignments
types_df = pd.DataFrame([
    {
        'Column': col,
        'Type': inferred.column_type.value,
        'Confidence': f"{inferred.confidence:.1%}",
    }
    for col, inferred in report.type_assignment.items()
])

print("🔍 Type Assignments:")
print(types_df.to_string(index=False))
```

### 5.8 View Selected Plots

```python
# Neue Zelle
print("📊 Selected Plots:")
for i, item in enumerate(report.plot_plan.items[:10], 1):
    print(f"{i:2}. {item.plot_type.value:20} | {str(item.columns)[:40]}")

if len(report.plot_plan.items) > 10:
    print(f"... and {len(report.plot_plan.items) - 10} more")
```

---

## 6️⃣ TROUBLESHOOTING

### Problem: "ModuleNotFoundError: No module named 'viz_pipeline'"

```
❌ Fehler beim Import

✅ Lösungen:

1. Überprüfe Environment:
   - Terminal sollte zeigen: (vizpipeline)
   - Wenn nicht: conda activate vizpipeline

2. Überprüfe Installation:
   python -c "from viz_pipeline import VizPipeline"
   
3. Wechsle Kernel in Jupyter:
   - Oben rechts: "Kernel" Menu
   - "Change kernel" 
   - Wähle "Python [conda env:vizpipeline]" oder "Python 3"
   
4. Neinstall:
   pip install -e ".[dev]" nochmal

5. Restart Jupyter:
   - Browser Tab schließen
   - Terminal: Ctrl+C
   - jupyter notebook nochmal starten
```

### Problem: "ImportError: cannot import name 'VizPipeline' from 'viz_pipeline'"

```
❌ Installation unvollständig

✅ Lösungen:

1. Überprüfe, dass du im VizPipeline Verzeichnis bist:
   pwd  # Mac/Linux
   cd  # Windows
   
   Sollte zeigen: .../VizPipeline (oder /path/to/VizPipeline)

2. Überprüfe pyproject.toml existiert:
   ls pyproject.toml  # Mac/Linux
   dir pyproject.toml # Windows

3. Neuinstall:
   pip uninstall viz-pipeline
   pip install -e ".[dev]"
   
4. Restart Jupyter
```

### Problem: "Kernel seems to have died. Restarting..."

```
❌ Jupyter Kernel abgestürzt

✅ Lösungen:

1. Warte kurz (Kernel startet neu)

2. Wenn es immer wieder passiert:
   - Browser Tab schließen
   - Terminal: Ctrl+C
   - conda activate vizpipeline nochmal
   - jupyter notebook nochmal starten

3. Check memory:
   - Wenn dein Notebook zu viel RAM braucht:
   - Nutze smaller dataset
   - Oder: enable_sampling=True in config
```

### Problem: Jupyter öffnet nicht im Browser

```
❌ Browser öffnet nicht automatisch

✅ Lösungen:

1. Terminal zeigt URL:
   http://localhost:8888/?token=abc123...
   
   Kopiere diese URL in Browser (Chrome, Firefox, etc.)

2. Wenn auch das nicht funktioniert:
   - Terminal: Ctrl+C (stop Jupyter)
   - jupyter notebook --no-browser
   - Kopiere URL aus Terminal
   - Öffne Browser, paste URL

3. Wenn Port 8888 schon in Benutzung:
   - jupyter notebook --port 8889
   - Oder: jupyter notebook --port 9999
```

### Problem: "pandas is not installed"

```
❌ pandas fehlt

✅ Lösung:
pip install pandas numpy matplotlib scipy seaborn
```

### Problem: Notebook lädt sehr langsam

```
❌ VizPipeline lädt lange

Das ist NORMAL bei großen DataFrames!

✅ Lösungen:

1. Nutze kleineres Dataset zum Testen:
   df = df.head(1000)  # Nur erste 1000 rows

2. Enable Sampling in config:
   config = VizConfig(
       enable_sampling=True,
       sample_limit=5000
   )

3. Reduziere Limits:
   config = VizConfig(
       max_univariate_plots=10,
       max_bivariate_pairs=5
   )
```

---

## 7️⃣ BEST PRACTICES FÜR JUPYTER

### 7.1 Notebook Structure

```python
# Cell 1: IMPORTS & SETUP
%matplotlib inline
import pandas as pd
import numpy as np
from viz_pipeline import VizPipeline, VizConfig

print("✅ Setup complete!")

# Cell 2: LOAD DATA
df = pd.read_csv('data.csv')
print(f"Loaded {df.shape}")

# Cell 3: CONFIGURE
config = VizConfig(...)

# Cell 4: RUN
report = VizPipeline.run(df, config=config)

# Cell 5+: EXPLORE RESULTS
print(f"Generated {len(report.plot_plan.items)} plots")
# ...
```

### 7.2 Markdown Cells for Documentation

```
Add Markdown cells zwischen Code Cells für Dokumentation:

Click "+ Markdown" oder change cell type:
1. Select cell
2. Cell menu → Cell Type → Markdown
3. Schreibe Markdown:

# My Analysis

This notebook explores customer data using VizPipeline.

## Data Overview
- 1000 rows
- 20 columns
- Target: churn

## Results
- 25 plots generated
- 5 key findings
```

### 7.3 Save Your Work

```python
# Jupyter speichert automatisch, aber:

# Manual save:
Ctrl+S  # Windows/Linux
Cmd+S   # Mac

# Or: File menu → Save and Checkpoint

# WICHTIG: Speichere regelmäßig!
# Wenn Kernel crashed vor dem Speichern → Arbeit verloren
```

### 7.4 Clear Output (wenn Notebook zu groß wird)

```
Cell menu → All Output → Clear

Oder:
Kernel menu → Restart & Clear Output

Das löscht die Ausgaben, nicht den Code!
```

### 7.5 Export Notebook

```
File menu → Download as:
- Notebook (.ipynb) ← Standard format
- HTML (.html) ← Share mit anderen
- PDF (.pdf) ← Print friendly
- Python (.py) ← Just the code
```

---

## 📝 COMPLETE FIRST NOTEBOOK TEMPLATE

Kopiere dies in eine neue Notebook (Zelle für Zelle):

```python
# CELL 1: Setup
%matplotlib inline
import pandas as pd
import numpy as np
from viz_pipeline import VizPipeline, VizConfig
print("✅ Imports complete!")

# CELL 2: Create Sample Data
np.random.seed(42)
df = pd.DataFrame({
    'age': np.random.randint(18, 80, 100),
    'income': np.random.randint(20000, 150000, 100),
    'churn': np.random.choice([0, 1], 100),
})
print(f"Created DataFrame: {df.shape}")
print(df.head())

# CELL 3: Configure
config = VizConfig(
    max_univariate_plots=12,
    max_bivariate_pairs=8,
    seed=42
)
print("✅ Configuration created!")

# CELL 4: Run VizPipeline
report = VizPipeline.run(df, target_cols=['churn'], config=config)
print(f"✅ Generated {len(report.plot_plan.items)} plots!")

# CELL 5: View Results
print("\n📊 SUMMARY:")
print(f"Univariate: {report.plot_plan.univariate_count}")
print(f"Bivariate: {report.plot_plan.bivariate_count}")

# CELL 6: Export
from IPython.display import HTML, display
display(HTML(report.html_report))
```

**Run jeden Cell mit:** Ctrl+Enter

---

## ✅ CHECKLIST

- [ ] Anaconda installiert (conda --version zeigt Version)
- [ ] Neues Environment erstellt: conda create -n vizpipeline python=3.11
- [ ] Environment aktiviert: conda activate vizpipeline
- [ ] Zu VizPipeline Verzeichnis navigiert: cd /path/to/VizPipeline
- [ ] VizPipeline installiert: pip install -e ".[dev]"
- [ ] Installation verified: python -c "from viz_pipeline import VizPipeline"
- [ ] Jupyter installiert: jupyter --version
- [ ] Jupyter gestartet: jupyter notebook
- [ ] Neue Notebook erstellt
- [ ] First cell executed: python version zeigt vizpipeline environment

---

## 🚀 QUICK START (ZUSAMMENFASSUNG)

```bash
# 1. Open Terminal/Anaconda Prompt

# 2. Create & Activate Environment
conda create -n vizpipeline python=3.11
conda activate vizpipeline

# 3. Navigate to VizPipeline
cd /path/to/VizPipeline

# 4. Install
pip install -e ".[dev]"

# 5. Start Jupyter
jupyter notebook

# 6. In Jupyter Browser:
# - Click "New" → "Python 3"
# - Copy template from above
# - Run each cell (Ctrl+Enter)
# - Explore results!
```

**Time:** ~5 minutes setup + ~2 minutes first run

---

## 📞 WHEN STUCK

1. **Check Terminal** - Zeigt oft die Lösung
2. **Restart Kernel** - Oft hilft ein Neustart
3. **Restart Jupyter** - Ctrl+C im Terminal, jupyter notebook nochmal
4. **Check Environment** - Zeige (vizpipeline) prefix
5. **Read Error Message** - Oft sehr hilfreich!
6. **Reference Troubleshooting** - Siehe Abschnitt 6

---

**Ready to use VizPipeline in Jupyter? Start with Step 1! 🎉**
