#!/bin/bash
set -e

echo "🧬 RNA Structure Prediction - Competition Winning System"
echo "========================================================"

# Create directory structure
mkdir -p {data,models,src,notebooks,results,logs,cache}
mkdir -p data/{raw,processed,msa,features}
mkdir -p models/{checkpoints,ensembles,configs}
mkdir -p src/{preprocessing,modeling,inference,evaluation}

echo "✅ Directory structure created"

# Install core dependencies
echo "📦 Installing dependencies..."

pip install --break-system-packages -q \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

pip install --break-system-packages -q \
    biopython==1.83 \
    pandas==2.1.4 \
    numpy==1.26.3 \
    scipy==1.11.4 \
    scikit-learn==1.3.2 \
    matplotlib==3.8.2 \
    seaborn==0.13.0 \
    tqdm==4.66.1 \
    wandb==0.16.2 \
    einops==0.7.0 \
    fair-esm==2.0.0 \
    transformers==4.36.2

echo "✅ Core dependencies installed"

# Download competition data info
cat > data/COMPETITION_INFO.md << 'EOF'
# RNA 3D Structure Prediction Competition

## Data Sources
1. Training sequences with ground truth structures
2. MSA (Multiple Sequence Alignment) files
3. Test sequences (structures to predict)

## Evaluation Metric
TM-score (Template Modeling score)
- Range: [0, 1]
- >0.5: Similar fold
- >0.7: Nearly identical structures
- Competition winning score: likely 0.65-0.75+

## Submission Format
- CSV with columns: ID, resname, resid, x_1, y_1, z_1, ..., x_5, y_5, z_5
- 5 conformations per residue
- All coordinates in Angstroms
EOF

echo "✅ Competition info documented"
echo ""
echo "🚀 Next steps:"
echo "1. Download competition data to data/raw/"
echo "2. Run data analysis: python src/preprocessing/analyze_data.py"
echo "3. Build baseline model"
echo ""
