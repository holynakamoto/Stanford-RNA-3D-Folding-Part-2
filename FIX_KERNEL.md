# Fixing "ModuleNotFoundError" in VS Code

If you're seeing `ModuleNotFoundError: No module named 'numpy'`, the notebook is not using your virtual environment.

## Quick Fix

### Option 1: Select the Virtual Environment Kernel (Recommended)

1. **Open the notebook** (`main.ipynb`)

2. **Click the kernel selector** (top-right corner of the notebook, shows current kernel)

3. **Select "Select Another Kernel"** or click the kernel name

4. **Choose one of these**:
   - **"Python Environments"** → Select `.venv` (should show path like `/Users/nickmoore/kagglecomp/.venv/bin/python`)
   - **"Python 3.9.6 ('venv': venv) .venv"** or similar

5. **Verify it worked**: Run this in a cell:
   ```python
   import sys
   print(sys.executable)  # Should show .venv/bin/python
   ```

### Option 2: Select Python Interpreter First

1. **Open Command Palette**: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)

2. **Type**: "Python: Select Interpreter"

3. **Choose**: `.venv/bin/python` (should be listed)

4. **Reload VS Code**: Command Palette → "Developer: Reload Window"

5. **Open notebook** and select the kernel (should now default to `.venv`)

### Option 3: Install Packages in Current Environment

If you want to use a different Python environment, install packages there:

```bash
# Activate your desired environment first, then:
pip install -r requirements.txt
```

## Verify Installation

Run this cell to check everything is working:

```python
import sys
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}")

# Test imports
import numpy as np
import pandas as pd
import torch
print(f"✓ numpy {np.__version__}")
print(f"✓ pandas {pd.__version__}")
print(f"✓ torch {torch.__version__}")
```

## Common Issues

### "Kernel not found" or "No kernel available"

1. Make sure `.venv` exists: `ls -la .venv`
2. Install ipykernel in the venv:
   ```bash
   source .venv/bin/activate
   pip install ipykernel
   ```
3. Register the kernel:
   ```bash
   python -m ipykernel install --user --name=kagglecomp --display-name "Python (kagglecomp)"
   ```
4. Select "kagglecomp" kernel in the notebook

### Still seeing errors?

1. **Check which Python is being used**:
   ```python
   import sys
   print(sys.executable)
   ```
   Should show: `/Users/nickmoore/kagglecomp/.venv/bin/python`

2. **If it shows a different path**, the kernel selection didn't work. Try:
   - Close and reopen VS Code
   - Delete `.ipynb_checkpoints` folder if it exists
   - Restart VS Code

3. **Verify packages are installed**:
   ```bash
   source .venv/bin/activate
   pip list | grep numpy
   ```

## For Kaggle Submissions

When submitting to Kaggle, the notebook will run in Kaggle's environment. The `!pip install` line in the first cell will install packages there. For local development, use the virtual environment.
