#!/usr/bin/env python3
"""
Fix the notebook to use test_sequences instead of validation_sequences for competition submission.
"""

import json

notebook_path = "main_offline_ready.ipynb"

print("Fixing notebook to use test_sequences for competition submission...")

# Load notebook
with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Find the data loading cell
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'TARGET_SEQS = validation_seqs' in source:
            print(f"Found target selection in cell {i}")

            # Replace validation_seqs with test_seqs
            old_source = source
            new_source = source.replace(
                'TARGET_SEQS = validation_seqs  # Change to test_seqs for submission',
                'TARGET_SEQS = test_seqs  # Using test sequences for competition submission'
            )

            if new_source != old_source:
                nb['cells'][i]['source'] = new_source.split('\n')
                print("✅ Changed TARGET_SEQS from validation_seqs to test_seqs")
                break

# Save the fixed notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Notebook updated: {notebook_path}")
print("\nKey fix:")
print("  ✓ TARGET_SEQS = test_seqs (instead of validation_seqs)")
print("  ✓ Will now generate predictions for the full test set")
print("  ✓ Submission will have correct number of rows")
print("\nThis should fix the 'incorrect format' error!")
print("The validation submission had only 30 rows, but test set needs thousands of rows.")