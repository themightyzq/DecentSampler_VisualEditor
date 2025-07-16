"""
Interactive tutorial dialog for understanding sample grouping concepts
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QTabWidget, QWidget, QScrollArea, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush

class GroupingTutorialDialog(QDialog):
    """Interactive tutorial explaining sample grouping concepts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sample Grouping Tutorial")
        self.setFixedSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🎵 Understanding Sample Groups in DecentSampler")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("padding: 10px; background-color: #4a9eff; color: white; border-radius: 5px;")
        layout.addWidget(header)
        
        # Create tabs for different concepts
        tabs = QTabWidget()
        
        # Tab 1: Overview
        overview_tab = self.create_overview_tab()
        tabs.addTab(overview_tab, "Overview")
        
        # Tab 2: Velocity Layers
        velocity_tab = self.create_velocity_tab()
        tabs.addTab(velocity_tab, "Velocity Layers")
        
        # Tab 3: Sample Blending
        blending_tab = self.create_blending_tab()
        tabs.addTab(blending_tab, "Sample Blending")
        
        # Tab 4: Simultaneous Layers
        layers_tab = self.create_layers_tab()
        tabs.addTab(layers_tab, "Simultaneous Layers")
        
        # Tab 5: Practice Examples
        examples_tab = self.create_examples_tab()
        tabs.addTab(examples_tab, "Examples")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Got It!")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("QPushButton { background-color: #51cf66; color: white; font-weight: bold; padding: 8px 16px; }")
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def create_overview_tab(self):
        """Create the overview tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Intro text
        intro = QTextEdit()
        intro.setReadOnly(True)
        intro.setMaximumHeight(200)
        intro.setHtml("""
        <h3>🎯 What Are Sample Groups?</h3>
        <p>Sample groups determine <b>which samples play when</b> and <b>how they interact</b>. Understanding groups is the key to creating expressive, professional sample libraries.</p>
        
        <h3>🔍 The Three Main Scenarios:</h3>
        <ul>
        <li><b>Velocity Layers:</b> Different samples based on playing intensity</li>
        <li><b>Sample Blending:</b> Multiple samples playing together with crossfade control</li>
        <li><b>Simultaneous Layers:</b> Multiple samples always playing together</li>
        </ul>
        """)
        layout.addWidget(intro)
        
        # Visual diagram
        diagram = self.create_overview_diagram()
        layout.addWidget(diagram)
        
        widget.setLayout(layout)
        return widget
        
    def create_velocity_tab(self):
        """Create the velocity layers explanation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Explanation
        explanation = QTextEdit()
        explanation.setReadOnly(True)
        explanation.setMaximumHeight(250)
        explanation.setHtml("""
        <h3>🎹 Velocity Layers: Dynamic Response</h3>
        <p><b>Goal:</b> Different samples trigger based on how hard you play the keys.</p>
        
        <h4>How It Works:</h4>
        <ul>
        <li><b>Multiple Groups</b> with the <b>same key ranges</b></li>
        <li>Each group has a <b>different velocity range</b></li>
        <li>Soft playing = Group 1, Hard playing = Group 3</li>
        </ul>
        
        <h4>Perfect For:</h4>
        <ul>
        <li>Piano samples (soft vs. loud playing)</li>
        <li>Drum hits (light taps vs. hard hits)</li>
        <li>Any instrument where playing dynamics matter</li>
        </ul>
        """)
        layout.addWidget(explanation)
        
        # Example setup
        example_group = QGroupBox("Example Setup")
        example_layout = QVBoxLayout()
        
        example_text = QLabel("""
📊 Piano Velocity Layers:

Group 1: "Soft Layer"     │ Velocity 0-42   │ Piano_C4_Soft.wav
Group 2: "Medium Layer"   │ Velocity 43-84  │ Piano_C4_Medium.wav  
Group 3: "Hard Layer"     │ Velocity 85-127 │ Piano_C4_Hard.wav

Result: Gentle press → Soft sample, Hard press → Hard sample
        """)
        example_text.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        example_layout.addWidget(example_text)
        
        example_group.setLayout(example_layout)
        layout.addWidget(example_group)
        
        # Setup instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(120)
        instructions.setHtml("""
        <h4>🛠️ How to Set Up in Your Editor:</h4>
        <ol>
        <li>Click <b>"Create Velocity Layers"</b> button</li>
        <li>Choose number of layers (2-4 recommended)</li>
        <li>Import samples for each dynamic level</li>
        <li>Assign samples to appropriate velocity groups</li>
        </ol>
        """)
        layout.addWidget(instructions)
        
        widget.setLayout(layout)
        return widget
        
    def create_blending_tab(self):
        """Create the sample blending explanation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Explanation
        explanation = QTextEdit()
        explanation.setReadOnly(True)
        explanation.setMaximumHeight(250)
        explanation.setHtml("""
        <h3>🎛️ Sample Blending: The BrokenPiano Technique</h3>
        <p><b>Goal:</b> Multiple samples play simultaneously with crossfade control.</p>
        
        <h4>How It Works:</h4>
        <ul>
        <li><b>Single Group</b> containing <b>multiple samples</b> for the same keys</li>
        <li>All samples play at once, but volumes controlled by <b>tags</b></li>
        <li>UI slider crossfades between tagged sample sets</li>
        </ul>
        
        <h4>Perfect For:</h4>
        <ul>
        <li>Close vs. distant microphone positions</li>
        <li>Guitar pickup blends (neck vs. bridge)</li>
        <li>Different recording perspectives of same performance</li>
        </ul>
        """)
        layout.addWidget(explanation)
        
        # BrokenPiano analysis
        analysis_group = QGroupBox("🔍 BrokenPiano Analysis")
        analysis_layout = QVBoxLayout()
        
        analysis_text = QLabel("""
🎹 BrokenPiano Structure:

Single Group: "Piano Blend"
├── Piano_C4_Close.wav    (tagged: "mic_close")
└── Piano_C4_Distant.wav  (tagged: "mic_distant")

UI Control: "Mic Blend" slider
├── At 0%:   Only close mic audible (distant = 0% volume)
├── At 50%:  Both mics at equal volume
└── At 100%: Only distant mic audible (close = 0% volume)

🎯 Both samples ALWAYS play together - the slider just changes their relative volumes!
        """)
        analysis_text.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        analysis_layout.addWidget(analysis_text)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Setup instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(120)
        instructions.setHtml("""
        <h4>🛠️ How to Set Up in Your Editor:</h4>
        <ol>
        <li>Click <b>"Create Blend Layers"</b> button</li>
        <li>Set up tags (e.g., "mic_close", "mic_distant")</li>
        <li>Add ALL samples to the SAME group</li>
        <li>Tag samples appropriately</li>
        <li>Create blend control with tag-based volume bindings</li>
        </ol>
        """)
        layout.addWidget(instructions)
        
        widget.setLayout(layout)
        return widget
        
    def create_layers_tab(self):
        """Create the simultaneous layers explanation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Explanation
        explanation = QTextEdit()
        explanation.setReadOnly(True)
        explanation.setMaximumHeight(200)
        explanation.setHtml("""
        <h3>🔊 Simultaneous Layers: Rich Textures</h3>
        <p><b>Goal:</b> Multiple samples always play together for rich, complex sounds.</p>
        
        <h4>How It Works:</h4>
        <ul>
        <li><b>Single Group</b> with multiple samples covering <b>same key range</b></li>
        <li>All samples trigger together when key is pressed</li>
        <li>Individual volumes can be adjusted for balance</li>
        </ul>
        
        <h4>Perfect For:</h4>
        <ul>
        <li>Layered pad sounds (analog + strings + choir)</li>
        <li>Orchestral sections (violins + violas + cellos)</li>
        <li>Complex textures that need multiple timbres</li>
        </ul>
        """)
        layout.addWidget(explanation)
        
        # Example setup
        example_group = QGroupBox("Example Setup")
        example_layout = QVBoxLayout()
        
        example_text = QLabel("""
🎵 Rich Pad Layers:

Group 1: "Layered Pad"
├── Analog_Pad_C4.wav     (Volume: 0.8)
├── String_Section_C4.wav (Volume: 0.6)  
└── Choir_Ah_C4.wav       (Volume: 0.4)

All samples: loNote=60, hiNote=60, rootNote=60

Result: Pressing C4 triggers ALL THREE samples simultaneously
        Creates a rich, complex timbre that's more than the sum of its parts
        """)
        example_text.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        example_layout.addWidget(example_text)
        
        example_group.setLayout(example_layout)
        layout.addWidget(example_group)
        
        # Tips
        tips = QTextEdit()
        tips.setReadOnly(True)
        tips.setMaximumHeight(150)
        tips.setHtml("""
        <h4>💡 Pro Tips:</h4>
        <ul>
        <li><b>Balance Carefully:</b> Adjust individual volumes to avoid muddy mix</li>
        <li><b>Complementary Timbres:</b> Choose sounds that enhance rather than compete</li>
        <li><b>Phase Relationships:</b> Be aware of phase cancellation between samples</li>
        <li><b>Frequency Content:</b> Layer sounds in different frequency ranges</li>
        </ul>
        
        <h4>🛠️ Setup: Add multiple samples to same group with identical key ranges</h4>
        """)
        layout.addWidget(tips)
        
        widget.setLayout(layout)
        return widget
        
    def create_examples_tab(self):
        """Create the examples tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        examples = QTextEdit()
        examples.setReadOnly(True)
        examples.setHtml("""
        <h3>🎼 Real-World Examples</h3>
        
        <h4>🎹 Piano Preset (Velocity Layers):</h4>
        <pre>
Group 1: "Piano Soft"    │ Velocity 0-42   │ Soft attack samples
Group 2: "Piano Medium"  │ Velocity 43-84  │ Medium attack samples
Group 3: "Piano Hard"    │ Velocity 85-127 │ Hard attack samples
        </pre>
        
        <h4>🎸 Guitar Preset (Sample Blending):</h4>
        <pre>
Group 1: "Guitar Blend"
├── Guitar_Neck_C4.wav   (tagged: "pickup_neck")
└── Guitar_Bridge_C4.wav (tagged: "pickup_bridge")
        
UI Control: "Pickup Blend" slider crossfades between positions
        </pre>
        
        <h4>🎺 Orchestral Preset (Simultaneous Layers):</h4>
        <pre>
Group 1: "Full Orchestra"
├── Violins_C4.wav       (Volume: 1.0)
├── Violas_C4.wav        (Volume: 0.8)
├── Cellos_C4.wav        (Volume: 0.6)
└── Basses_C4.wav        (Volume: 0.4)
        </pre>
        
        <h4>🥁 Drum Kit (Multiple Techniques):</h4>
        <pre>
Group 1: "Kick Soft"     │ Velocity 0-64   │ Kick_Soft.wav
Group 2: "Kick Hard"     │ Velocity 65-127 │ Kick_Hard.wav

Group 3: "Snare Layers"  │ All velocities
├── Snare_Close.wav      (tagged: "close")
└── Snare_Room.wav       (tagged: "room")
        </pre>
        
        <h3>🚀 Quick Setup Guide:</h3>
        <ol>
        <li><b>Identify your goal:</b> Dynamics? Blending? Layering?</li>
        <li><b>Choose the right technique</b> based on your samples</li>
        <li><b>Use the Group Manager</b> quick setup buttons</li>
        <li><b>Test and adjust</b> volumes and ranges</li>
        <li><b>Create UI controls</b> for user interaction</li>
        </ol>
        
        <div style="background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin-top: 10px;">
        <b>💡 Remember:</b> The goal is always <i>musical expression</i>. Choose the technique that best serves the music!
        </div>
        """)
        layout.addWidget(examples)
        
        widget.setLayout(layout)
        return widget
        
    def create_overview_diagram(self):
        """Create a visual diagram showing the three approaches"""
        frame = QFrame()
        frame.setFixedHeight(200)
        frame.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        
        # This would contain a custom painted diagram
        # For now, we'll use a text-based representation
        
        return frame

def show_grouping_tutorial(parent=None):
    """Show the grouping tutorial dialog"""
    dialog = GroupingTutorialDialog(parent)
    dialog.exec_()