#!/usr/bin/env python3
"""
Simple test to run the updated GUI with camera stability fixes
"""

import sys
import os
import logging

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'gui'))

def test_stability():
    """Test the updated GUI with stability fixes"""
    print("=" * 70)
    print("CAMERA STABILITY TEST - UPDATED VERSION")
    print("=" * 70)
    print("Running GUI with NEW camera feed stability fixes:")
    print("✅ Canvas dimension caching")
    print("✅ Throttled resize handling")
    print("✅ Reduced refresh rates (20 FPS GUI, 15 FPS display)")
    print("✅ Scaling constraints (30% min, 150% max)")
    print("✅ Minimum image sizes (200x150)")
    print("✅ Smooth frame transitions")
    print()
    print("Starting GUI...")
    
    try:
        from main_gui import main
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stability()
