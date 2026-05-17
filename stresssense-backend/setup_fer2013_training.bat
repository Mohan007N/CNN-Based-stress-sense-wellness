@echo off
REM setup_fer2013_training.bat — Setup FER2013 Training Environment (Windows)
REM ===========================================================================
REM Installs dependencies and downloads FER2013 dataset for CNN training

echo ==========================================
echo 🚀 FER2013 Training Setup (Windows)
echo ==========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment (optional but recommended)
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies...
pip install tensorflow>=2.10.0
pip install numpy pandas matplotlib seaborn scikit-learn
pip install kaggle

echo.
echo ==========================================
echo 📥 FER2013 Dataset Setup
echo ==========================================

REM Check if dataset already exists
if exist "data\fer2013.csv" (
    echo ✅ FER2013 dataset already exists at data\fer2013.csv
) else (
    echo 📥 Downloading FER2013 dataset...
    echo.
    echo ⚠️  You need a Kaggle account and API token:
    echo    1. Go to https://www.kaggle.com/settings
    echo    2. Click 'Create New API Token'
    echo    3. Place kaggle.json in %%USERPROFILE%%\.kaggle\
    echo.
    
    set /p KAGGLE_READY="Do you have Kaggle API configured? (y/n): "
    
    if /i "%KAGGLE_READY%"=="y" (
        echo 📥 Downloading from Kaggle...
        python model\train_fer2013_improved.py --download
    ) else (
        echo.
        echo 📝 Manual download instructions:
        echo    1. Go to: https://www.kaggle.com/datasets/msambare/fer2013
        echo    2. Download fer2013.csv
        echo    3. Place it in: data\fer2013.csv
        echo.
        echo    Or download from:
        echo    https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data
        echo.
        pause
    )
)

REM Verify dataset
if exist "data\fer2013.csv" (
    echo ✅ Dataset verified!
    
    echo.
    echo ==========================================
    echo ✅ Setup Complete!
    echo ==========================================
    echo.
    echo 🚀 Ready to train! Run:
    echo    python model\train_fer2013_improved.py
    echo.
    echo ⚙️  Training options:
    echo    --epochs 100        # Number of epochs (default: 100^)
    echo    --batch_size 64     # Batch size (default: 64^)
    echo    --learning_rate 0.001  # Learning rate (default: 0.001^)
    echo.
    echo 📊 Expected results:
    echo    Training time: 2-4 hours (CPU^) or 30-60 min (GPU^)
    echo    Test accuracy: 65-70%%
    echo    Model size: ~50 MB
    echo.
) else (
    echo ❌ Dataset not found. Please download manually.
    pause
    exit /b 1
)

pause
