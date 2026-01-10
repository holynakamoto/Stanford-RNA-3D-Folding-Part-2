#!/usr/bin/env python3
"""
Debug submission format issues.
Check for common problems that cause Kaggle scoring errors.
"""

import pandas as pd
import numpy as np

def debug_submission_format(submission_df):
    """Check submission for common format issues."""

    print("🔍 DEBUGGING SUBMISSION FORMAT")
    print("="*50)

    # 1. Check basic structure
    print(f"Shape: {submission_df.shape}")
    print(f"Columns: {list(submission_df.columns)}")
    print(f"Data types:\\n{submission_df.dtypes}")

    # 2. Check required columns
    required_cols = ['ID', 'resname', 'resid'] + \
                   [f'{coord}_{i}' for i in range(1, 6) for coord in ['x', 'y', 'z']]

    missing_cols = [col for col in required_cols if col not in submission_df.columns]
    if missing_cols:
        print(f"❌ MISSING COLUMNS: {missing_cols}")
        return False
    else:
        print("✅ All required columns present")

    # 3. Check column order
    actual_cols = list(submission_df.columns)
    if actual_cols != required_cols:
        print(f"❌ WRONG COLUMN ORDER:")
        print(f"  Expected: {required_cols}")
        print(f"  Actual:   {actual_cols}")
        return False
    else:
        print("✅ Column order is correct")

    # 4. Check for NaN values
    nan_counts = submission_df.isnull().sum()
    total_nans = nan_counts.sum()
    if total_nans > 0:
        print(f"❌ FOUND NaN VALUES: {total_nans} total")
        print(f"  Breakdown:\\n{nan_counts[nan_counts > 0]}")
        return False
    else:
        print("✅ No NaN values found")

    # 5. Check data types
    expected_dtypes = {
        'ID': 'object',
        'resname': 'object',
        'resid': 'int64'
    }

    for coord in ['x', 'y', 'z']:
        for i in range(1, 6):
            col = f'{coord}_{i}'
            expected_dtypes[col] = 'float64'

    wrong_dtypes = []
    for col, expected_dtype in expected_dtypes.items():
        actual_dtype = str(submission_df[col].dtype)
        if actual_dtype != expected_dtype:
            wrong_dtypes.append(f"{col}: {actual_dtype} → {expected_dtype}")

    if wrong_dtypes:
        print(f"❌ WRONG DATA TYPES:")
        for dtype_issue in wrong_dtypes:
            print(f"  {dtype_issue}")
        return False
    else:
        print("✅ All data types correct")

    # 6. Check coordinate ranges
    coord_cols = [col for col in submission_df.columns if col.startswith(('x_', 'y_', 'z_'))]
    min_vals = submission_df[coord_cols].min()
    max_vals = submission_df[coord_cols].max()

    out_of_range = []
    for col in coord_cols:
        min_val = min_vals[col]
        max_val = max_vals[col]
        if min_val < -999.999 or max_val > 9999.999:
            out_of_range.append(f"{col}: [{min_val:.2f}, {max_val:.2f}]")

    if out_of_range:
        print(f"❌ COORDINATES OUT OF RANGE [-999.999, 9999.999]:")
        for issue in out_of_range:
            print(f"  {issue}")
        return False
    else:
        print("✅ All coordinates within valid range")

    # 7. Check ID format
    # Correct format for this competition: target_chain_residue (e.g., 1ABC_A_1)
    id_format_ok = submission_df['ID'].str.match(r'^[^_]+_[^_]+_\d+$').all()
    if not id_format_ok:
        bad_ids = submission_df[~submission_df['ID'].str.match(r'^[^_]+_[^_]+_\d+$')]['ID'].head(5).tolist()
        print(f"❌ INVALID ID FORMAT (should be 'target_chain_residue'): {bad_ids}")
        return False
    else:
        print("✅ ID format is correct (target_chain_residue)")

    # 8. Check resname values
    valid_bases = {'A', 'C', 'G', 'U'}
    invalid_resnames = set(submission_df['resname'].unique()) - valid_bases
    if invalid_resnames:
        print(f"❌ INVALID RESNAMES (should be A,C,G,U): {invalid_resnames}")
        return False
    else:
        print("✅ All resnames are valid RNA bases")

    # 9. Check resid values
    min_resid = submission_df['resid'].min()
    max_resid = submission_df['resid'].max()
    if min_resid < 1:
        print(f"❌ INVALID RESID VALUES (should start from 1): min={min_resid}")
        return False
    else:
        print(f"✅ Resid values valid (1 to {max_resid})")

    # 10. Sample output
    print("\\n📊 SAMPLE OUTPUT:")
    print(submission_df.head(3))

    print("\\n✅ ALL CHECKS PASSED - Submission format is valid!")
    return True

if __name__ == "__main__":
    # Try to load submission.csv if it exists
    try:
        submission_df = pd.read_csv('submission.csv')
        debug_submission_format(submission_df)
    except FileNotFoundError:
        print("❌ submission.csv not found - run the notebook first")
    except Exception as e:
        print(f"❌ Error loading submission: {e}")