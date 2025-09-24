# Driver Monitoring System

A comprehensive computer vision-based driver monitoring system that detects various safety conditions including drowsiness, distraction, seatbelt usage, facial recognition, emotion detection, hand position, and driver attention.

## Features

### Detection Capabilities
- **Drowsiness Detection**: Uses Eye Aspect Ratio (EAR) to detect when driver is getting drowsy
- **Distraction Detection**: Monitors head pose and gaze direction to detect driver distraction  
- **Seatbelt Detection**: Computer vision-based detection of seatbelt usage
- **Facial Recognition**: Identifies authorized drivers and alerts for unauthorized access
- **Emotion Detection**: Analyzes facial expressions to detect stress and emotional state
- **Hand Position Detection**: Monitors hand placement on steering wheel using MediaPipe
- **Attention Detection**: Tracks driver attention and gaze patterns

### Alert System
- Audio alerts for immediate safety warnings
- Visual alerts displayed on screen
- Configurable alert thresholds and sensitivity
- Alert logging and history tracking

### User Interface
- Modern GUI built with Tkinter
- Real-time video display with detection overlays
- Configuration panels for all detection modules
- Statistics and monitoring dashboard
- Console mode for headless operation

## Installation

### Prerequisites
- Python 3.7 or higher
- Webcam/camera device
- Sufficient lighting for face detection

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd "driver monitering system"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download required models**
   ```bash
   python download_models.py
   ```
   
   Or when running the main application:
   ```bash
   python main.py --download-models
   ```

4. **Check if all dependencies are installed**
   ```bash
   python main.py --check-deps
   ```

## Usage

### GUI Mode (Recommended)
```bash
python main.py --mode gui
```

### Console Mode
```bash
python main.py --mode console
```

### Command Line Options
```bash
python main.py --help
```

Available options:
- `--mode {gui,console}`: Choose interface mode
- `--download-models`: Download required detection models
- `--log-level {DEBUG,INFO,WARNING,ERROR}`: Set logging level
- `--check-deps`: Check if all dependencies are installed

## Configuration

The system uses `config/config.json` for configuration. Key settings include:

```json
{
  "camera": {
    "device_id": 0,
    "resolution": [640, 480],
    "fps": 30
  },
  "detection_settings": {
    "drowsiness": {
      "eye_aspect_ratio_threshold": 0.25,
      "consecutive_frames": 20,
      "enabled": true
    },
    "distraction": {
      "head_pose_threshold": 30,
      "consecutive_frames": 15, 
      "enabled": true
    }
  }
}
```

### Adding Known Drivers

For facial recognition:
1. Start the application in GUI mode
2. Position yourself in front of the camera
3. Go to Tools → Add Driver Face
4. Enter the driver name when prompted
5. The system will capture and save your face encoding

## Detection Modules

### Drowsiness Detection
- Monitors eye aspect ratio using facial landmarks
- Triggers alert when eyes are closed for extended period
- Configurable sensitivity and frame thresholds

### Distraction Detection  
- Uses MediaPipe for head pose estimation
- Detects when driver looks away from road
- Monitors yaw and pitch angles

### Seatbelt Detection
- Color-based detection in chest/shoulder region
- Edge detection for diagonal seatbelt patterns
- Configurable region of interest

### Facial Recognition
- Uses face_recognition library for encoding faces
- Supports multiple authorized drivers
- Real-time recognition with confidence scoring

### Emotion Detection
- Analyzes facial expressions
- Detects stress indicators (anger, fear, sadness)
- Optional: Custom emotion models can be trained

### Hand Position Detection
- MediaPipe hands tracking
- Monitors steering wheel region
- Detects proper grip and hand placement

### Attention Detection
- Gaze tracking using facial landmarks
- Defines road focus area
- Combines eye openness and gaze direction

## File Structure

```
driver monitering system/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── download_models.py      # Model downloader script
├── config/
│   └── config.json        # System configuration
├── src/                   # Detection modules
│   ├── main_detector.py   # Main integration system
│   ├── drowsiness_detector.py
│   ├── distraction_detector.py
│   ├── seatbelt_detector.py  
│   ├── facial_recognition.py
│   ├── emotion_detector.py
│   ├── hand_position_detector.py
│   └── attention_detector.py
├── gui/
│   └── main_gui.py        # Tkinter GUI application
├── utils/
│   ├── alert_system.py    # Alert management
│   └── config_manager.py  # Configuration handling
├── models/                # Detection models (downloaded)
├── data/
│   ├── known_faces/       # Authorized driver faces
│   ├── logs/             # System logs
│   ├── screenshots/      # Saved screenshots
│   └── recordings/       # Video recordings
```

## Models Used

The system downloads and uses several computer vision models:

- **OpenCV Haar Cascades**: Face and eye detection
- **Dlib Shape Predictor**: 68-point facial landmarks
- **MediaPipe**: Hand tracking and face mesh
- **Custom Models**: Emotion detection (optional)

## Troubleshooting

### Camera Issues
- Ensure camera is not being used by another application
- Try different camera device IDs (0, 1, 2, etc.)
- Check camera permissions on your system

### Model Loading Errors
- Run `python download_models.py` to ensure all models are downloaded
- Check internet connection for model downloads
- Verify model files exist in the `models/` directory

### Performance Issues
- Reduce camera resolution in config
- Disable unused detection modules
- Lower detection frame rates

### Import Errors
- Install all requirements: `pip install -r requirements.txt`
- Check Python version (3.7+ required)
- Some packages may need system-specific installation

## Development

### Adding New Detection Modules
1. Create new detector class in `src/`
2. Implement standard detection interface
3. Add to `main_detector.py` integration
4. Update configuration schema
5. Add GUI controls if needed

### Custom Alert Types
1. Define alert in `alert_system.py`
2. Add audio/visual assets
3. Update alert definitions dictionary
4. Test with `test_alerts()` method

## License

This project is for educational and research purposes. Please ensure compliance with local privacy and surveillance laws when deploying in real-world scenarios.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request with detailed description

## Support

For issues and questions:
1. Check troubleshooting section
2. Review system logs in `data/logs/`
3. Test with minimal configuration
4. Report bugs with system details and logs
# AI-Driver-Monitering-System
