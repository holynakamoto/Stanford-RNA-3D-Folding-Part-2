#!/usr/bin/env python3
"""
Add the missing save_submission and clip_coordinates functions to the notebook.
"""

import json

notebook_path = "main_rhofold_integrated.ipynb"

print("Adding save_submission and clip_coordinates functions...")

# Load notebook
with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Add the missing functions to Cell 2 (missing functions cell)
save_functions = """

def clip_coordinates(coords):
    \"\"\"
    Clip coordinates to valid range [-999.999, 9999.999] as required by competition.

    Args:
        coords: Array of coordinates (N, 3) or (3,)

    Returns:
        Clipped coordinates
    \"\"\"
    coords = np.clip(coords, -999.999, 9999.999)
    return coords

def save_submission(predictions_df, output_path="submission.csv"):
    \"\"\"
    Save predictions to submission CSV file.

    Args:
        predictions_df: DataFrame with predictions in submission format
        output_path: Path to save the submission file
    \"\"\"
    # Clip coordinates to valid range before saving
    coord_cols = [col for col in predictions_df.columns if col.startswith(('x_', 'y_', 'z_'))]
    for col in coord_cols:
        predictions_df[col] = clip_coordinates(predictions_df[col].values)

    # Create directory if it doesn't exist (for local development)
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")

    predictions_df.to_csv(output_path, index=False)
    print(f"Saving submission to: {output_path}")
    print(f"Shape: {predictions_df.shape}")
    print(f"Columns: {list(predictions_df.columns)}")

print("✅ Additional functions added successfully!")
print(f"Available functions: clip_coordinates, save_submission")
"""

# Find the missing functions cell (Cell 2) and add the new functions
if len(nb['cells']) > 2:
    existing_source = ''.join(nb['cells'][2]['source']) if isinstance(nb['cells'][2]['source'], list) else nb['cells'][2]['source']

    # Add the new functions to the end of Cell 2
    new_source = existing_source + "\n\n" + save_functions
    nb['cells'][2]['source'] = new_source.split('\n')

print("✓ Added save_submission and clip_coordinates functions")

# Save notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Notebook updated: {notebook_path}")
print("\nAdded:")
print("  ✓ clip_coordinates() function")
print("  ✓ save_submission() function")
print("  ✓ Coordinate clipping to valid ranges")
print("  ✓ CSV saving with proper formatting")
print("\nThis should fix the final NameError!")
