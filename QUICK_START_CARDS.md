# ⚡ QUICK START CARDS - ANACONDA + GIT

## 🎓 ANACONDA + JUPYTER - 5 MINUTE SETUP

### ✅ If Anaconda Already Installed:

```bash
# Terminal/Anaconda Prompt

# 1. Create environment
conda create -n vizpipeline python=3.11

# 2. Activate it
conda activate vizpipeline

# 3. Go to your VizPipeline folder
cd /path/to/VizPipeline

# 4. Install
pip install -e ".[dev]"

# 5. Test
python -c "from viz_pipeline import VizPipeline; print('✅')"

# 6. Start Jupyter
jupyter notebook

# 7. In browser: New → Python 3 → Copy template below
```

### 📓 Minimal Notebook Template (Copy into cells):

```python
# CELL 1
%matplotlib inline
from viz_pipeline import VizPipeline, VizConfig
import pandas as pd
import numpy as np
print("✅ Ready!")

# CELL 2
np.random.seed(42)
df = pd.DataFrame({
    'age': np.random.randint(18, 80, 100),
    'income': np.random.randint(20000, 150000, 100),
    'churn': np.random.choice([0, 1], 100),
})
print(f"Created: {df.shape}")

# CELL 3
config = VizConfig(max_univariate_plots=12, max_bivariate_pairs=8)
report = VizPipeline.run(df, target_cols=['churn'], config=config)

# CELL 4
print(f"✅ {len(report.plot_plan.items)} plots generated!")

# CELL 5
from IPython.display import HTML, display
display(HTML(report.html_report))
```

### 🔧 Troubleshooting Quick Fixes:

| Problem | Quick Fix |
|---------|-----------|
| `ModuleNotFoundError: viz_pipeline` | `conda activate vizpipeline` then Kernel → Change kernel → vizpipeline |
| Jupyter doesn't open | Copy URL from Terminal → paste in browser |
| Slow pipeline | Use smaller df or set `enable_sampling=True` |
| ImportError | Navigate to VizPipeline folder, run `pip install -e ".[dev]"` again |

---

## 🚀 GIT DEPLOYMENT - 10 MINUTE SETUP

### ✅ Push to GitHub (If Git Already Connected):

```bash
# Terminal in VizPipeline folder

# 1. Initialize git (first time only)
git init

# 2. Add files
git add .

# 3. First commit
git commit -m "Initial commit: VizPipeline v0.1.0 Alpha

- Phase 1: Infrastructure (types, config, logging)
- Phase 2: Full orchestration (7 tools)
- Complete documentation
- Ready for production"

# 4. On GitHub.com: Create new repository "viz-pipeline"
# (Don't init with README/gitignore - you already have them!)

# 5. Connect local to GitHub
git remote add origin https://github.com/YourUsername/viz-pipeline.git

# 6. Push
git push -u origin master

# 7. Done! Check github.com/YourUsername/viz-pipeline
```

### 📋 .gitignore Content (Create in root):

```
# Save as: .gitignore (in VizPipeline root)

__pycache__/
*.py[cod]
*.so
build/
dist/
*.egg-info/
venv/
ENV/
env/
.venv
.vscode/
.idea/
.ipynb_checkpoints/
.coverage
htmlcov/
data/
*.csv
```

### 📝 Regular Updates:

```bash
# After you make changes:
git status          # See what changed
git add .           # Stage all
git commit -m "Your message"
git push            # Push to GitHub
```

### 🔧 Troubleshooting Quick Fixes:

| Problem | Quick Fix |
|---------|-----------|
| "not a git repository" | Run `git init` in project folder |
| "could not read Username" | Create GitHub token: github.com/settings/tokens → use as password |
| "no upstream branch" | Use `git push -u origin master` (first time) |
| Wrong commit message | `git reset --soft HEAD~1` → redo commit |

---

## ✅ COMPLETE CHECKLIST (Both)

### Anaconda Setup
- [ ] `conda --version` works
- [ ] Created environment: `conda create -n vizpipeline python=3.11`
- [ ] Activated environment: `conda activate vizpipeline`
- [ ] Navigated to VizPipeline: `cd /path/to/VizPipeline`
- [ ] Installed: `pip install -e ".[dev]"`
- [ ] Test passed: `python -c "from viz_pipeline import VizPipeline"`
- [ ] Jupyter running: `jupyter notebook`
- [ ] Browser opened: http://localhost:8888

### Git Deployment
- [ ] `git --version` works
- [ ] Configured user: `git config --global user.name "..."`
- [ ] `.gitignore` created
- [ ] Repo initialized: `git init`
- [ ] Files staged: `git add .`
- [ ] First commit: `git commit -m "..."`
- [ ] GitHub repo created
- [ ] Remote added: `git remote add origin https://...`
- [ ] Pushed: `git push -u origin master`
- [ ] GitHub shows files ✅

---

## 📞 WHEN YOU GET STUCK

### Quick Diagnostics:

```bash
# Check Anaconda environment
conda info
conda list viz-pipeline

# Check Git status
git status
git log
git remote -v

# Check VizPipeline installation
python -c "import viz_pipeline; print(viz_pipeline.__version__)"

# Check Python version
python --version
```

### Get Help:

1. **Read Error Message** - Usually very helpful!
2. **Check Logs** - Terminal shows what went wrong
3. **Google Error** - Copy exact error message
4. **Check Docs** - ANACONDA_JUPYTER_SETUP_GUIDE.md or GIT_DEPLOYMENT_GUIDE.md
5. **Ask Team** - Share error + what you were doing

---

## 🎉 YOU'RE DONE WHEN:

✅ Jupyter Notebook runs with VizPipeline imported  
✅ You can execute: `report = VizPipeline.run(df)`  
✅ GitHub shows your code at `github.com/YourUsername/viz-pipeline`  

**That's it! You're ready to use VizPipeline! 🚀**

---

## 📚 DETAILED GUIDES

For more info:
- **ANACONDA_JUPYTER_SETUP_GUIDE.md** - Full setup guide
- **GIT_DEPLOYMENT_GUIDE.md** - Full git guide
- **JUPYTER_INTEGRATION_GUIDE.md** - How to use VizPipeline in notebooks

---

## ⏱️ TIME ESTIMATE

| Task | Time |
|------|------|
| Anaconda environment setup | 5 min |
| VizPipeline installation | 2 min |
| First notebook test | 5 min |
| Git initialization | 3 min |
| First GitHub push | 2 min |
| **TOTAL** | **~17 minutes** |

---

**Ready? Start with the checklist! Follow step by step. You've got this! 💪**
