#!/usr/bin/env python3
"""
Test script for the DecentSampler transposition system
Demonstrates the calculation and visualization features
"""

import sys
import os
sys.path.insert(0, 'src')

from utils.audio_transposition import get_transposition_engine, SampleTranspositionWidget
from widgets.transposition_controls import TranspositionControlWidget
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def test_transposition_calculations():
    """Test the transposition calculation system"""
    print("🎵 Testing DecentSampler Transposition System")
    print("=" * 50)
    
    engine = get_transposition_engine()
    
    # Test scenarios
    test_cases = [
        {"name": "Piano C4 Sample", "root": 60, "played": [48, 60, 72]},
        {"name": "Guitar E2 Sample", "root": 40, "played": [40, 52, 64]},
        {"name": "Violin A3 Sample", "root": 57, "played": [57, 69, 81]},
    ]
    
    for case in test_cases:
        print(f"\n📊 {case['name']} (Root: {SampleTranspositionWidget.get_note_name(case['root'])})")
        print("-" * 30)
        
        for played_note in case['played']:
            info = engine.get_transposition_info(played_note, case['root'])
            
            played_name = SampleTranspositionWidget.get_note_name(played_note)
            root_name = SampleTranspositionWidget.get_note_name(case['root'])
            
            if info['direction'] == 'none':
                print(f"  {played_name}: 🎵 Original pitch (no transposition)")
            else:
                direction = "↑" if info['direction'] == 'up' else "↓"
                print(f"  {played_name}: {direction} {info['semitones']} semitones (ratio: {info['pitch_ratio']:.3f})")
    
    # Test capabilities
    print(f"\n🔧 Engine Capabilities:")
    print("-" * 20)
    capabilities = engine.get_capabilities()
    print(f"Method: {capabilities['quality']}")
    print(f"Can transpose: {capabilities['can_transpose']}")
    
    if capabilities['recommendations']:
        print("\n💡 Recommendations:")
        for rec in capabilities['recommendations']:
            print(f"  • {rec}")

def create_test_gui():
    """Create a test GUI showing transposition controls"""
    app = QApplication(sys.argv)
    
    # Main window
    window = QWidget()
    window.setWindowTitle("DecentSampler Transposition Test")
    window.resize(600, 400)
    
    layout = QVBoxLayout()
    
    # Header
    header = QLabel("🎵 DecentSampler Transposition System Test")
    header.setFont(QFont("Arial", 16, QFont.Bold))
    header.setAlignment(Qt.AlignCenter)
    header.setStyleSheet("color: #4a9eff; padding: 10px;")
    layout.addWidget(header)
    
    # Create mock sample mapping
    mock_mapping = {
        'lo': 48,
        'hi': 72,
        'root': 60,
        'path': 'Piano_C4.wav',
        'tune': 0.0
    }
    
    # Transposition controls
    controls = TranspositionControlWidget()
    controls.set_mapping(mock_mapping)
    layout.addWidget(controls)
    
    # Instructions
    instructions = QLabel("""
    <b>Instructions:</b>
    <ul>
    <li>Adjust the root note to see how transposition changes</li>
    <li>Use fine tuning to adjust cents</li>
    <li>Select different test notes to preview transposition</li>
    <li>Click Play to hear the result (if audio libraries are installed)</li>
    </ul>
    
    <b>Visual Indicators:</b>
    <ul>
    <li>↑ Green arrows show notes pitched up from root</li>
    <li>↓ Red arrows show notes pitched down from root</li>
    <li>🔸 Red diamonds mark the root note</li>
    </ul>
    """)
    instructions.setWordWrap(True)
    instructions.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
    layout.addWidget(instructions)
    
    window.setLayout(layout)
    
    # Apply dark theme
    window.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: white;
        }
        QLabel {
            color: white;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #404040;
            color: white;
            border: 1px solid #555;
            padding: 2px;
        }
        QPushButton {
            background-color: #4a9eff;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #5ba0ff;
        }
    """)
    
    window.show()
    
    print("\n🎹 GUI Test Window Created!")
    print("Adjust the controls to see real-time transposition calculations.")
    
    return app.exec_()

if __name__ == "__main__":
    # Run calculation tests
    test_transposition_calculations()
    
    # Ask user if they want to see the GUI
    print(f"\n{'='*50}")
    response = input("Would you like to see the GUI test? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        create_test_gui()
    else:
        print("Test completed! ✅")