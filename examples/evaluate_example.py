"""
Example: Evaluating RNA Structure Predictions

This script demonstrates how to evaluate predictions using the evaluation pipeline.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.metrics import (
    TMScoreCalculator,
    StructureQualityMetrics,
    EvaluationPipeline,
    SubmissionGenerator
)
from src.inference.predict import RNASequencePredictor
from src.config import get_config


def example_tm_score():
    """Example: Calculate TM-score between two structures"""
    print("=" * 60)
    print("Example 1: TM-score Calculation")
    print("=" * 60)
    
    calculator = TMScoreCalculator()
    
    # Create sample structures
    L = 50
    np.random.seed(42)
    
    # True structure
    true_coords = np.random.randn(L, 3) * 10
    
    # Predicted structure (similar but with noise)
    pred_coords = true_coords + np.random.randn(L, 3) * 2.0
    
    # Calculate TM-score
    tm_score = calculator.calculate(pred_coords, true_coords)
    
    print(f"\nSequence length: {L}")
    print(f"TM-score: {tm_score:.4f}")
    print(f"Interpretation:")
    if tm_score > 0.7:
        print("  ✅ Nearly identical structures")
    elif tm_score > 0.5:
        print("  ✅ Similar fold")
    else:
        print("  ⚠️  Different fold (needs improvement)")
    
    return tm_score


def example_quality_metrics():
    """Example: Calculate structure quality metrics"""
    print("\n" + "=" * 60)
    print("Example 2: Structure Quality Metrics")
    print("=" * 60)
    
    metrics_calc = StructureQualityMetrics()
    
    # Create sample structure
    L = 30
    np.random.seed(42)
    coords = np.random.randn(L, 3) * 10
    sequence = "A" * L  # Placeholder sequence
    
    # Calculate metrics
    metrics = metrics_calc.calculate_all_metrics(coords, sequence)
    
    print(f"\nStructure length: {L}")
    print(f"Quality metrics:")
    print(f"  Clashes: {metrics['num_clashes']}")
    print(f"  Bond RMSD: {metrics['rmsd_from_ideal']:.2f} Å")
    print(f"  Radius of gyration: {metrics['radius_of_gyration']:.2f} Å")
    print(f"  Compactness: {metrics['compactness']:.2f} Å")
    
    return metrics


def example_evaluation_pipeline():
    """Example: Complete evaluation pipeline"""
    print("\n" + "=" * 60)
    print("Example 3: Complete Evaluation Pipeline")
    print("=" * 60)
    
    config = get_config()
    eval_pipeline = EvaluationPipeline(config)
    
    # Create sample data
    seq_id = "TEST_SEQ"
    sequence = "AUGCAUGCAU"
    L = len(sequence)
    
    np.random.seed(42)
    
    # Ground truth
    true_coords = np.random.randn(L, 3) * 10
    
    # Predictions (5 conformations)
    pred_coords = np.zeros((L, 5, 3))
    for conf in range(5):
        pred_coords[:, conf, :] = true_coords + np.random.randn(L, 3) * 2.0
    
    predictions = {seq_id: pred_coords}
    ground_truth = {seq_id: true_coords}
    sequences = {seq_id: sequence}
    
    # Evaluate
    results = eval_pipeline.evaluate_predictions(
        predictions, ground_truth, sequences
    )
    
    print(f"\nEvaluation Summary:")
    print(f"  Mean TM-score: {results['mean_tm_score']:.4f}")
    print(f"  Sequences evaluated: {results['num_sequences']}")
    
    return results


def example_submission_generation():
    """Example: Generate submission file"""
    print("\n" + "=" * 60)
    print("Example 4: Submission Generation")
    print("=" * 60)
    
    config = get_config()
    submission_gen = SubmissionGenerator(config)
    
    # Create sample predictions
    predictions = {}
    sequences = {}
    
    for seq_id, seq_str in [("seq_1", "AUGCAUGCAU"), ("seq_2", "GGCGUAGUCC")]:
        L = len(seq_str)
        np.random.seed(42 + hash(seq_id) % 1000)
        
        # Generate 5 conformations
        coords = np.zeros((L, 5, 3))
        base_coords = np.random.randn(L, 3) * 10
        for conf in range(5):
            coords[:, conf, :] = base_coords + np.random.randn(L, 3) * 1.0
        
        predictions[seq_id] = coords
        sequences[seq_id] = seq_str
    
    # Generate submission
    output_path = Path("examples/evaluation_submission.csv")
    output_path.parent.mkdir(exist_ok=True)
    
    df = submission_gen.generate_submission(
        predictions, sequences, output_path
    )
    
    # Validate
    is_valid = submission_gen.validate_submission(df)
    
    print(f"\nSubmission generated:")
    print(f"  Path: {output_path}")
    print(f"  Rows: {len(df)}")
    print(f"  Sequences: {len(predictions)}")
    print(f"  Valid: {is_valid}")
    
    return df


def example_model_evaluation():
    """Example: Evaluate model predictions"""
    print("\n" + "=" * 60)
    print("Example 5: Model Prediction Evaluation")
    print("=" * 60)
    
    config = get_config()
    predictor = RNASequencePredictor(config)
    eval_pipeline = EvaluationPipeline(config)
    
    # Test sequence
    sequence = "GGCGUAGUCC"
    target_id = "eval_test"
    
    # Predict structure
    print(f"\nPredicting structure for: {sequence}")
    pred_coords = predictor.predict_sequence(sequence, target_id, refine=False)
    print(f"  Prediction shape: {pred_coords.shape}")
    
    # Create dummy ground truth for evaluation
    # In real usage, load from train_labels.csv
    np.random.seed(42)
    true_coords = np.random.randn(len(sequence), 3) * 10
    
    # Evaluate
    predictions = {target_id: pred_coords}
    ground_truth = {target_id: true_coords}
    sequences = {target_id: sequence}
    
    results = eval_pipeline.evaluate_predictions(
        predictions, ground_truth, sequences
    )
    
    print(f"\nModel evaluation:")
    print(f"  Mean TM-score: {results['mean_tm_score']:.4f}")
    
    return results


if __name__ == "__main__":
    print("🧬 RNA Structure Evaluation - Usage Examples\n")
    
    # Example 1: TM-score
    tm_score = example_tm_score()
    
    # Example 2: Quality metrics
    metrics = example_quality_metrics()
    
    # Example 3: Evaluation pipeline
    results = example_evaluation_pipeline()
    
    # Example 4: Submission generation
    submission_df = example_submission_generation()
    
    # Example 5: Model evaluation
    model_results = example_model_evaluation()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60)
