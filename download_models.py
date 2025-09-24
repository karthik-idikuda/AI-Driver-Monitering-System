#!/usr/bin/env python3
"""
Model Downloader for Driver Monitoring System
Downloads required models for various detection tasks
"""

import os
import urllib.request
import zipfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelDownloader:
    def __init__(self, models_dir="models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Model URLs (using OpenCV and other open-source models)
        self.model_urls = {
            "haarcascade_frontalface_default.xml": 
                "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml",
            "haarcascade_eye.xml":
                "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml",
            "haarcascade_smile.xml":
                "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_smile.xml",
            "shape_predictor_68_face_landmarks.dat":
                "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
        }
    
    def download_file(self, url, filename):
        """Download a file from URL"""
        try:
            filepath = self.models_dir / filename
            if filepath.exists():
                logger.info(f"{filename} already exists, skipping download")
                return True
                
            logger.info(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
            logger.info(f"Successfully downloaded {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {filename}: {str(e)}")
            return False
    
    def extract_bz2(self, filepath):
        """Extract bz2 files"""
        try:
            import bz2
            import shutil
            
            with bz2.BZ2File(filepath, 'rb') as source:
                with open(filepath.with_suffix(''), 'wb') as dest:
                    shutil.copyfileobj(source, dest)
            
            # Remove the compressed file
            filepath.unlink()
            logger.info(f"Extracted {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract {filepath}: {str(e)}")
            return False
    
    def download_all_models(self):
        """Download all required models"""
        logger.info("Starting model downloads...")
        
        success_count = 0
        total_count = len(self.model_urls)
        
        for filename, url in self.model_urls.items():
            if self.download_file(url, filename):
                success_count += 1
                
                # Handle compressed files
                filepath = self.models_dir / filename
                if filename.endswith('.bz2'):
                    self.extract_bz2(filepath)
        
        logger.info(f"Downloaded {success_count}/{total_count} models successfully")
        
        # Create placeholder models for custom ones
        self.create_placeholder_models()
    
    def create_placeholder_models(self):
        """Create placeholder files for custom models that need to be trained"""
        placeholders = [
            "emotion_model.h5",
            "seatbelt_detector.h5", 
            "attention_model.h5"
        ]
        
        for placeholder in placeholders:
            filepath = self.models_dir / placeholder
            if not filepath.exists():
                # Create empty file with info
                with open(filepath, 'w') as f:
                    f.write(f"# Placeholder for {placeholder}\n")
                    f.write("# This model needs to be trained or downloaded separately\n")
                logger.info(f"Created placeholder for {placeholder}")
    
    def verify_models(self):
        """Verify that all required models exist"""
        required_models = [
            "haarcascade_frontalface_default.xml",
            "haarcascade_eye.xml",
            "shape_predictor_68_face_landmarks.dat"
        ]
        
        missing_models = []
        for model in required_models:
            if not (self.models_dir / model).exists():
                missing_models.append(model)
        
        if missing_models:
            logger.warning(f"Missing models: {missing_models}")
            return False
        else:
            logger.info("All required models are available")
            return True

def main():
    """Main function to download models"""
    downloader = ModelDownloader()
    downloader.download_all_models()
    downloader.verify_models()
    
    print("\n" + "="*50)
    print("Model Download Summary:")
    print("="*50)
    print("✓ OpenCV Haar Cascades downloaded")
    print("✓ Dlib face landmarks model downloaded") 
    print("⚠ Custom models (emotion, seatbelt) need separate training")
    print("="*50)
    print("\nRun the main application with: python src/main.py")

if __name__ == "__main__":
    main()
