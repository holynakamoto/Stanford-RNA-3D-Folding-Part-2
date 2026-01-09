# Quick Start Guide - Getting to Top 5%

**See `QUICK_START_WINNING.md` for the complete detailed guide!**

## Current Status ✅

You have a complete, working baseline system. Here's what works right now:

- ✅ Submission generation (format validated)
- ✅ Data pipeline (tested with sample data)
- ✅ Model architecture (ready for training)
- ✅ Evaluation system (TM-score working)
- ✅ All code tested and documented

## Immediate Next Steps

### 1. Test Current Baseline (5 minutes)

```bash
cd /Users/nickmoore/kagglecomp

# Test prediction
python examples/predict_example.py

# Test evaluation
python examples/evaluate_example.py

# Generate submission
python test_locally.py
```

### 2. Submit Baseline to Kaggle (10 minutes)

1. Upload `main.ipynb` to Kaggle
2. Also upload `utils.py` (needed by notebook)
3. Run notebook on Kaggle
4. Download `submission.csv`
5. Submit to competition

**Expected score:** ~0.10-0.15 TM-score (baseline)

### 3. Download Competition Data (30 minutes)

```bash
# Install Kaggle API
pip install kaggle

# Download competition data
kaggle competitions download -c stanford-rna-3d-folding-2

# Extract
unzip stanford-rna-3d-folding-2.zip -d data/raw/

# Organize
# You should have:
# - data/raw/train_sequences.csv
# - data/raw/train_labels.csv
# - data/raw/test_sequences.csv
# - data/raw/MSA/*.fasta
```

### 4. Test on Real Data (1 hour)

```bash
# Analyze training data
python src/preprocessing/analyze_data.py

# Test prediction on real sequences
python examples/predict_example.py  # Modify to use real data

# Evaluate if you have labels
python examples/evaluate_example.py  # Modify to use real labels
```

## Week 1 Goal: Data Infrastructure

**Tasks:**
- [ ] Download all competition data
- [ ] Process training sequences
- [ ] Extract MSA features
- [ ] Create train/validation split
- [ ] Cache processed features

**Deliverable:** Working data pipeline on real competition data

## Week 2 Goal: Pre-trained Model

**Tasks:**
- [ ] Choose model (RoseTTAFoldRNA recommended)
- [ ] Clone repository
- [ ] Download weights
- [ ] Integrate into pipeline
- [ ] Evaluate baseline

**Deliverable:** Pre-trained model inference working

**Expected improvement:** +0.40 TM-score (0.15 → 0.55)

## Key Files Reference

### Current Submission
- `main.ipynb` - Submission notebook
- `utils.py` - Utility functions
- `submission.csv` - Current baseline

### For Development
- `src/preprocessing/` - Data pipeline
- `src/modeling/` - Model code
- `src/inference/` - Prediction code
- `src/evaluation/` - Evaluation metrics

### For Training (Week 3+)
- `src/training/` - (Create this for training loop)
- `models/checkpoints/` - Save trained models here
- `logs/` - Training logs (wandb)

## Commands Reference

```bash
# Data processing
python src/preprocessing/analyze_data.py
python src/preprocessing/data_pipeline.py

# Prediction
python examples/predict_example.py
python -m src.inference.predict

# Evaluation
python examples/evaluate_example.py
python -m src.evaluation.demo

# Testing
python test_locally.py

# Notebook
jupyter notebook main.ipynb
# Or open in VS Code
```

## Quick Win Checklist

- [x] Baseline submission ready
- [ ] Submit baseline to Kaggle (establish position)
- [ ] Download competition data
- [ ] Test data pipeline
- [ ] Set up GPU environment
- [ ] Clone pre-trained model (Week 2)
- [ ] Integrate pre-trained model (Week 2)
- [ ] First competitive submission (Week 2)

## Success Metrics

Track your progress:

- **Baseline (Now):** ~0.10-0.15 TM-score
- **Week 2:** >0.50 TM-score (pre-trained)
- **Week 3:** >0.55 TM-score (fine-tuned)
- **Week 4:** >0.60 TM-score (improved)
- **Week 5:** >0.65 TM-score (ensemble)
- **Week 6:** >0.70 TM-score (final)

## Need Help?

- Check `README.md` for overview
- Check `WINNING_STRATEGY.md` for detailed roadmap
- Check `src/*/README.md` for module-specific docs
- Check `examples/` for usage examples

---

**You're ready to start! Good luck! 🚀**
