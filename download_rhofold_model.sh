#!/bin/bash
# Download RhoFold pretrained model from Google Drive

set -e

MODEL_DIR="/Users/nickmoore/kagglecomp/rhofold_kaggle_dataset/RhoFold/pretrained"
MODEL_URL="https://drive.google.com/file/d/1To2bjbhQLFx1k8hBOW5q1JFq6ut27XEv/view?usp=sharing"
MODEL_FILE="$MODEL_DIR/model.pt"

echo "=== Downloading RhoFold Pretrained Model ==="
echo ""
echo "Model URL: $MODEL_URL"
echo "Destination: $MODEL_FILE"
echo ""

# Check if gdown is installed
if ! command -v gdown &> /dev/null; then
    echo "Installing gdown (Google Drive downloader)..."
    pip install gdown
fi

# Download model
echo "Downloading model (this may take a few minutes, ~500MB)..."
cd "$MODEL_DIR"

# Use gdown with the file ID
FILE_ID="1To2bjbhQLFx1k8hBOW5q1JFq6ut27XEv"
gdown "https://drive.google.com/uc?id=${FILE_ID}" -O model.pt

if [ -f "model.pt" ]; then
    echo ""
    echo "✓ Model downloaded successfully!"
    echo "  Location: $MODEL_FILE"
    echo "  Size: $(du -h model.pt | cut -f1)"
    echo ""
    echo "Dataset is now ready to upload to Kaggle!"
else
    echo ""
    echo "✗ Download failed. Manual download instructions:"
    echo ""
    echo "1. Open this URL in your browser:"
    echo "   $MODEL_URL"
    echo ""
    echo "2. Click 'Download' button"
    echo ""
    echo "3. Move the downloaded file to:"
    echo "   $MODEL_DIR/model.pt"
    echo ""
    echo "Alternative: Use rclone or another Google Drive tool"
fi
