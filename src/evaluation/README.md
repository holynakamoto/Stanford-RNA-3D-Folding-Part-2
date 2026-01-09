# Evaluation and Submission System

This module provides tools for evaluating RNA structure predictions and generating submission files.

## Components

### 1. TMScoreCalculator
Calculates TM-score (Template Modeling score), the competition's evaluation metric.

**TM-score**:
- Range: [0, 1]
- >0.5: Similar fold
- >0.7: Nearly identical structures
- Competition winning scores: likely 0.65-0.75+

### 2. StructureQualityMetrics
Additional quality metrics for structure validation:
- **Clash count**: Steric clashes (atoms too close)
- **Bond RMSD**: Deviation from ideal backbone distances
- **Radius of gyration**: Measure of compactness
- **Compactness**: Average pairwise distance

### 3. SubmissionGenerator
Generates submission files in the competition format:
- Validates format
- Clips coordinates to valid range [-999.999, 9999.999]
- Ensures correct ID format (`target_id_resid`)

### 4. EvaluationPipeline
Complete evaluation pipeline combining all components.

## Usage

### Evaluate Predictions

```python
from src.evaluation.metrics import EvaluationPipeline
from src.config import get_config

config = get_config()
eval_pipeline = EvaluationPipeline(config)

# Predictions: Dict[seq_id, coords] where coords shape is (L, num_confs, 3)
predictions = {
    'seq_1': coords1,  # Shape: (100, 5, 3)
    'seq_2': coords2,  # Shape: (50, 5, 3)
}

# Ground truth: Dict[seq_id, coords] where coords shape is (L, 3)
ground_truth = {
    'seq_1': true_coords1,  # Shape: (100, 3)
    'seq_2': true_coords2,  # Shape: (50, 3)
}

# Sequences: Dict[seq_id, sequence_str]
sequences = {
    'seq_1': 'AUGCAUGCAU...',
    'seq_2': 'GGCGUAGUCC...',
}

# Evaluate
results = eval_pipeline.evaluate_predictions(
    predictions, ground_truth, sequences
)

# Results include:
# - mean_tm_score: Average TM-score
# - per_sequence_results: Detailed metrics per sequence
```

### Generate Submission

```python
from src.evaluation.metrics import SubmissionGenerator
from src.config import get_config
from pathlib import Path

config = get_config()
submission_gen = SubmissionGenerator(config)

# Predictions and sequences
predictions = {...}  # Dict[seq_id, coords] where coords shape is (L, 5, 3)
sequences = {...}    # Dict[seq_id, sequence_str]

# Generate submission
output_path = Path("submission.csv")
df = submission_gen.generate_submission(
    predictions, sequences, output_path
)

# Validate
is_valid = submission_gen.validate_submission(df)
```

### Calculate TM-score Directly

```python
from src.evaluation.metrics import TMScoreCalculator

calculator = TMScoreCalculator()

# pred_coords: (L, 3)
# true_coords: (L, 3)
tm_score = calculator.calculate(pred_coords, true_coords)

print(f"TM-score: {tm_score:.4f}")
```

### Calculate Quality Metrics

```python
from src.evaluation.metrics import StructureQualityMetrics

metrics_calc = StructureQualityMetrics()

# coords: (L, 3)
# sequence: "AUGCAUGCAU..."
metrics = metrics_calc.calculate_all_metrics(coords, sequence)

print(f"Clashes: {metrics['num_clashes']}")
print(f"Bond RMSD: {metrics['rmsd_from_ideal']:.2f} Å")
print(f"Radius of gyration: {metrics['radius_of_gyration']:.2f} Å")
```

## Integration with Model

```python
from src.inference.predict import RNASequencePredictor
from src.evaluation.metrics import EvaluationPipeline, SubmissionGenerator
from src.config import get_config
import pandas as pd

config = get_config()

# Initialize predictor
predictor = RNASequencePredictor(config)

# Predict structures
sequences_df = pd.DataFrame({
    'target_id': ['seq_1', 'seq_2'],
    'sequence': ['AUGCAUGCAU', 'GGCGUAGUCC'],
    ...
})

predictions = {}
sequences_dict = {}
for _, row in sequences_df.iterrows():
    target_id = row['target_id']
    sequence = row['sequence']
    
    coords = predictor.predict_sequence(sequence, target_id)
    predictions[target_id] = coords  # Shape: (L, 5, 3)
    sequences_dict[target_id] = sequence

# Generate submission
submission_gen = SubmissionGenerator(config)
df = submission_gen.generate_submission(
    predictions, sequences_dict, Path("submission.csv")
)
```

## Evaluation on Training Data

```python
from src.preprocessing.data_pipeline import DataPipeline
from src.inference.predict import RNASequencePredictor
from src.evaluation.metrics import EvaluationPipeline
from pathlib import Path

# Load training data
pipeline = DataPipeline()
sequences = pipeline.process_training_data(
    Path("data/raw/train_sequences.csv"),
    Path("data/raw/train_labels.csv")
)

# Convert to ground truth format
ground_truth = {}
sequences_dict = {}
for seq_id, seq_obj in sequences.items():
    # Use first conformation as ground truth
    ground_truth[seq_id] = seq_obj.structure[:, 0, :]  # (L, 3)
    sequences_dict[seq_id] = seq_obj.sequence

# Predict
config = get_config()
predictor = RNASequencePredictor(config)
predictions = {}
for seq_id, seq_obj in sequences.items():
    coords = predictor.predict_sequence(seq_obj.sequence, seq_id)
    predictions[seq_id] = coords  # (L, 5, 3)

# Evaluate
eval_pipeline = EvaluationPipeline(config)
results = eval_pipeline.evaluate_predictions(
    predictions, ground_truth, sequences_dict
)
```

## TM-score Details

The TM-score calculation uses the competition's formula:

```
TM-score = (1/L) * Σ(1 / (1 + (d_i / d0)^2))
```

Where:
- `L`: Length of structure
- `d_i`: Distance between aligned residue pairs
- `d0`: Normalization factor based on length

The structures are optimally aligned using the Kabsch algorithm before calculating distances.

## Validation Rules

Submission validation checks:
- ✅ All required columns present
- ✅ No NaN values
- ✅ Coordinates within valid range [-999.999, 9999.999]
- ✅ Correct ID format (`target_id_resid`)
- ✅ 5 conformations per sequence

## Notes

- TM-score calculation uses optimal superposition (Kabsch algorithm)
- Quality metrics help validate structure realism
- Submission generator automatically clips coordinates
- All metrics are computed efficiently

The evaluation system is ready for use with your predictions!
