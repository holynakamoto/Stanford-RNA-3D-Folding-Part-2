"""
Analyze competition data to understand distributions, patterns, and statistics.

This is a convenience wrapper around the main data_pipeline module.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.preprocessing.data_pipeline import DataPipeline
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_sequences(sequences_df: pd.DataFrame, output_dir: str = "results"):
    """
    Analyze sequence data and generate statistics.
    
    Args:
        sequences_df: DataFrame with target_id, sequence, and metadata
        output_dir: Directory to save analysis results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=== Sequence Analysis ===")
    print(f"Total sequences: {len(sequences_df)}")
    print(f"\nSequence length statistics:")
    lengths = sequences_df['sequence'].str.len()
    print(lengths.describe())
    
    # Nucleotide composition
    print(f"\nNucleotide composition:")
    all_seqs = ''.join(sequences_df['sequence'].values)
    nuc_counts = pd.Series(list(all_seqs)).value_counts()
    print(nuc_counts)
    
    # Save plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Length distribution
    axes[0, 0].hist(lengths, bins=50, edgecolor='black')
    axes[0, 0].set_xlabel('Sequence Length')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Sequence Length Distribution')
    
    # Nucleotide composition
    axes[0, 1].bar(nuc_counts.index, nuc_counts.values)
    axes[0, 1].set_xlabel('Nucleotide')
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].set_title('Overall Nucleotide Composition')
    
    # GC content
    gc_content = sequences_df['sequence'].apply(
        lambda s: (s.count('G') + s.count('C')) / len(s) if len(s) > 0 else 0
    )
    axes[1, 0].hist(gc_content, bins=30, edgecolor='black')
    axes[1, 0].set_xlabel('GC Content')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('GC Content Distribution')
    
    # Sequence length vs GC content
    axes[1, 1].scatter(lengths, gc_content, alpha=0.5)
    axes[1, 1].set_xlabel('Sequence Length')
    axes[1, 1].set_ylabel('GC Content')
    axes[1, 1].set_title('Length vs GC Content')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/sequence_analysis.png", dpi=150)
    print(f"\n✅ Analysis plots saved to {output_dir}/sequence_analysis.png")
    
    return {
        'length_stats': lengths.describe().to_dict(),
        'nucleotide_counts': nuc_counts.to_dict(),
        'gc_content_stats': gc_content.describe().to_dict()
    }


def analyze_structures(labels_df: pd.DataFrame, output_dir: str = "results"):
    """
    Analyze structure data from labels.
    
    Args:
        labels_df: DataFrame with structure coordinates
        output_dir: Directory to save analysis results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n=== Structure Analysis ===")
    
    # Extract coordinate columns
    coord_cols = [col for col in labels_df.columns if col.startswith(('x_', 'y_', 'z_'))]
    n_predictions = len([c for c in coord_cols if c.startswith('x_')])
    
    print(f"Number of structure predictions: {n_predictions}")
    print(f"Total residues: {len(labels_df)}")
    
    # Calculate inter-residue distances for each prediction
    for pred_num in range(1, n_predictions + 1):
        x_col, y_col, z_col = f'x_{pred_num}', f'y_{pred_num}', f'z_{pred_num}'
        coords = labels_df[[x_col, y_col, z_col]].values
        
        # Group by sequence
        seq_ids = labels_df['ID'].str.split('_').str[0]
        distances = []
        
        for seq_id in seq_ids.unique():
            seq_mask = seq_ids == seq_id
            seq_coords = coords[seq_mask]
            if len(seq_coords) > 1:
                for i in range(len(seq_coords) - 1):
                    dist = np.linalg.norm(seq_coords[i+1] - seq_coords[i])
                    distances.append(dist)
        
        if distances:
            distances = np.array(distances)
            print(f"\nPrediction {pred_num}:")
            print(f"  Mean inter-residue distance: {distances.mean():.2f} Å")
            print(f"  Std: {distances.std():.2f} Å")
            print(f"  Range: [{distances.min():.2f}, {distances.max():.2f}] Å")
    
    return {'n_predictions': n_predictions, 'n_residues': len(labels_df)}


if __name__ == "__main__":
    # Example usage
    print("Data Analysis Script")
    print("=" * 50)
    
    # Use the main data pipeline
    pipeline = DataPipeline()
    
    # Try to load data
    from src.config import get_config
    config = get_config()
    
    data_dir = config.raw_data_dir
    
    # Process training data if available
    if config.train_sequences_file.exists() and config.train_labels_file.exists():
        print(f"\nLoading training data from {data_dir}")
        sequences = pipeline.process_training_data(
            config.train_sequences_file,
            config.train_labels_file
        )
        
        # Prepare features
        features = pipeline.prepare_training_data(sequences)
        print(f"\n✅ Processed {len(features)} sequences with features")
        
        # Save features
        feature_path = config.features_dir / "train_features.pkl.gz"
        pipeline.save_features(features, feature_path)
    
    # Process submission file if available (for testing)
    elif config.submission_sample_path.exists():
        print(f"\nLoading submission data from {config.submission_sample_path}")
        df, sequences = pipeline.process_submission_data(config.submission_sample_path)
        
        # Prepare features
        features = pipeline.prepare_training_data(sequences)
        print(f"\n✅ Processed {len(features)} sequences with features")
    
    else:
        print(f"\n⚠️  No data files found.")
        print(f"Expected files:")
        print(f"  - {config.train_sequences_file}")
        print(f"  - {config.train_labels_file}")
        print(f"  - {config.submission_sample_path} (for testing)")
    
    print("\n✅ Analysis complete!")
