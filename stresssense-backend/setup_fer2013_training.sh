#!/bin/bash
# setup_fer2013_training.sh — Setup FER2013 Training Environment
# ================================================================
# Installs dependencies and downloads FER2013 dataset for CNN training

set -e  # Exit on error

echo "=========================================="
echo "🚀 FER2013 Training Setup"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install tensorflow>=2.10.0
pip install numpy pandas matplotlib seaborn scikit-learn
pip install kaggle  # For dataset download

echo ""
echo "=========================================="
echo "📥 FER2013 Dataset Setup"
echo "=========================================="

# Check if dataset already exists
if [ -f "data/fer2013.csv" ]; then
    echo "✅ FER2013 dataset already exists at data/fer2013.csv"
else
    echo "📥 Downloading FER2013 dataset..."
    echo ""
    echo "⚠️  You need a Kaggle account and API token:"
    echo "   1. Go to https://www.kaggle.com/settings"
    echo "   2. Click 'Create New API Token'"
    echo "   3. Place kaggle.json in ~/.kaggle/"
    echo ""
    
    read -p "Do you have Kaggle API configured? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Downloading from Kaggle..."
        python3 model/train_fer2013_improved.py --download
    else
        echo ""
        echo "📝 Manual download instructions:"
        echo "   1. Go to: https://www.kaggle.com/datasets/msambare/fer2013"
        echo "   2. Download fer2013.csv"
        echo "   3. Place it in: data/fer2013.csv"
        echo ""
        echo "   Or download from:"
        echo "   https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data"
        echo ""
        read -p "Press Enter after downloading the dataset..."
    fi
fi

# Verify dataset
if [ -f "data/fer2013.csv" ]; then
    echo "✅ Dataset verified!"
    
    # Show dataset info
    echo ""
    echo "📊 Dataset info:"
    wc -l data/fer2013.csv | awk '{print "   Total rows: " $1}'
    
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "🚀 Ready to train! Run:"
    echo "   python model/train_fer2013_improved.py"
    echo ""
    echo "⚙️  Training options:"
    echo "   --epochs 100        # Number of epochs (default: 100)"
    echo "   --batch_size 64     # Batch size (default: 64)"
    echo "   --learning_rate 0.001  # Learning rate (default: 0.001)"
    echo ""
    echo "📊 Expected results:"
    echo "   Training time: 2-4 hours (CPU) or 30-60 min (GPU)"
    echo "   Test accuracy: 65-70%"
    echo "   Model size: ~50 MB"
    echo ""
else
    echo "❌ Dataset not found. Please download manually."
    exit 1
fi
