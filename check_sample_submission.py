#!/usr/bin/env python3
"""
Check what the correct submission format should be by examining sample data.
"""

import pandas as pd
import os

# Check if we can load sample submission
sample_path = '/kaggle/input/stanford-rna-3d-folding/sample_submission.csv'
if os.path.exists(sample_path):
    print("Loading sample submission...")
    sample_df = pd.read_csv(sample_path)
    print(f"Sample shape: {sample_df.shape}")
    print(f"Sample columns: {list(sample_df.columns)}")
    print(f"First few IDs: {sample_df['ID'].head(5).tolist()}")

    # Check ID format
    first_id = sample_df['ID'].iloc[0]
    print(f"Sample ID format: {first_id}")
    print(f"ID pattern: {first_id.split('_')}")
else:
    print("Sample submission not available locally")

# Check our current submission
print("\\nOur current submission:")
submission_df = pd.read_csv('submission.csv')
print(f"Our shape: {submission_df.shape}")
print(f"Our columns: {list(submission_df.columns)}")
print(f"Our first few IDs: {submission_df['ID'].head(5).tolist()}")

first_id = submission_df['ID'].iloc[0]
print(f"Our ID format: {first_id}")
print(f"Our ID pattern: {first_id.split('_')}")

# Test the regex pattern
import re
pattern = r'^[^_]+_\d+$'
test_ids = submission_df['ID'].head(5).tolist()
print(f"\\nTesting regex pattern: {pattern}")
for test_id in test_ids:
    match = re.match(pattern, test_id)
    print(f"  {test_id}: {'✓' if match else '✗'}")

# What should the pattern be?
print("\\nCorrect pattern should be: target_chain_residue")
print("Example: 1ABC_A_1 (target=1ABC, chain=A, residue=1)")