#!/usr/bin/env python3
"""
Test the Advanced Animated GUI with Enhanced Visual Effects
"""

import sys
import os
import logging

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'gui'))

def test_advanced_gui():
    """Test the advanced animated GUI"""
    print("=" * 80)
    print("🚀 ADVANCED ANIMATED DRIVER MONITORING SYSTEM")
    print("=" * 80)
    print("Launching enhanced GUI with advanced animations and features:")
    print()
    print("✨ NEW FEATURES:")
    print("  🎨 Modern glassmorphism design")
    print("  🌈 Smooth color transitions and gradients")
    print("  💫 Pulsing status indicators")
    print("  🔄 Animated borders and glows")
    print("  📹 Enhanced camera feed with effects")
    print("  🎯 Interactive click ripple effects")
    print("  🔍 Zoom in/out with smooth scaling")
    print("  ✨ Visual effects toggle")
    print("  🎛️ Animated control buttons")
    print("  📊 Real-time performance indicators")
    print("  🔔 Enhanced alert animations")
    print("  ⚙️ Smart detection presets")
    print()
    print("🎮 INTERACTIVE FEATURES:")
    print("  • Click on camera feed for ripple effects")
    print("  • Use zoom controls for camera zoom")
    print("  • Toggle effects for enhanced visuals")
    print("  • Watch status indicators pulse and glow")
    print("  • Enjoy smooth hover animations on buttons")
    print()
    print("Starting advanced GUI...")
    print()
    
    try:
        from main_gui import main
        main()
    except KeyboardInterrupt:
        print("\n🛑 GUI closed by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_advanced_gui()
