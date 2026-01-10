#!/bin/bash
# Script to prepare RhoFold dataset for Kaggle
# Run locally, then upload as Kaggle dataset

set -e

DATASET_DIR="rhofold_kaggle_dataset"
mkdir -p $DATASET_DIR

echo "=== Preparing RhoFold Dataset for Kaggle ==="

# 1. Clone RhoFold repository
echo "Cloning RhoFold..."
cd $DATASET_DIR
if [ ! -d "RhoFold" ]; then
    git clone https://github.com/ml4bio/RhoFold.git
    cd RhoFold
    
    # Remove git history to save space
    rm -rf .git
    
    echo "Repository cloned"
else
    echo "RhoFold already exists"
    cd RhoFold
fi

# 2. Download pretrained model
echo "Downloading pretrained model..."
mkdir -p pretrained
cd pretrained

# Check if model already exists
if [ ! -f "model.pt" ]; then
    # Download from Zenodo or provided link
    # NOTE: Update this URL with actual RhoFold model link
    # For now, placeholder - check RhoFold GitHub releases
    echo "⚠️  MANUAL STEP: Download model.pt from RhoFold releases"
    echo "    Place in: $DATASET_DIR/RhoFold/pretrained/model.pt"
    echo "    URL: Check https://github.com/ml4bio/RhoFold/releases"
else
    echo "Model already downloaded"
fi

cd ../../..

# 3. Create metadata file
cat > $DATASET_DIR/dataset-metadata.json <<EOF
{
  "title": "RhoFold RNA Structure Prediction",
  "id": "yourusername/rhofold-rna-prediction",
  "licenses": [{"name": "Apache-2.0"}],
  "resources": [
    {
      "path": "RhoFold/",
      "description": "RhoFold model and code for RNA 3D structure prediction"
    }
  ]
}
EOF

# 4. Create README
cat > $DATASET_DIR/README.md <<EOF
# RhoFold RNA Structure Prediction Dataset

This dataset contains the RhoFold model and code for RNA 3D structure prediction.

## Contents
- \`RhoFold/\`: Complete RhoFold repository
- \`pretrained/model.pt\`: Pre-trained model weights

## Usage in Kaggle Notebook

\`\`\`python
import sys
sys.path.append('/kaggle/input/rhofold-rna-prediction/RhoFold')

from rhofold.model import RhoFold
from rhofold.utils import inference

# Load model
model = RhoFold.load_from_checkpoint(
    '/kaggle/input/rhofold-rna-prediction/RhoFold/pretrained/model.pt'
)
\`\`\`

## Citation
If you use RhoFold, please cite:
[Add RhoFold citation]

## License
Apache 2.0
EOF

echo ""
echo "=== Dataset Preparation Complete ==="
echo ""
echo "Next steps:"
echo "1. Download model weights manually (see message above)"
echo "2. Upload $DATASET_DIR to Kaggle:"
echo "   - Go to https://www.kaggle.com/datasets"
echo "   - Click 'New Dataset'"
echo "   - Upload folder: $DATASET_DIR"
echo "   - Make it public"
echo "3. Add dataset to your competition notebook"
echo ""
echo "Dataset location: $(pwd)/$DATASET_DIR"
