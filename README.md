# Stanford RNA 3D Folding Part 2 - Kaggle Competition

## Competition Overview

This competition focuses on predicting the 3D structure of RNA molecules using only their sequences. The goal is to develop machine learning models that can predict RNA folding and function at the molecular level.

## Evaluation Metric

Submissions are scored using **TM-score** (Template Modeling Score), which ranges from 0.0 to 1.0 (higher is better).

## Submission Format

- **Input**: `test_sequences.csv` with columns:
  - `target_id`: Identifier (format: `pdb_id_chain_id`)
  - `sequence`: RNA sequence string
  - Additional metadata: `temporal_cutoff`, `description`, `stoichiometry`, `all_sequences`, etc.
  
- **Output**: `submission.csv` with 5 predictions per sequence
- Format: `ID,resname,resid,x_1,y_1,z_1,x_2,y_2,z_2,x_3,y_3,z_3,x_4,y_4,z_4,x_5,y_5,z_5`
- **ID Format**: `target_id_resid` (e.g., `1ABC_A_1`, `1ABC_A_2`)
- **Coordinates**: Must be in range [-999.999, 9999.999] (automatically clipped)
- Each sequence must have 5 structure predictions, and coordinates are for the C1' atom of each residue.

See `DATA_FORMAT.md` for detailed information about the data structure.

## Requirements

- CPU/GPU Notebook ≤ 8 hours run-time
- Internet access disabled
- Freely & publicly available external data allowed (including pre-trained models)
- Submission file must be named `submission.csv`

## Key Resources

- [CASP16 challenge 2024](https://kaggle.com/competitions/stanford-rna-3d-folding-2) - State-of-the-art approaches
- [Part 1 of Stanford RNA 3D Folding challenge](https://kaggle.com/competitions/stanford-rna-3d-folding) - Previous competition results

## Timeline

- **Start Date**: January 7, 2026
- **Entry Deadline**: March 18, 2026
- **Competition End**: March 25, 2026

## Getting Started

### Quick Start

1. **Set up virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install ipykernel
   ```

2. **Configure VS Code**:
   - Select interpreter: `.venv/bin/python` (Command Palette → "Python: Select Interpreter")
   - Reload VS Code window
   - Open `main.ipynb` and select the kernel

3. **Test locally**:
   ```bash
   python test_locally.py
   ```

4. **Run the notebook**: Open `main.ipynb` in VS Code or Jupyter

See `SETUP.md` for detailed environment setup instructions and troubleshooting.

### Competitive Setup

For building competitive models, see:
- `README_COMPETITIVE.md` - Competitive strategy guide
- `COMPETITIVE_SETUP.md` - Setup instructions
- `src/` - Source code for models and evaluation

### Project Structure

- `main.ipynb` - Kaggle submission notebook (baseline)
- `utils.py` - Utility functions
- `src/preprocessing/` - Data pipeline
- `src/modeling/` - Model architectures
- `src/inference/` - Prediction code
- `src/evaluation/` - Evaluation metrics (TM-score, etc.)
- `examples/` - Usage examples

## Competition Rules

**Important**: Please review the competition rules before submitting. Key points:
- Maximum 5 submissions per day
- Up to 2 final submissions for judging
- Winners must provide open source code (OSI-approved license)
- External data must be publicly available and reasonably accessible
- See `COMPETITION_RULES.md` for a summary of key requirements
