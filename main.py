#!/usr/bin/env python3
"""
Main entry point for Driver Monitoring System
Can be run in GUI mode or command line mode
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add project directories to path
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "gui"))
sys.path.append(str(project_root / "utils"))

def setup_logging(log_level="INFO"):
    """Setup logging configuration"""
    # Create logs directory
    log_dir = project_root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_file = log_dir / "driver_monitoring.log"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'cv2', 'numpy', 'PIL', 'tkinter', 'mediapipe'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            elif package == 'tkinter':
                import tkinter
            elif package == 'mediapipe':
                import mediapipe
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def run_gui_mode():
    """Run in GUI mode"""
    try:
        from main_gui import DriverMonitoringGUI
        
        print("Starting Driver Monitoring System in GUI mode...")
        app = DriverMonitoringGUI()
        app.run()
        
    except ImportError as e:
        print(f"Error importing GUI modules: {e}")
        print("Please ensure all dependencies are installed")
        return False
    except Exception as e:
        print(f"Error running GUI: {e}")
        return False
    
    return True

def run_console_mode():
    """Run in console mode"""
    try:
        from main_detector import DriverMonitoringSystem
        import cv2
        import time
        
        print("Starting Driver Monitoring System in console mode...")
        print("Press 'q' to quit, 'p' to pause/resume, 'r' to reset")
        
        # Create and start monitoring system
        system = DriverMonitoringSystem()
        
        if not system.start():
            print("Failed to start monitoring system")
            return False
        
        try:
            while system.is_running:
                frame, results = system.process_frame()
                
                if frame is not None:
                    # Display frame
                    cv2.imshow('Driver Monitoring System', frame)
                    
                    # Print detection results
                    if results:
                        active_alerts = results.get('active_alerts', [])
                        if active_alerts:
                            print(f"Active alerts: {', '.join(active_alerts)}")
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('p'):
                        system.pause()
                    elif key == ord('r'):
                        system.reset_all_detectors()
                    elif key == ord('s'):
                        system.take_screenshot()
                        print("Screenshot saved")
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        finally:
            system.stop()
            cv2.destroyAllWindows()
            
    except ImportError as e:
        print(f"Error importing console modules: {e}")
        return False
    except Exception as e:
        print(f"Error running console mode: {e}")
        return False
    
    return True

def download_models():
    """Download required models"""
    try:
        from download_models import ModelDownloader
        
        print("Downloading required models...")
        downloader = ModelDownloader()
        downloader.download_all_models()
        
        print("Model download completed!")
        
    except Exception as e:
        print(f"Error downloading models: {e}")
        return False
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Driver Monitoring System")
    parser.add_argument("--mode", choices=["gui", "console"], default="gui",
                       help="Run mode (gui or console)")
    parser.add_argument("--download-models", action="store_true",
                       help="Download required models")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Logging level")
    parser.add_argument("--check-deps", action="store_true",
                       help="Check dependencies and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Driver Monitoring System")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Log level: {args.log_level}")
    
    # Check dependencies
    if args.check_deps:
        if check_dependencies():
            print("All dependencies are installed!")
            return 0
        else:
            return 1
    
    if not check_dependencies():
        return 1
    
    # Download models if requested
    if args.download_models:
        if not download_models():
            return 1
    
    # Run in specified mode
    try:
        if args.mode == "gui":
            success = run_gui_mode()
        else:
            success = run_console_mode()
        
        if success:
            logger.info("Driver Monitoring System shut down successfully")
            return 0
        else:
            logger.error("Driver Monitoring System encountered errors")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
