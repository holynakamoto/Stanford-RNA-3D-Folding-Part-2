"""
Entry point to generate submission.csv from test_sequences.csv using the project's inference stack.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import argparse

# Ensure project src is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.inference.predict import predict_from_dataframe
from src.config import get_config
from src.utils.diagnostics import diagnose_conformational_diversity
from utils import (
    read_test_sequences,
    build_submission_dataframe,
    validate_submission,
    save_submission,
)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate RNA 3D structure predictions")
    parser.add_argument("--diagnose", action="store_true", 
                       help="Run RMSD diagnostics on first 3 targets (for fast local validation)")
    parser.add_argument("--diagnose-targets", type=int, default=3,
                       help="Number of targets to diagnose (default: 3)")
    parser.add_argument("--center", action="store_true",
                       help="Center coordinates (default: False to preserve diversity)")
    args = parser.parse_args()
    
    # Resolve test_sequences path
    # Prefer local test_sequences.csv if present, otherwise sample_test_sequences.csv for dry-runs
    if os.path.exists("test_sequences.csv"):
        sequences_df = read_test_sequences("test_sequences.csv")
    elif os.path.exists("sample_test_sequences.csv"):
        print("Using sample_test_sequences.csv for dry-run")
        sequences_df = pd.read_csv("sample_test_sequences.csv")
    else:
        # Kaggle input path fallback
        sequences_df = read_test_sequences("/kaggle/input/stanford-rna-3d-folding-2/test_sequences.csv")

    # Minimal required columns check
    if not {"target_id", "sequence"}.issubset(sequences_df.columns):
        raise ValueError("test_sequences.csv must include 'target_id' and 'sequence' columns")

    config = get_config()
    
    print("\n" + "="*60)
    print("RNA 3D Structure Prediction Pipeline")
    print("="*60)
    print(f"Config settings:")
    print(f"  - Max refinement steps: {config.max_refinement_steps}")
    print(f"  - Noise scales: {config.noise_scales}")
    print(f"  - Num conformations: {config.num_conformations}")
    print(f"  - Centering: {args.center}")
    print("="*60 + "\n")

    # Predict per target
    predictions = predict_from_dataframe(sequences_df, config=config, msa_dir=config.msa_dir)

    # Run diagnostics if requested (fast local validation)
    if args.diagnose:
        print("\n" + "="*60)
        print("CONFORMATIONAL DIVERSITY DIAGNOSTICS")
        print("="*60)
        check_targets = list(predictions.keys())[:args.diagnose_targets]
        
        for target_id in check_targets:
            coords = predictions[target_id]  # (L, K, 3)
            coords_list = [coords[:, k, :] for k in range(coords.shape[1])]
            diagnose_conformational_diversity(
                coords_list, 
                target_id=target_id, 
                expected_scales=config.noise_scales
            )
        
        print("\n" + "="*60)
        print("✅ Diagnostics complete!")
        print("="*60 + "\n")

    # Build submission frame with standardized post-processing
    submission_df = build_submission_dataframe(sequences_df, predictions, center=args.center)

    # Validate and save
    validate_submission(submission_df, sequences_df)
    save_submission(submission_df, output_path="submission.csv")


if __name__ == "__main__":
    main()
