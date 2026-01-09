"""
Example: Using the RNA Structure Prediction Model

This script demonstrates how to use the model for prediction.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.inference.predict import RNASequencePredictor, predict_from_dataframe
from src.config import get_config
import pandas as pd


def example_single_prediction():
    """Example: Predict structure for a single sequence"""
    print("=" * 60)
    print("Example 1: Single Sequence Prediction")
    print("=" * 60)
    
    # Initialize predictor
    config = get_config()
    predictor = RNASequencePredictor(config)
    
    # Predict
    sequence = "GGCGUAGUCC"
    target_id = "example_1"
    
    print(f"\nSequence: {sequence}")
    print(f"Length: {len(sequence)} residues")
    
    coords = predictor.predict_sequence(
        sequence=sequence,
        target_id=target_id,
        refine=False  # Set to True for refinement
    )
    
    print(f"\n✅ Prediction successful!")
    print(f"  Shape: {coords.shape}")
    print(f"  Expected: ({len(sequence)}, {config.num_conformations}, 3)")
    print(f"  Coordinate range: [{coords.min():.2f}, {coords.max():.2f}] Å")
    
    return coords


def example_batch_prediction():
    """Example: Predict structures for multiple sequences"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Prediction")
    print("=" * 60)
    
    # Create sample sequences
    sequences_df = pd.DataFrame({
        'target_id': ['seq_1', 'seq_2'],
        'sequence': ['GGCGUAGUCC', 'AUCGAUCGAU'],
        'temporal_cutoff': ['2025-01-01', '2025-01-02'],
        'description': ['Example 1', 'Example 2'],
        'stoichiometry': ['A:1', 'B:1'],
        'all_sequences': ['', ''],
        'ligand_ids': ['', ''],
        'ligand_SMILES': ['', '']
    })
    
    print(f"\nSequences to predict: {len(sequences_df)}")
    
    # Predict
    predictions = predict_from_dataframe(sequences_df)
    
    print(f"\n✅ Batch prediction successful!")
    for target_id, coords in predictions.items():
        print(f"  {target_id}: Shape {coords.shape}")
    
    return predictions


def example_with_submission_format():
    """Example: Generate submission format predictions"""
    print("\n" + "=" * 60)
    print("Example 3: Submission Format Output")
    print("=" * 60)
    
    from src.preprocessing.data_pipeline import DataPipeline
    from utils import generate_submission_template, save_submission
    
    # Load sequences (using sample data)
    sequences_df = pd.DataFrame({
        'target_id': ['1ABC_A', '2DEF_B'],
        'sequence': ['GGCGUAGUCC', 'AUCGAUCGAU'],
        'temporal_cutoff': ['2025-01-01', '2025-01-02'],
        'description': ['Sample 1', 'Sample 2'],
        'stoichiometry': ['A:1', 'B:1'],
        'all_sequences': ['', ''],
        'ligand_ids': ['', ''],
        'ligand_SMILES': ['', '']
    })
    
    # Initialize predictor
    config = get_config()
    predictor = RNASequencePredictor(config)
    
    # Generate submission template
    submission_df = generate_submission_template(sequences_df)
    
    # Predict structures
    print("\nGenerating predictions...")
    for _, row in sequences_df.iterrows():
        target_id = row['target_id']
        sequence = row['sequence']
        
        coords = predictor.predict_sequence(sequence, target_id, refine=False)
        
        # Update submission DataFrame
        for resid in range(1, len(sequence) + 1):
            submission_id = f"{target_id}_{resid}"
            mask = submission_df['ID'] == submission_id
            
            for conf_idx in range(config.num_conformations):
                pred_num = conf_idx + 1
                submission_df.loc[mask, f'x_{pred_num}'] = coords[resid-1, conf_idx, 0]
                submission_df.loc[mask, f'y_{pred_num}'] = coords[resid-1, conf_idx, 1]
                submission_df.loc[mask, f'z_{pred_num}'] = coords[resid-1, conf_idx, 2]
        
        print(f"  ✅ Processed {target_id}")
    
    # Save submission
    output_path = Path("examples/prediction_submission.csv")
    output_path.parent.mkdir(exist_ok=True)
    save_submission(submission_df, output_path)
    
    print(f"\n✅ Submission file created: {output_path}")
    print(f"  Shape: {submission_df.shape}")
    
    return submission_df


if __name__ == "__main__":
    # Run examples
    print("🧬 RNA Structure Prediction - Usage Examples\n")
    
    # Example 1: Single prediction
    coords1 = example_single_prediction()
    
    # Example 2: Batch prediction
    predictions = example_batch_prediction()
    
    # Example 3: Submission format
    submission = example_with_submission_format()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60)
