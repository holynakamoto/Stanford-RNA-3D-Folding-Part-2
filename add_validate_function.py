#!/usr/bin/env python3
"""
Add the missing validate_submission function to the notebook.
"""

import json

notebook_path = "main_rhofold_integrated.ipynb"

print("Adding validate_submission function...")

# Load notebook
with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Add validate_submission function to the missing functions cell (Cell 2)
validate_function = """
def validate_submission(submission_df, sequences_df):
    \"\"\"
    Validate that submission has correct format and all sequences are present.

    Args:
        submission_df: Submission DataFrame
        sequences_df: Test sequences DataFrame (with target_id and sequence columns)

    Returns:
        True if valid, raises error if invalid
    \"\"\"
    # Check required columns
    required_cols = SUBMISSION_COLUMNS
    missing_cols = [col for col in required_cols if col not in submission_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Check coordinate ranges
    coord_cols = [col for col in submission_df.columns if col.startswith(('x_', 'y_', 'z_'))]
    for col in coord_cols:
        min_val = submission_df[col].min()
        max_val = submission_df[col].max()
        if min_val < -999.999 or max_val > 9999.999:
            print(f"Warning: {col} has values outside valid range [-999.999, 9999.999]")
            print(f"  Min: {min_val}, Max: {max_val}")

    # Check all sequences have predictions
    for _, row in sequences_df.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        seq_length = len(sequence)

        # Check that we have predictions for all residues
        expected_ids = [f"{target_id}_{i}" for i in range(1, seq_length + 1)]

        for expected_id in expected_ids:
            seq_rows = submission_df[submission_df['ID'] == expected_id]
            if len(seq_rows) == 0:
                raise ValueError(f"No predictions found for {expected_id}")

            # Check that coordinates are not all zeros (basic validation)
            for pred_num in range(1, 6):
                x_col = f'x_{pred_num}'
                y_col = f'y_{pred_num}'
                z_col = f'z_{pred_num}'
                coords = seq_rows[[x_col, y_col, z_col]].values[0]
                if np.allclose(coords, 0):
                    print(f"Warning: Prediction {pred_num} for {expected_id} contains all zeros")

    print("✅ Submission validation passed!")
    return True
"""

# Find the missing functions cell (Cell 2) and add validate_submission
if len(nb['cells']) > 2:
    existing_source = ''.join(nb['cells'][2]['source']) if isinstance(nb['cells'][2]['source'], list) else nb['cells'][2]['source']

    # Add validate_submission to the end of Cell 2
    new_source = existing_source + "\n\n" + validate_function
    nb['cells'][2]['source'] = new_source.split('\n')

print("✓ Added validate_submission function")

# Save notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Notebook updated: {notebook_path}")
print("\nAdded:")
print("  ✓ validate_submission() function")
print("  ✓ Checks required columns")
print("  ✓ Validates coordinate ranges")
print("  ✓ Ensures all sequences have predictions")
print("  ✓ Checks for zero coordinates")
print("\nThis should fix the NameError!")
