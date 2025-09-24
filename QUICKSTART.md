# Driver Monitoring System - Quick Start Guide

## What You Have

A complete computer vision-based driver monitoring system with:

### 🔍 Detection Features
- **Drowsiness Detection** - Eye closure monitoring
- **Distraction Detection** - Head pose and gaze tracking
- **Seatbelt Detection** - Visual seatbelt verification
- **Facial Recognition** - Authorized driver identification
- **Emotion Detection** - Stress and mood analysis
- **Hand Position** - Steering wheel grip monitoring
- **Attention Tracking** - Road focus verification

### 🎛️ Interface Options
- **GUI Mode** - Full-featured graphical interface
- **Console Mode** - Command-line operation
- **Real-time Alerts** - Audio and visual warnings
- **Configuration Panel** - Customizable settings

## Quick Start (macOS)

### 1. Environment Setup ✅ COMPLETED
The virtual environment is already activated and all dependencies are installed!

```bash
# Virtual environment: ✅ Activated
# Dependencies: ✅ All installed
# Camera access: ✅ Working
# System status: ✅ Ready to use
```

### 2. Quick Commands

```bash
# Check system status
python check_status.py

# Start with GUI (recommended)
./run_system.sh gui

# Start in console mode  
./run_system.sh console

# Run system tests
./run_system.sh test
```

### 3. Alternative Commands
```bash
# Direct Python commands (venv must be activated)
source venv/bin/activate

# GUI Mode (recommended)
python main.py --mode gui

# Console Mode
python main.py --mode console

# System tests
python test_system.py

# Download models first (optional)
python3 main.py --download-models
```

## Project Structure

```
driver monitering system/
├── main.py                    # 🚀 Main entry point
├── test_system.py            # 🧪 System tests
├── setup.sh / setup.bat      # ⚙️ Setup scripts
├── README.md                 # 📖 Full documentation
├── requirements.txt          # 📦 Dependencies
├── config/config.json        # ⚙️ Configuration
├── src/                      # 🔧 Detection modules
│   ├── main_detector.py      # Integration system
│   ├── drowsiness_detector.py
│   ├── distraction_detector.py
│   ├── seatbelt_detector.py
│   ├── facial_recognition.py
│   ├── emotion_detector.py
│   ├── hand_position_detector.py
│   ├── attention_detector.py
│   └── simple_drowsiness_detector.py
├── gui/main_gui.py           # 🖥️ GUI interface
├── utils/                    # 🛠️ Utilities
│   ├── alert_system.py
│   └── config_manager.py
├── models/                   # 🤖 AI models
├── data/                     # 💾 Data storage
│   ├── known_faces/          # Driver photos
│   ├── logs/                 # System logs
│   ├── screenshots/          # Saved images
│   └── recordings/           # Video files
```

## Usage Tips

### Adding Authorized Drivers
1. Start GUI mode
2. Position face in camera view
3. Tools → Add Driver Face
4. Enter name when prompted

### Adjusting Sensitivity
- Edit `config/config.json`
- Modify threshold values
- Restart application

### Troubleshooting
- **Camera issues**: Check other apps aren't using camera
- **Permission errors**: Allow camera access in System Preferences
- **Import errors**: Install missing packages with pip
- **Performance issues**: Lower resolution in config

## Key Commands

### GUI Mode
- Start/Stop monitoring buttons
- Configure detection modules via checkboxes
- Save screenshots and recordings
- View real-time detection status

### Console Mode
- `q` - Quit application
- `p` - Pause/resume monitoring
- `r` - Reset all detectors
- `s` - Save screenshot

## Advanced Features

### Custom Configuration
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
      "consecutive_frames": 20
    }
  }
}
```

### Video Recording
- Automatic recording on alerts
- Manual recording via GUI
- Configurable duration and quality

### Alert System
- Multiple alert types
- Customizable sounds
- Visual overlays
- Logging and history

## Safety Notes

⚠️ **Important**: This system is for research and development purposes. For production use in vehicles:

1. Test thoroughly in controlled environments
2. Ensure compliance with local regulations
3. Consider privacy implications
4. Have backup safety systems
5. Regular calibration and maintenance

## Support

For issues:
1. Run `python3 test_system.py` to diagnose problems
2. Check logs in `data/logs/`
3. Review configuration in `config/config.json`
4. Consult full README.md for detailed troubleshooting

---

**Ready to start monitoring? Run `python3 main.py --mode gui`** 🚗👁️
