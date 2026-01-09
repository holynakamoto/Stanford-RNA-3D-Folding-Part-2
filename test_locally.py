"""
Local testing script for RNA structure prediction.
This allows you to test your model locally before submitting to Kaggle.
"""

import pandas as pd
import sys
from utils import (
    read_test_sequences,
    generate_submission_template,
    save_submission,
    validate_submission
)
import numpy as np


def predict_rna_structure(sequence: str, prediction_number: int) -> np.ndarray:
    """
    Predict 3D structure coordinates for an RNA sequence.
    
    This is a placeholder - replace with your actual model.
    """
    sequence_length = len(sequence)
    np.random.seed(hash(sequence) % 2**32 + prediction_number)
    
    # Simple random walk starting from origin
    coords = np.zeros((sequence_length, 3))
    # Start from a random initial position to avoid all zeros
    coords[0] = np.random.normal(0, 2.0, 3)
    for i in range(1, sequence_length):
        coords[i] = coords[i-1] + np.random.normal(0, 2.5, 3)
    
    return coords


def main():
    """Main function to generate predictions locally."""
    print("Loading test sequences...")
    test_sequences = read_test_sequences("sample_test_sequences.csv")
    print(f"Loaded {len(test_sequences)} sequences")
    
    print("\nGenerating submission template...")
    submission_df = generate_submission_template(test_sequences)
    
    print("\nGenerating predictions...")
    for idx, row in test_sequences.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        
        for pred_num in range(1, 6):
            coords = predict_rna_structure(sequence, pred_num)
            
            # Update coordinates with correct ID format: target_id_resid
            submission_ids = [f"{target_id}_{resid}" for resid in range(1, len(sequence) + 1)]
            mask = submission_df['ID'].isin(submission_ids)
            
            for i, submission_id in enumerate(submission_ids):
                row_mask = (submission_df['ID'] == submission_id) & mask
                if row_mask.sum() > 0:
                    submission_df.loc[row_mask, f'x_{pred_num}'] = coords[i, 0]
                    submission_df.loc[row_mask, f'y_{pred_num}'] = coords[i, 1]
                    submission_df.loc[row_mask, f'z_{pred_num}'] = coords[i, 2]
        
        print(f"  Processed {target_id}: {len(sequence)} residues")
    
    print("\nValidating submission...")
    validate_submission(submission_df, test_sequences)
    
    print("\nSaving submission...")
    save_submission(submission_df, "submission.csv")
    
    print("\n✓ Local test completed successfully!")
    print("\nSample submission:")
    print(submission_df.head(10))


if __name__ == "__main__":
    main()
