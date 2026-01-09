# Data Preprocessing Module

This module provides comprehensive data loading, processing, and feature extraction for the RNA structure prediction competition.

## Components

### 1. `data_pipeline.py` - Main Pipeline
Complete data processing pipeline with:
- **DataLoader**: Loads CSV files and parses structures
- **FeatureExtractor**: Extracts features (one-hot encoding, position encoding, distance matrices)
- **DataPipeline**: Orchestrates the entire process
- **RNASequence**: Data class representing sequences with structures

### 2. `load_msa.py` - MSA Processing
Handles Multiple Sequence Alignment files:
- Read MSA FASTA files
- Parse MSA headers for metadata
- Convert MSA to numpy arrays
- Extract conservation and gap frequency features

### 3. `analyze_data.py` - Data Analysis
Convenience script for analyzing competition data:
- Sequence statistics
- Structure properties
- Visualization

## Usage

### Basic Usage

```python
from src.preprocessing.data_pipeline import DataPipeline
from pathlib import Path

# Initialize pipeline
pipeline = DataPipeline(cache_dir=Path("cache"))

# Process submission file (for testing)
df, sequences = pipeline.process_submission_data(Path("submission.csv"))

# Process training data
sequences = pipeline.process_training_data(
    Path("data/raw/train_sequences.csv"),
    Path("data/raw/train_labels.csv")
)

# Extract features
features = pipeline.prepare_training_data(sequences)

# Save features for later use
pipeline.save_features(features, Path("data/features/train_features.pkl.gz"))
```

### Feature Extraction

```python
from src.preprocessing.data_pipeline import FeatureExtractor, RNASequence

extractor = FeatureExtractor()

# Create a sequence object
seq = RNASequence(
    id="1ABC_A",
    sequence="GGCGUAGUCC",
    structure=np.array([...])  # Optional
)

# Extract features
features = extractor.extract_all_features(seq)

# Features include:
# - sequence_encoding: (L, 4) one-hot encoded sequence
# - position_encoding: (L, 128) sinusoidal position encoding
# - distance_matrix: (L, L) pairwise distances (if structure provided)
# - coordinates: (L, 3) 3D coordinates (if structure provided)
```

### MSA Processing

```python
from src.preprocessing.load_msa import load_msa_for_target, extract_msa_features

# Load MSA for a target
msa_array = load_msa_for_target("1ABC_A", msa_dir=Path("data/msa"))

# Extract MSA features
if msa_array is not None:
    features = extract_msa_features(msa_array)
    # Features include:
    # - conservation: (L,) conservation score per position
    # - gap_frequency: (L,) gap frequency per position
```

## Data Formats

### Sequence CSV Format
```csv
target_id,sequence,temporal_cutoff,description,...
1ABC_A,GGCGUAGUCC,2025-01-01,...
```

### Labels CSV Format
```csv
ID,resname,resid,x_1,y_1,z_1,x_2,y_2,z_2,...
1ABC_A_1,G,1,-7.561,9.392,9.361,...
1ABC_A_2,G,2,-8.02,11.014,14.606,...
```

### Submission CSV Format
```csv
ID,resname,resid,x_1,y_1,z_1,...,x_5,y_5,z_5
1ABC_A_1,G,1,-7.561,9.392,9.361,...
1ABC_A_2,G,2,-8.02,11.014,14.606,...
```

## Features

The pipeline extracts the following features:

1. **Sequence Encoding**: One-hot encoding (A, U, G, C) - shape: (L, 4)
2. **Position Encoding**: Sinusoidal position encoding - shape: (L, 128)
3. **Distance Matrix**: Pairwise C1' distances - shape: (L, L)
4. **Coordinates**: 3D C1' coordinates - shape: (L, 3) or (L, n_confs, 3)
5. **MSA Features** (if available):
   - Conservation scores - shape: (L,)
   - Gap frequencies - shape: (L,)

## Testing

Test the pipeline with your current submission:

```bash
cd /Users/nickmoore/kagglecomp
python -m src.preprocessing.data_pipeline
```

Or run the analysis script:

```bash
python src/preprocessing/analyze_data.py
```

## Integration with Models

Features extracted by this pipeline can be directly used with:
- Graph Neural Networks (GNNs)
- Transformer models
- CNN/LSTM architectures
- Any PyTorch/TensorFlow model

Example:
```python
features = pipeline.prepare_training_data(sequences)

# For training
for feature_dict in features:
    seq_encoding = feature_dict['sequence_encoding']
    pos_encoding = feature_dict['position_encoding']
    # ... feed to model
```
