"""
model/download_datasets.py — Download Facial Emotion Datasets
==============================================================
Download and prepare popular facial emotion recognition datasets.

Supported datasets:
    - FER2013 (Facial Expression Recognition 2013)
    - CK+ (Extended Cohn-Kanade)
    - JAFFE (Japanese Female Facial Expression)
    - Sample datasets for testing

Usage:
    python model/download_datasets.py --dataset fer2013
    python model/download_datasets.py --dataset all
"""

import os
import sys
import argparse
import urllib.request
import zipfile
import tarfile
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')


# ══════════════════════════════════════════════════════════════════════════════
# DATASET INFORMATION
# ══════════════════════════════════════════════════════════════════════════════

DATASETS = {
    'fer2013': {
        'name': 'FER2013',
        'description': 'Facial Expression Recognition 2013 Challenge',
        'samples': '35,887 grayscale images (48x48)',
        'emotions': '7 emotions (angry, disgust, fear, happy, sad, surprise, neutral)',
        'kaggle_url': 'https://www.kaggle.com/datasets/msambare/fer2013',
        'manual': True,
        'instructions': """
📥 FER2013 Dataset Download Instructions:

1. Go to: https://www.kaggle.com/datasets/msambare/fer2013
2. Click "Download" (requires Kaggle account)
3. Extract the downloaded ZIP file
4. Copy 'fer2013.csv' to: {data_dir}/fer2013.csv

Alternative (Kaggle API):
    kaggle datasets download -d msambare/fer2013
    unzip fer2013.zip -d {data_dir}
"""
    },
    
    'ckplus': {
        'name': 'CK+ (Extended Cohn-Kanade)',
        'description': 'Extended Cohn-Kanade Database',
        'samples': '593 sequences from 123 subjects',
        'emotions': '7 emotions',
        'url': 'http://www.consortium.ri.cmu.edu/ckagree/',
        'manual': True,
        'instructions': """
📥 CK+ Dataset Download Instructions:

1. Go to: http://www.consortium.ri.cmu.edu/ckagree/
2. Fill out the request form
3. Download the dataset after approval
4. Extract to: {data_dir}/CK+/
"""
    },
    
    'jaffe': {
        'name': 'JAFFE',
        'description': 'Japanese Female Facial Expression Database',
        'samples': '213 images of 10 Japanese female models',
        'emotions': '7 emotions',
        'url': 'https://zenodo.org/record/3451524',
        'manual': True,
        'instructions': """
📥 JAFFE Dataset Download Instructions:

1. Go to: https://zenodo.org/record/3451524
2. Download the dataset
3. Extract to: {data_dir}/jaffe/
"""
    },
    
    'sample': {
        'name': 'Sample Dataset',
        'description': 'Small sample dataset for testing',
        'samples': '~100 images',
        'emotions': '7 emotions',
        'auto': True,
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_sample_dataset():
    """
    Create a small sample dataset for testing.
    Uses synthetic/placeholder images.
    """
    print("🎨 Creating sample dataset...")
    
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        print("❌ PIL required. Install with: pip install Pillow")
        return False
    
    sample_dir = os.path.join(DATA_DIR, 'sample_emotions')
    os.makedirs(sample_dir, exist_ok=True)
    
    emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    
    for emotion in emotions:
        emotion_dir = os.path.join(sample_dir, emotion)
        os.makedirs(emotion_dir, exist_ok=True)
        
        # Generate 15 sample images per emotion
        for i in range(15):
            # Create a simple grayscale image with random patterns
            img_array = np.random.randint(0, 256, (48, 48), dtype=np.uint8)
            
            # Add some structure (circles, lines) to make it look more face-like
            center = (24, 24)
            for y in range(48):
                for x in range(48):
                    dist = np.sqrt((x - center[0])**2 + (y - center[1])**2)
                    if dist < 20:
                        img_array[y, x] = min(255, img_array[y, x] + 50)
            
            img = Image.fromarray(img_array, mode='L')
            img.save(os.path.join(emotion_dir, f'{emotion}_{i:03d}.png'))
    
    print(f"✅ Sample dataset created at: {sample_dir}")
    print(f"   {len(emotions)} emotions × 15 images = {len(emotions) * 15} total images")
    
    return True


def download_with_progress(url, dest_path):
    """Download file with progress bar."""
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r   Downloading... {percent}%")
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, dest_path, reporthook)
    print()  # New line after progress


def show_dataset_info(dataset_name):
    """Display information about a dataset."""
    if dataset_name not in DATASETS:
        print(f"❌ Unknown dataset: {dataset_name}")
        return
    
    info = DATASETS[dataset_name]
    
    print("\n" + "=" * 60)
    print(f"📊 {info['name']}")
    print("=" * 60)
    print(f"Description: {info['description']}")
    print(f"Samples:     {info['samples']}")
    print(f"Emotions:    {info['emotions']}")
    
    if info.get('manual'):
        print("\n⚠️  Manual download required")
        print(info['instructions'].format(data_dir=DATA_DIR))
    
    print("=" * 60)


# ══════════════════════════════════════════════════════════════════════════════
# KAGGLE API INTEGRATION
# ══════════════════════════════════════════════════════════════════════════════

def download_fer2013_kaggle():
    """
    Download FER2013 using Kaggle API.
    Requires: pip install kaggle
    """
    try:
        import kaggle
    except ImportError:
        print("❌ Kaggle API not installed")
        print("   Install with: pip install kaggle")
        print("   Setup: https://github.com/Kaggle/kaggle-api#api-credentials")
        return False
    
    print("📥 Downloading FER2013 from Kaggle...")
    
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Download dataset
        kaggle.api.dataset_download_files(
            'msambare/fer2013',
            path=DATA_DIR,
            unzip=True
        )
        
        print(f"✅ FER2013 downloaded to: {DATA_DIR}")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("\n💡 Alternative: Download manually from:")
        print("   https://www.kaggle.com/datasets/msambare/fer2013")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# DATASET PREPARATION
# ══════════════════════════════════════════════════════════════════════════════

def prepare_fer2013():
    """Check if FER2013 is ready to use."""
    fer_csv = os.path.join(DATA_DIR, 'fer2013.csv')
    
    if os.path.exists(fer_csv):
        print(f"✅ FER2013 dataset found at: {fer_csv}")
        
        # Check file size
        size_mb = os.path.getsize(fer_csv) / (1024 * 1024)
        print(f"   File size: {size_mb:.1f} MB")
        
        # Count lines
        with open(fer_csv, 'r') as f:
            lines = sum(1 for _ in f)
        print(f"   Samples: {lines - 1:,} (excluding header)")
        
        return True
    else:
        print(f"❌ FER2013 not found at: {fer_csv}")
        show_dataset_info('fer2013')
        return False


def verify_custom_dataset(data_dir):
    """Verify custom dataset structure."""
    if not os.path.exists(data_dir):
        print(f"❌ Directory not found: {data_dir}")
        return False
    
    emotions = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    
    if not emotions:
        print(f"❌ No emotion folders found in: {data_dir}")
        print("\n📁 Expected structure:")
        print("   data_dir/")
        print("       angry/")
        print("           img1.jpg")
        print("       happy/")
        print("           img1.jpg")
        print("       ...")
        return False
    
    print(f"✅ Custom dataset found at: {data_dir}")
    print(f"   Emotions: {emotions}")
    
    total_images = 0
    for emotion in emotions:
        emotion_path = os.path.join(data_dir, emotion)
        images = [f for f in os.listdir(emotion_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"   {emotion}: {len(images)} images")
        total_images += len(images)
    
    print(f"   Total: {total_images} images")
    
    return True


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Download facial emotion datasets")
    parser.add_argument(
        '--dataset',
        choices=['fer2013', 'ckplus', 'jaffe', 'sample', 'all', 'info'],
        default='info',
        help='Dataset to download or info to show all'
    )
    parser.add_argument(
        '--use_kaggle',
        action='store_true',
        help='Use Kaggle API for FER2013 (requires kaggle package)'
    )
    parser.add_argument(
        '--verify',
        type=str,
        help='Verify custom dataset at specified path'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📥 Facial Emotion Dataset Downloader")
    print("=" * 60)
    
    # Create data directory
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Data directory: {DATA_DIR}\n")
    
    # Verify custom dataset
    if args.verify:
        verify_custom_dataset(args.verify)
        return
    
    # Show info for all datasets
    if args.dataset == 'info':
        for dataset_name in ['fer2013', 'ckplus', 'jaffe', 'sample']:
            show_dataset_info(dataset_name)
        return
    
    # Download specific dataset
    if args.dataset == 'fer2013':
        if args.use_kaggle:
            download_fer2013_kaggle()
        else:
            show_dataset_info('fer2013')
            print("\n💡 Tip: Use --use_kaggle flag to download via Kaggle API")
        prepare_fer2013()
    
    elif args.dataset == 'sample':
        create_sample_dataset()
    
    elif args.dataset in ['ckplus', 'jaffe']:
        show_dataset_info(args.dataset)
    
    elif args.dataset == 'all':
        print("📥 Downloading all available datasets...\n")
        
        # Sample dataset (auto)
        create_sample_dataset()
        
        # FER2013 (manual or Kaggle)
        print()
        if args.use_kaggle:
            download_fer2013_kaggle()
        else:
            show_dataset_info('fer2013')
        
        # Others (manual)
        for dataset in ['ckplus', 'jaffe']:
            print()
            show_dataset_info(dataset)
    
    print("\n✅ Done!")
    print(f"\n📁 Datasets location: {DATA_DIR}")
    print("\n🚀 Next steps:")
    print("   1. Download required datasets (see instructions above)")
    print("   2. Train CNN model:")
    print("      python model/train_emotion_cnn.py --dataset fer2013 --epochs 50")


if __name__ == "__main__":
    main()
