#!/usr/bin/env python3
"""Prepare notebook for Kaggle submission by cleaning local references"""

import json
import sys

notebook_path = "main_kaggle_submission.ipynb"

# Load notebook
with open(notebook_path, 'r') as f:
    nb = json.load(f)

print(f"Cleaning notebook: {notebook_path}")
print(f"Total cells: {len(nb['cells'])}")

changes_made = 0

# Clean each cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        # Clean source code
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        original = source
        
        # Remove local path references
        source = source.replace('/Users/nickmoore/kagglecomp/', '')
        source = source.replace('  Full path: /Users/nickmoore/kagglecomp/submission.csv', 
                               '  Working directory: {os.getcwd()}')
        
        # Update cell source
        if source != original:
            cell['source'] = source.split('\n')
            # Keep newlines except for last line
            cell['source'] = [line + '\n' if i < len(cell['source'])-1 else line 
                             for i, line in enumerate(cell['source'])]
            changes_made += 1
            print(f"  Cleaned cell {i}")
        
        # Clear outputs for submission (optional but cleaner)
        if 'outputs' in cell:
            cell['outputs'] = []
        if 'execution_count' in cell:
            cell['execution_count'] = None

print(f"\nChanges made: {changes_made} cells")

# Save cleaned notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"✓ Saved: {notebook_path}")
print("\nNotebook is ready for Kaggle submission!")
print("\nNext steps:")
print("1. Go to: https://www.kaggle.com/competitions/stanford-rna-3d-folding")
print("2. Click 'Code' → 'New Notebook'")
print("3. Upload main_kaggle_submission.ipynb")
print("4. Click 'Run' (or 'Submit')")
print("5. Wait for submission.csv to be generated")
print("6. Check your score on the leaderboard!")
