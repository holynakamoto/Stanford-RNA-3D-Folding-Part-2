# Environment Setup Guide

## Recommended: Virtual Environment Setup

For best results, use a project-specific virtual environment to avoid conflicts with system Python installations.

### Initial Setup

```bash
# Navigate to project directory
cd /Users/nickmoore/kagglecomp

# Create virtual environment with Python 3.14.2 (or your preferred version)
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install ipykernel for Jupyter support
pip install ipykernel

# (Optional) Install Jupyter for local development
pip install jupyter jupyterlab
```

### VS Code Configuration

1. **Select the virtual environment interpreter**:
   - Open Command Palette (Cmd+Shift+P on macOS, Ctrl+Shift+P on Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows)

2. **Reload VS Code**:
   - Command Palette → "Developer: Reload Window"

3. **Select kernel in notebook**:
   - Open `main.ipynb`
   - Click kernel picker (top-right)
   - Select "Python Environments" → `.venv` or the Python 3.x option that shows your venv path

### Verify Installation

Run this in a notebook cell:
```python
import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")

# Test imports
import numpy as np
import pandas as pd
import ipykernel
print(f"ipykernel version: {ipykernel.__version__}")
print("✓ All imports successful!")
```

## Alternative: Global Installation

If you prefer not to use a virtual environment:

```bash
# Install ipykernel globally
python3 -m pip install ipykernel -U --force-reinstall --user

# In VS Code, select your system Python interpreter
# Command Palette → "Python: Select Interpreter" → Choose system Python 3.14.2
```

## Troubleshooting

### VS Code still shows "ipykernel not installed"

1. **Check interpreter selection**:
   - Bottom-left status bar should show the correct Python path
   - If not, use Command Palette → "Python: Select Interpreter"

2. **Force VS Code refresh**:
   - Command Palette → "Developer: Reload Window"
   - Or quit and reopen VS Code

3. **Manual kernel installation**:
   ```bash
   # With venv activated
   python -m ipykernel install --user --name=kagglecomp --display-name "Python (kagglecomp)"
   ```
   Then select this kernel in the notebook.

### Permission Errors

If you get permission errors, use `--user` flag:
```bash
pip install --user ipykernel
```

### Multiple Python Versions

If you have multiple Python installations:
```bash
# Check which Python is being used
which python3
python3 --version

# Use specific Python for venv
/opt/homebrew/bin/python3 -m venv .venv  # macOS Homebrew
# OR
/usr/bin/python3 -m venv .venv            # System Python
```

## Testing the Setup

After setup, test with the local test script:

```bash
# Activate venv first
source .venv/bin/activate

# Run local test
python test_locally.py
```

This should generate a `submission.csv` file with sample predictions.
