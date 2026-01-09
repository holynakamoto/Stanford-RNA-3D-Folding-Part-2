# Competitive RNA Structure Prediction Setup

This directory structure is designed for building a competitive RNA 3D structure prediction system.

## Directory Structure

```
kagglecomp/
├── data/
│   ├── raw/              # Raw competition data (CSV files, MSA files)
│   ├── processed/        # Processed/cleaned data
│   ├── msa/              # Multiple sequence alignment files
│   └── features/         # Extracted features (embeddings, etc.)
├── models/
│   ├── checkpoints/     # Model checkpoints during training
│   ├── ensembles/       # Ensemble model weights
│   └── configs/          # Model configuration files
├── src/
│   ├── preprocessing/    # Data preprocessing scripts
│   ├── modeling/        # Model architectures
│   ├── inference/       # Inference/prediction code
│   └── evaluation/      # Evaluation metrics
├── notebooks/           # Jupyter notebooks for exploration
├── results/             # Analysis results, plots
├── logs/                # Training logs
└── cache/               # Cached computations
```

## Setup Instructions

1. **Run the setup script:**
   ```bash
   ./setup_competitive.sh
   ```

2. **Download competition data:**
   - Place `train_sequences.csv`, `train_labels.csv`, `test_sequences.csv` in `data/raw/`
   - Place MSA files in `data/msa/`

3. **Analyze the data:**
   ```bash
   python src/preprocessing/analyze_data.py
   ```

## Next Steps for Competitive Model

### Option 1: Pre-trained Models
- **RhoFold**: State-of-the-art RNA structure predictor
- **RoseTTAFoldRNA**: Extension of RoseTTAFold for RNA
- **ESM-2 + GNN**: Use protein language model embeddings with graph networks

### Option 2: Build from Scratch
1. **Feature Extraction:**
   - ESM-2 embeddings for sequences
   - MSA features (conservation, coevolution)
   - Secondary structure predictions

2. **Model Architecture:**
   - Graph Neural Network (GNN) for structure prediction
   - Transformer-based encoder-decoder
   - Diffusion models for structure generation

3. **Training Strategy:**
   - Train on `train_sequences.csv` with `train_labels.csv`
   - Use validation set for early stopping
   - Ensemble multiple models

### Option 3: Template-Based Approach
- Search PDB for similar RNA structures
- Use homology modeling
- Refine with energy minimization

## Key Files

- `main.ipynb`: Current submission notebook (keep for Kaggle)
- `utils.py`: Utility functions (already set up)
- `src/`: Competitive model code (separate from submission)

## Competition Strategy

1. **Baseline (Current)**: Geometric placeholder - ✅ Done
2. **Simple ML**: ESM-2 + simple GNN - Next step
3. **Advanced**: Pre-trained RNA models - Competitive
4. **Ensemble**: Combine multiple approaches - Winning strategy

## Resources

- [RhoFold Paper](https://www.nature.com/articles/s41592-023-02048-x)
- [ESM-2 Documentation](https://github.com/facebookresearch/esm)
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/) for GNNs
