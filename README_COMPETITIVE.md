# Building a Competitive RNA Structure Prediction System

## Current Status

✅ **Baseline Complete**: Improved placeholder model that generates valid structures
- Format: Valid submission format
- Quality: Non-zero coordinates, reasonable geometry
- Score: Expected < 0.1 TM-score (baseline, not competitive)

## Project Structure

```
kagglecomp/
├── main.ipynb              # Kaggle submission notebook (keep current)
├── utils.py                # Utility functions (works for both)
├── submission.csv          # Current baseline submission
│
├── data/                   # Competition data
│   ├── raw/               # Raw CSV files, MSA files
│   ├── processed/         # Cleaned/preprocessed data
│   └── features/          # Extracted features
│
├── src/                    # Competitive model code
│   ├── preprocessing/     # Data analysis & preprocessing
│   ├── modeling/          # Model architectures
│   ├── inference/         # Prediction code
│   └── evaluation/        # Metrics & scoring
│
├── models/                 # Trained models
│   ├── checkpoints/       # Training checkpoints
│   └── ensembles/         # Ensemble weights
│
└── results/                # Analysis & plots
```

## Quick Start

### 1. Setup (Already Done)
```bash
./setup_competitive.sh
```

### 2. Download Competition Data
Place these files in `data/raw/`:
- `train_sequences.csv`
- `train_labels.csv`
- `test_sequences.csv`
- MSA files (from `MSA/` directory)

### 3. Test Data Pipeline
```bash
# Test with current submission file
python -m src.preprocessing.data_pipeline

# Or run analysis
python src/preprocessing/analyze_data.py
```

### 4. Process Training Data (once you have competition data)
```python
from src.preprocessing.data_pipeline import DataPipeline
from pathlib import Path

pipeline = DataPipeline()
sequences = pipeline.process_training_data(
    Path("data/raw/train_sequences.csv"),
    Path("data/raw/train_labels.csv")
)
features = pipeline.prepare_training_data(sequences)
```

## Competitive Approaches

### Tier 1: Pre-trained Models (Fastest Path)
**Best for**: Quick competitive baseline

1. **RhoFold** (Recommended)
   - State-of-the-art RNA structure predictor
   - Pre-trained, just need to run inference
   - Expected score: 0.4-0.6 TM-score

2. **RoseTTAFoldRNA**
   - Extension of protein folding model
   - Good for RNA-protein complexes

3. **ESM-2 + Simple GNN**
   - Use ESM-2 embeddings as features
   - Train lightweight GNN for structure prediction
   - Expected score: 0.3-0.5 TM-score

### Tier 2: Custom ML Models (More Work, Better Control)
**Best for**: Learning and customization

1. **Feature Engineering:**
   - ESM-2 sequence embeddings
   - MSA conservation scores
   - Secondary structure predictions
   - Base pairing probabilities

2. **Model Architecture:**
   - Graph Neural Network (GNN)
   - Transformer encoder-decoder
   - Diffusion model for structure generation

3. **Training:**
   - Train on `train_sequences.csv` + `train_labels.csv`
   - Cross-validation for model selection
   - Ensemble multiple models

### Tier 3: Ensemble (Winning Strategy)
**Best for**: Maximum performance

- Combine multiple models:
  - Pre-trained models (RhoFold, etc.)
  - Custom ML models
  - Template-based predictions
- Weighted averaging or learned combination
- Expected score: 0.6-0.75+ TM-score

## Implementation Roadmap

### Phase 1: Quick Win (1-2 days)
- [ ] Integrate RhoFold or similar pre-trained model
- [ ] Run inference on test sequences
- [ ] Generate submission
- **Goal**: 0.4+ TM-score

### Phase 2: Improvement (1 week)
- [ ] Add MSA features
- [ ] Build simple ESM-2 + GNN model
- [ ] Train on training data
- [ ] Ensemble with pre-trained model
- **Goal**: 0.5+ TM-score

### Phase 3: Competitive (2-3 weeks)
- [ ] Advanced architectures (Transformers, Diffusion)
- [ ] Extensive feature engineering
- [ ] Large ensemble
- [ ] Hyperparameter optimization
- **Goal**: 0.65+ TM-score (top 10%)

## Key Files

- `main.ipynb`: Keep for Kaggle submission (current baseline works)
- `src/modeling/`: Add competitive models here
- `src/inference/`: Prediction code for competitive models
- `models/`: Store trained model weights

## Resources

- **RhoFold**: https://github.com/RosettaCommons/RhoFold
- **ESM-2**: https://github.com/facebookresearch/esm
- **PyTorch Geometric**: https://pytorch-geometric.readthedocs.io/
- **Competition**: https://www.kaggle.com/competitions/stanford-rna-3d-folding-2

## Next Steps

1. **Immediate**: Test current baseline submission on Kaggle
2. **Short-term**: Integrate pre-trained model (RhoFold)
3. **Medium-term**: Build custom ML model
4. **Long-term**: Build ensemble system

## Notes

- Keep `main.ipynb` working for submissions
- Develop competitive models in `src/` separately
- Can integrate competitive models into `main.ipynb` when ready
- Current baseline is good for testing submission pipeline
