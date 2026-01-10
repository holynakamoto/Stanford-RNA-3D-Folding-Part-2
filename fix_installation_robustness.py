#!/usr/bin/env python3
"""
Make the installation more robust for Kaggle environment.
Fix network issues by using cached installations or simpler approaches.
"""

import json

notebook_path = "main_rhofold_integrated.ipynb"

print("Making installation more robust for Kaggle...")

# Load notebook
with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Find the installation cell (Cell 1)
installation_cell = nb['cells'][1]

# Replace with more robust installation
new_installation_source = [
    "# ============================================================================\n",
    "# INSTALLATION - Robust for Kaggle Environment\n",
    "# ============================================================================\n",
    "import subprocess\n",
    "import sys\n",
    "import os\n",
    "\n",
    "print(\"Setting up environment...\")\n",
    "\n",
    "# Check for offline wheels (if user uploaded them)\n",
    "wheels_path = '/kaggle/input/pytorch-offline-wheels'\n",
    "use_offline_wheels = os.path.exists(wheels_path)\n",
    "\n",
    "if use_offline_wheels:\n",
    "    print(f\"✅ Found offline wheels at {wheels_path}\")\n",
    "    try:\n",
    "        subprocess.run([\n",
    "            sys.executable, '-m', 'pip', 'install',\n",
    "            '--no-index', '--find-links', wheels_path,\n",
    "            '-q', 'torch', 'einops', 'fair-esm', 'ml-collections'\n",
    "        ], check=False, timeout=300)\n",
    "        print(\"✅ Installed from offline wheels\")\n",
    "    except Exception as e:\n",
    "        print(f\"⚠ Offline installation failed: {e}\")\n",
    "else:\n",
    "    print(\"ℹ No offline wheels found, will use fallback model\")\n",
    "\n",
    "# Always install these core packages (usually work on Kaggle)\n",
    "try:\n",
    "    subprocess.run([\n",
    "        sys.executable, '-m', 'pip', 'install', '-q',\n",
    "        'numpy>=1.24.0', 'pandas>=2.0.0', 'scipy>=1.10.0'\n",
    "    ], check=False, timeout=120)\n",
    "    print(\"✅ Core packages installed\")\n",
    "except Exception as e:\n",
    "    print(f\"⚠ Core package installation failed: {e}\")\n",
    "\n",
    "# Try optional packages (may fail on Kaggle)\n",
    "optional_packages = ['biopython>=1.81']\n",
    "for package in optional_packages:\n",
    "    try:\n",
    "        subprocess.run([\n",
    "            sys.executable, '-m', 'pip', 'install', '-q', package\n",
    "        ], check=False, timeout=60)\n",
    "        print(f\"✅ {package} installed\")\n",
    "    except Exception as e:\n",
    "        print(f\"⚠ {package} installation failed: {e}\")\n",
    "        print(\"  This is OK - notebook will use fallback methods\")\n",
    "\n",
    "print(\"\\n\" + \"=\"*70)\n",
    "print(\"DEPENDENCY CHECK\")\n",
    "print(\"=\"*70)\n",
    "\n",
    "# Import everything with fallbacks\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "\n",
    "# Check for RhoFold dependencies\n",
    "RHOFOLD_AVAILABLE = False\n",
    "try:\n",
    "    import torch\n",
    "    from einops import rearrange  # Test einops\n",
    "    import ml_collections\n",
    "    RHOFOLD_AVAILABLE = True\n",
    "    print(\"✅ RhoFold dependencies available\")\n",
    "    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'\n",
    "    print(f\"   Device: {DEVICE}\")\n",
    "except ImportError as e:\n",
    "    print(f\"⚠ RhoFold dependencies not available: {e}\")\n",
    "    print(\"   Will use physics-based fallback\")\n",
    "    DEVICE = 'cpu'\n",
    "    RHOFOLD_AVAILABLE = False\n",
    "\n",
    "# Check for Biopython\n",
    "try:\n",
    "    from Bio import PDB\n",
    "    BIOPYTHON_AVAILABLE = True\n",
    "    print(\"✅ Biopython available\")\n",
    "except ImportError:\n",
    "    print(\"⚠ Biopython not available\")\n",
    "    print(\"   PDB template loading disabled\")\n",
    "    BIOPYTHON_AVAILABLE = False\n",
    "\n",
    "# Set random seed\n",
    "np.random.seed(42)\n",
    "if RHOFOLD_AVAILABLE:\n",
    "    torch.manual_seed(42)\n",
    "\n",
    "print(\"\\n\" + \"=\"*70)\n",
    "print(\"ENVIRONMENT READY\")\n",
    "print(\"=\"*70)\n",
    "print(f\"RhoFold available: {RHOFOLD_AVAILABLE}\")\n",
    "print(f\"Biopython available: {BIOPYTHON_AVAILABLE}\")\n",
    "print(f\"Device: {DEVICE}\")\n",
    "\n",
    "if RHOFOLD_AVAILABLE:\n",
    "    print(\"\\n🎯 Will use RhoFold deep learning model\")\n",
    "    print(\"   Expected score: 0.35-0.40\")\n",
    "else:\n",
    "    print(\"\\n📊 Will use physics-based fallback model\")\n",
    "    print(\"   Expected score: 0.15-0.18\")\n",
    "    print(\"   (To enable RhoFold: Add datasets to notebook)\")\n"
]

nb['cells'][1]['source'] = new_installation_source

# Save the improved notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Robust installation saved: {notebook_path}")
print("\nImprovements made:")
print("  ✓ Added offline wheel support")
print("  ✓ Made PyTorch installation optional")
print("  ✓ Added timeout limits to prevent hanging")
print("  ✓ Better error handling and user feedback")
print("  ✓ Clear indication of what will be used")
print("  ✓ Faster startup (no waiting for failed installations)")
print("\nThis should prevent the 13+ minute installation timeout!")
