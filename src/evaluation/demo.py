"""
Demo evaluation system
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.evaluation.metrics import EvaluationPipeline
from src.config import get_config


def demo():
    """Demo evaluation system"""
    config = get_config()
    eval_pipeline = EvaluationPipeline(config)
    
    # Create dummy data
    seq_id = "TEST_SEQ"
    sequence = "AUGCAUGCAU"
    L = len(sequence)
    
    # Ground truth (random structure)
    np.random.seed(42)
    true_coords = np.random.randn(L, 3) * 10
    
    # Predictions (similar to ground truth with noise)
    pred_coords = np.zeros((L, 5, 3))
    for conf in range(5):
        pred_coords[:, conf, :] = true_coords + np.random.randn(L, 3) * 2.0
    
    predictions = {seq_id: pred_coords}
    ground_truth = {seq_id: true_coords}
    sequences = {seq_id: sequence}
    
    # Evaluate
    results = eval_pipeline.evaluate_predictions(predictions, ground_truth, sequences)
    
    # Generate submission
    output_path = Path("results/demo_submission.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df = eval_pipeline.submission_gen.generate_submission(
        predictions, sequences, output_path
    )
    
    # Validate
    eval_pipeline.submission_gen.validate_submission(df)
    
    return results, df


if __name__ == "__main__":
    results, df = demo()
