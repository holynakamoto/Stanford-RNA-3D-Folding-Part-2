"""
Entry point to generate submission.csv from test_sequences.csv using the project's inference stack.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Ensure project src is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.inference.predict import predict_from_dataframe
from src.config import get_config
from utils import (
    read_test_sequences,
    build_submission_dataframe,
    validate_submission,
    save_submission,
)


def main():
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

    # Predict per target
    predictions = predict_from_dataframe(sequences_df, config=config, msa_dir=config.msa_dir)

    # Build submission frame with standardized post-processing
    submission_df = build_submission_dataframe(sequences_df, predictions)

    # Validate and save
    validate_submission(submission_df, sequences_df)
    save_submission(submission_df, output_path="submission.csv")


if __name__ == "__main__":
    main()
