# RNA Structure Prediction Model

This module contains the neural network architectures for RNA 3D structure prediction.

## Model Architecture

### RNAStructureModel
Main model combining:
- **MSATransformer**: Processes multiple sequence alignments for evolutionary information
- **StructureModule**: Generates 3D coordinates from sequence features
- **GeometricRefiner**: Physics-based structure refinement

### Architecture Components

1. **TransformerBlock**: Standard transformer with:
   - Multi-head self-attention
   - Pre-norm layer normalization
   - Residual connections
   - MLP with GELU activation

2. **MSATransformer**: 
   - Processes MSA alignments
   - Extracts conservation patterns
   - Outputs MSA features for structure prediction

3. **StructureModule**:
   - Takes sequence and MSA features
   - Generates 3D coordinates
   - Predicts 5 conformations per sequence

4. **GeometricRefiner**:
   - Physics-based refinement
   - Enforces bond length constraints
   - Prevents clashes
   - Gradient-based optimization

## Usage

### Basic Usage

```python
from src.modeling.rna_model import RNAStructureModel
from src.config import get_config

# Initialize model
config = get_config()
model = RNAStructureModel(config)

# Predict structure
sequence = "AUGCAUGCAU"
coords = model.predict(sequence)

# Output: (seq_len, num_conformations, 3)
# coords.shape = (10, 5, 3)
```

### With Refinement

```python
from src.modeling.rna_model import RNAStructureModel, GeometricRefiner
from src.config import get_config

config = get_config()
model = RNAStructureModel(config)
refiner = GeometricRefiner(config)

# Predict
sequence = "AUGCAUGCAU"
coords = model.predict(sequence)

# Refine first conformation
refined = refiner.refine(coords[:, 0, :], sequence)
```

### Using Inference Module

```python
from src.inference.predict import RNASequencePredictor
from src.config import get_config

config = get_config()
predictor = RNASequencePredictor(config)

# Predict with automatic MSA loading
coords = predictor.predict_sequence(
    sequence="AUGCAUGCAU",
    target_id="test_1",
    refine=True
)
```

## Model Configuration

Configure in `src/config.py`:

```python
@dataclass
class Config:
    hidden_dim: int = 128          # Model hidden dimension
    use_msa: bool = True           # Enable MSA processing
    num_conformations: int = 5     # Number of conformations to predict
    max_refinement_steps: int = 50 # Refinement iterations
```

## Integration with Data Pipeline

The model works seamlessly with the data preprocessing pipeline:

```python
from src.preprocessing.data_pipeline import DataPipeline
from src.inference.predict import predict_from_dataframe

# Load and process data
pipeline = DataPipeline()
sequences = pipeline.process_training_data(
    Path("data/raw/train_sequences.csv"),
    Path("data/raw/train_labels.csv")
)

# Predict structures
predictions = predict_from_dataframe(sequences_df, msa_dir=Path("data/msa"))
```

## Model Features

### Current Implementation (NumPy-based)
- ✅ Transformer architecture (placeholder attention)
- ✅ MSA processing
- ✅ Structure generation
- ✅ Geometric refinement
- ✅ Multi-conformation prediction

### For Production (PyTorch/TensorFlow)
- Use proper attention mechanism (scaled dot-product)
- Learnable embeddings instead of random initialization
- Trained weights instead of random weights
- GPU acceleration
- Batch processing optimization

## Training

To train the model (when training infrastructure is ready):

1. **Data**: Use `train_sequences.csv` and `train_labels.csv`
2. **Features**: Extract with `DataPipeline`
3. **Loss**: Structure loss (L1/L2 on coordinates, TM-score)
4. **Optimizer**: Adam with learning rate scheduling
5. **Validation**: Use validation set for early stopping

## Next Steps

1. **Implement Proper Attention**: Replace placeholder with scaled dot-product attention
2. **Add Training Loop**: Implement PyTorch training code
3. **Load Pre-trained Weights**: Use RhoFold or similar pre-trained models
4. **Add Ensemble**: Combine multiple model predictions
5. **Optimize**: GPU acceleration, batch processing

## Notes

- Current model uses NumPy for compatibility
- For production, convert to PyTorch/TensorFlow
- Random weights are initialized (needs training)
- Model architecture is ready for training/inference
