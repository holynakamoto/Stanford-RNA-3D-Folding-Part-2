#!/usr/bin/env python3
"""
Add missing functions to the RhoFold notebook that are needed for submission.
"""

import json

notebook_path = "main_rhofold_integrated.ipynb"

print("Adding missing functions to notebook...")

# Load notebook
with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Add missing constants and functions
missing_functions_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# ============================================================================\n",
        "# MISSING FUNCTIONS - Added for Submission\n",
        "# ============================================================================\n",
        "\n",
        "# Submission columns (required format)\n",
        "SUBMISSION_COLUMNS = [\n",
        "    'ID', 'resname', 'resid',\n",
        "    'x_1', 'y_1', 'z_1', 'x_2', 'y_2', 'z_2',\n",
        "    'x_3', 'y_3', 'z_3', 'x_4', 'y_4', 'z_4',\n",
        "    'x_5', 'y_5', 'z_5'\n",
        "]\n",
        "\n",
        "def center_coordinates(coords: np.ndarray) -> np.ndarray:\n",
        "    \"\"\"\n",
        "    Center coordinates by subtracting the centroid.\n",
        "    \n",
        "    Args:\n",
        "        coords: (L, 3) array\n",
        "    Returns:\n",
        "        Centered coords (L, 3)\n",
        "    \"\"\"\n",
        "    centroid = np.mean(coords, axis=0, keepdims=True)\n",
        "    return coords - centroid\n",
        "\n",
        "def backbone_distance_stats(coords: np.ndarray) -> tuple:\n",
        "    \"\"\"\n",
        "    Calculate backbone distance statistics.\n",
        "    \n",
        "    Args:\n",
        "        coords: (L, 3) coordinates\n",
        "    Returns:\n",
        "        (mean, std) of consecutive residue distances\n",
        "    \"\"\"\n",
        "    if len(coords) < 2:\n",
        "        return 0.0, 0.0\n",
        "    diffs = coords[1:] - coords[:-1]\n",
        "    distances = np.sqrt(np.sum(diffs**2, axis=1))\n",
        "    return float(np.mean(distances)), float(np.std(distances))\n",
        "\n",
        "def build_submission_dataframe(sequences_df, predictions, center=True):\n",
        "    \"\"\"\n",
        "    Build submission DataFrame from predictions.\n",
        "    \n",
        "    Args:\n",
        "        sequences_df: DataFrame with target_id and sequence\n",
        "        predictions: dict[target_id] -> coords (L, K, 3)\n",
        "        center: Whether to center coordinates\n",
        "    Returns:\n",
        "        DataFrame with SUBMISSION_COLUMNS\n",
        "    \"\"\"\n",
        "    rows = []\n",
        "    for _, row in sequences_df.iterrows():\n",
        "        target_id = row['target_id']\n",
        "        sequence = row['sequence']\n",
        "        coords = predictions[target_id]  # (L, K, 3)\n",
        "        L, K, _ = coords.shape\n",
        "        assert K == 5, f\"Expected 5 conformations, got {K} for {target_id}\"\n",
        "\n",
        "        # Post-process per conformation\n",
        "        proc = np.empty_like(coords)\n",
        "        for k in range(K):\n",
        "            c = coords[:, k, :]\n",
        "            if center:\n",
        "                c = center_coordinates(c)\n",
        "            proc[:, k, :] = c\n",
        "\n",
        "        for i, base in enumerate(sequence, start=1):\n",
        "            entry = {\n",
        "                'ID': f\"{target_id}_{i}\",\n",
        "                'resname': base.upper(),\n",
        "                'resid': i,\n",
        "            }\n",
        "            for k in range(K):\n",
        "                entry[f'x_{k+1}'] = float(proc[i-1, k, 0])\n",
        "                entry[f'y_{k+1}'] = float(proc[i-1, k, 1])\n",
        "                entry[f'z_{k+1}'] = float(proc[i-1, k, 2])\n",
        "            rows.append(entry)\n",
        "    df = pd.DataFrame(rows, columns=SUBMISSION_COLUMNS)\n",
        "    return df\n",
        "\n",
        "print(\"✅ Missing functions added successfully!\")\n",
        "print(f\"Available functions: SUBMISSION_COLUMNS, center_coordinates, backbone_distance_stats, build_submission_dataframe\")"
    ]
}

# Insert after Cell 1 (installation) and before Cell 2 (data loading)
nb['cells'].insert(2, missing_functions_cell)

print("✓ Added missing functions cell")

# Save notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Notebook updated: {notebook_path}")
print("\nAdded:")
print("  ✓ SUBMISSION_COLUMNS constant")
print("  ✓ center_coordinates() function")
print("  ✓ backbone_distance_stats() function")
print("  ✓ build_submission_dataframe() function")
print("\nThis should fix the NameError!")
