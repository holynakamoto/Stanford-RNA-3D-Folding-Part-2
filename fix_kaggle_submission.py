#!/usr/bin/env python3
"""
Fix the Kaggle submission error by correcting the function name and ensuring proper submission generation.
"""

import json

notebook_path = "main_rhofold_integrated.ipynb"

print("Fixing Kaggle submission error...")

# Load notebook
with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Find the cell that calls generate_submission_template
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'generate_submission_template' in source:
            print(f"Found the problematic cell {i}")

            # Replace with correct submission generation
            new_source = [
                "# Generate predictions for all test sequences\n",
                "print(\"Generating predictions for all test sequences...\")\n",
                "print(f\"Total sequences: {len(test_sequences)}\")\n",
                "\n",
                "# Initialize predictions dictionary\n",
                "predictions = {}\n",
                "total_processed = 0\n",
                "\n",
                "# Process each sequence\n",
                "for idx, row in test_sequences.iterrows():\n",
                "    target_id = row['target_id']\n",
                "    sequence = row['sequence']\n",
                "    \n",
                "    if idx % 5 == 0:  # Progress every 5 sequences\n",
                "        print(f\"  Processing {idx+1}/{len(test_sequences)}: {target_id} ({len(sequence)}nt)\")\n",
                "    \n",
                "    # Generate 5 predictions for this sequence\n",
                "    coords_list = []\n",
                "    for pred_num in range(5):\n",
                "        coords = predict_rna_structure(sequence, pred_num + 1)\n",
                "        coords_list.append(coords)\n",
                "    \n",
                "    # Stack into array shape (L, 5, 3)\n",
                "    coords_array = np.stack(coords_list, axis=1)  # (L, 5, 3)\n",
                "    predictions[target_id] = coords_array\n",
                "    total_processed += 1\n",
                "\n",
                "print(f\"\\n✅ Generated predictions for {total_processed} sequences\")\n",
                "print(f\"Total predictions: {sum(len(preds) for preds in predictions.values())} coordinates\")\n",
                "\n",
                "# Build submission dataframe\n",
                "print(\"\\nBuilding submission dataframe...\")\n",
                "submission_df = build_submission_dataframe(test_sequences, predictions, center=True)\n",
                "print(f\"Submission dataframe shape: {submission_df.shape}\")\n",
                "print(f\"Columns: {list(submission_df.columns)}\")\n"
            ]

            nb['cells'][i]['source'] = new_source
            print("✓ Fixed submission generation cell")
            break

# Save fixed notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Fixed notebook saved: {notebook_path}")
print("\nChanges made:")
print("  ✓ Replaced 'generate_submission_template()' with proper prediction loop")
print("  ✓ Added progress tracking")
print("  ✓ Fixed function call to 'build_submission_dataframe'")
print("  ✓ Ensured proper coordinate formatting")
print("\nThis should fix the NameError and allow the notebook to run successfully on Kaggle!")
