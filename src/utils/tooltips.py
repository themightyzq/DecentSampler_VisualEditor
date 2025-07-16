"""
Comprehensive tooltip system for DecentSampler Frontend
Provides context-sensitive help and guidance for all UI elements
"""

# Main Window Tooltips
MAIN_WINDOW_TOOLTIPS = {
    "menu_file_new": "Create a new DecentSampler preset from scratch",
    "menu_file_open": "Open an existing .dspreset file for editing",
    "menu_file_save": "Save the current preset to a .dspreset file",
    "menu_edit_undo": "Undo the last action (Ctrl+Z)",
    "menu_edit_redo": "Redo the last undone action (Ctrl+Y)",
}

# Sample Mapping Tooltips
SAMPLE_MAPPING_TOOLTIPS = {
    "import_samples": "Import WAV files to use as samples in your preset",
    "auto_map": "Automatically map imported samples across the keyboard starting from the lowest note",
    "sample_list": "List of imported samples with their current key mappings. Click to select and edit.",
    "lo_note": "Lowest MIDI note that will trigger this sample (0-127)",
    "hi_note": "Highest MIDI note that will trigger this sample (0-127)", 
    "root_note": "The MIDI note at which this sample plays at its original pitch",
    "velocity_low": "Minimum velocity (0-127) required to trigger this sample",
    "velocity_high": "Maximum velocity (0-127) at which this sample will trigger",
}

# ADSR/Group Properties Tooltips
ADSR_TOOLTIPS = {
    "attack_enable": "Enable attack control for this preset",
    "attack_value": "Time in seconds for the sound to reach full volume after a key is pressed",
    "decay_enable": "Enable decay control for this preset", 
    "decay_value": "Time in seconds for the sound to decay from peak to sustain level",
    "sustain_enable": "Enable sustain control for this preset",
    "sustain_value": "Level (0.0-1.0) that the sound maintains while a key is held",
    "release_enable": "Enable release control for this preset",
    "release_value": "Time in seconds for the sound to fade to silence after a key is released",
}

# Project Properties Tooltips
PROJECT_TOOLTIPS = {
    "preset_name": "The name of your preset as it will appear in DecentSampler",
    "ui_width": "Width of the preset interface in pixels (recommended: 812)",
    "ui_height": "Height of the preset interface in pixels (recommended: 375)",
    "bg_color": "Background color of the preset interface (ARGB hex format)",
    "bg_image": "Optional background image file for the preset interface",
    "effects_list": "List of effect controls that will appear in your preset interface",
    "add_effect": "Add a new effect control to your preset interface",
    "edit_effect": "Edit the selected effect control properties",
    "delete_effect": "Remove the selected effect control from your preset",
}

# Modulation System Tooltips
MODULATION_TOOLTIPS = {
    "lfo_name": "Unique name for this LFO modulator",
    "lfo_frequency": "Speed of the LFO in Hz (cycles per second) when in free-running mode",
    "lfo_waveform": "Shape of the modulation wave:\n• Sine: Smooth, musical vibrato\n• Triangle: Linear up/down\n• Sawtooth: Sharp rise, instant fall\n• Square: On/off switching\n• S&H: Random stepped values\n• Envelope Follower: Follows input level",
    "lfo_amplitude": "Depth of modulation (0.0 = no effect, 1.0 = full range)",
    "lfo_offset": "DC offset added to the LFO output",
    "lfo_phase": "Starting phase of the waveform in degrees (0-360)",
    "lfo_sync": "Synchronization mode:\n• Free: Independent timing\n• Tempo: Locked to DAW tempo",
    "lfo_sync_length": "Note value for tempo sync (1/4 = quarter note, etc.)",
    "lfo_retrigger": "Whether the LFO restarts from phase 0 on each new note",
    
    "mod_matrix": "Matrix showing which LFOs modulate which parameters",
    "mod_lfo": "Source LFO for this modulation connection",
    "mod_target_type": "Type of parameter being modulated (amp, effect, general)",
    "mod_parameter": "Specific parameter to modulate (ENV_ATTACK, FX_MIX, etc.)",
    "mod_level": "Scope of modulation:\n• Instrument: Affects entire preset\n• Group: Affects specific sample group\n• Tag: Affects samples with specific tag",
    "mod_amount": "Strength of modulation (-10.0 to 10.0, negative values invert)",
    "mod_invert": "Invert the modulation signal (useful for creating opposite effects)",
}

# Sampling Features Tooltips
SAMPLING_TOOLTIPS = {
    "seq_mode": "Sample selection behavior:\n• Round-Robin: Cycles through samples in order\n• Random: Random selection with repetition\n• True Random: Random without immediate repetition\n• Always: Always plays this specific sample",
    "seq_position": "Position in the round-robin sequence (1-32)",
    "sample_volume": "Volume offset for this sample in dB (-60 to +20)",
    "sample_pan": "Pan position for this sample (-1.0 = left, 0 = center, 1.0 = right)",
    "sample_tune": "Pitch offset for this sample in cents (-1200 to +1200)",
    "sample_start": "Starting point in the sample file (sample offset)",
    "sample_end": "Ending point in the sample file (0 = end of file)",
    
    "loop_enabled": "Enable looping for this sample",
    "loop_start": "Sample position where the loop begins",
    "loop_end": "Sample position where the loop ends",
    "loop_crossfade": "Crossfade time in seconds between loop end and start",
    "loop_mode": "Loop playback mode:\n• Forward: Normal forward looping\n• Backward: Reverse looping\n• Bidirectional: Ping-pong looping",
}

# Keyboard Widget Tooltips
KEYBOARD_TOOLTIPS = {
    "keyboard_display": "Visual keyboard showing sample mappings and custom colors. Click keys to test playback.",
    "color_ranges": "Define custom colors for different key ranges to organize your samples visually",
    "add_color_range": "Add a new color range for a specific set of keys",
    "remove_color_range": "Remove the selected color range",
    "range_lo_note": "Lowest MIDI note for this color range",
    "range_hi_note": "Highest MIDI note for this color range", 
    "normal_color": "Color shown for keys in this range when not pressed",
    "pressed_color": "Color shown for keys in this range when pressed",
}

# XY Pad Tooltips
XY_PAD_TOOLTIPS = {
    "xy_pad": "2D control surface for simultaneous manipulation of two parameters. Drag the handle to adjust values.",
    "x_range_min": "Minimum value for the X-axis parameter",
    "x_range_max": "Maximum value for the X-axis parameter",
    "y_range_min": "Minimum value for the Y-axis parameter", 
    "y_range_max": "Maximum value for the Y-axis parameter",
    "pad_color": "Background color of the XY pad surface",
    "handle_color": "Color of the draggable control handle",
}

# Effects Tooltips
EFFECTS_TOOLTIPS = {
    "reverb": "Adds natural-sounding reverberation and spatial depth",
    "delay": "Creates echo effects with adjustable time and feedback",
    "chorus": "Thickens sound with modulated pitch and timing variations", 
    "filter": "Frequency filtering for tone shaping (lowpass, highpass, etc.)",
    "distortion": "Adds harmonic saturation and overdrive character",
    "compressor": "Controls dynamic range and punch",
    "eq": "Frequency equalization for detailed tone adjustment",
    "phaser": "Sweeping frequency modulation for movement effects",
    "flanger": "Jet-like sweeping effects with delayed signal mixing",
}

# General UI Tooltips
GENERAL_TOOLTIPS = {
    "preview_canvas": "Live preview of how your preset interface will appear in DecentSampler",
    "piano_keyboard": "Visual representation of the keyboard with current sample mappings",
    "status_bar": "Shows current operation status and helpful tips",
    "tabs": "Switch between different editing panels for various preset aspects",
}

# Quality of Life Tooltips
QOL_TOOLTIPS = {
    "workflow_tip": "💡 Tip: Follow the workflow steps shown in the status bar for best results",
    "save_reminder": "💾 Remember to save your work frequently to avoid data loss",
    "validation_tip": "✅ Green indicators show valid settings, red indicates errors that need fixing",
    "undo_tip": "↩️ Use Ctrl+Z/Ctrl+Y to undo/redo changes while editing",
    "preview_tip": "👁️ Use the preview panel to see how your preset will look in DecentSampler",
}

def get_tooltip_for_widget(widget_type, widget_name):
    """Get the appropriate tooltip for a widget"""
    tooltip_maps = {
        'main_window': MAIN_WINDOW_TOOLTIPS,
        'sample_mapping': SAMPLE_MAPPING_TOOLTIPS,
        'adsr': ADSR_TOOLTIPS,
        'project': PROJECT_TOOLTIPS,
        'modulation': MODULATION_TOOLTIPS,
        'sampling': SAMPLING_TOOLTIPS,
        'keyboard': KEYBOARD_TOOLTIPS,
        'xy_pad': XY_PAD_TOOLTIPS,
        'effects': EFFECTS_TOOLTIPS,
        'general': GENERAL_TOOLTIPS,
        'qol': QOL_TOOLTIPS,
    }
    
    tooltip_map = tooltip_maps.get(widget_type, {})
    return tooltip_map.get(widget_name, "")

def apply_tooltips_to_panel(panel, panel_type):
    """Apply all relevant tooltips to a panel"""
    tooltip_map = {
        'main_window': MAIN_WINDOW_TOOLTIPS,
        'sample_mapping': SAMPLE_MAPPING_TOOLTIPS,
        'adsr': ADSR_TOOLTIPS,
        'project': PROJECT_TOOLTIPS,
        'modulation': MODULATION_TOOLTIPS,
        'sampling': SAMPLING_TOOLTIPS,
        'keyboard': KEYBOARD_TOOLTIPS,
        'xy_pad': XY_PAD_TOOLTIPS,
        'effects': EFFECTS_TOOLTIPS,
        'general': GENERAL_TOOLTIPS,
    }.get(panel_type, {})
    
    for widget_name, tooltip_text in tooltip_map.items():
        widget = panel.findChild(type(panel), widget_name)
        if widget:
            widget.setToolTip(tooltip_text)

# Contextual help messages for complex workflows
WORKFLOW_HELP = {
    "getting_started": """
    🎵 Welcome to DecentSampler Preset Editor!
    
    Getting Started:
    1. Click 'Import' to add your WAV samples
    2. Use 'Auto Map' or manually assign key ranges
    3. Adjust ADSR envelope settings
    4. Add effects and modulation as needed
    5. Preview your preset in the center panel
    6. Save as .dspreset file when ready
    
    💡 Tip: Start with a simple preset and add complexity gradually.
    """,
    
    "modulation_setup": """
    🌊 Setting Up Modulation:
    
    1. Go to the Modulation panel
    2. Add an LFO in the LFOs tab
    3. Configure waveform, frequency, and amplitude
    4. Switch to Modulation Matrix tab
    5. Add a route connecting your LFO to a parameter
    6. Adjust the amount for desired effect strength
    
    💡 Tip: Start with subtle amounts (0.1-0.3) and increase gradually.
    """,
    
    "sampling_advanced": """
    🎛️ Advanced Sampling Features:
    
    Round-Robin: Use multiple samples for the same key to avoid machine-gun effect
    Velocity Layers: Different samples trigger based on how hard keys are pressed  
    Looping: For sustained sounds like pads and strings
    
    💡 Tip: Use round-robin for drums, velocity layers for piano/strings.
    """,
    
    "ui_design": """
    🎨 Designing Your Preset Interface:
    
    1. Set overall dimensions in Project Properties
    2. Add controls for parameters you want users to adjust
    3. Use keyboard colors to show key mappings visually
    4. Add XY pads for interesting 2D control
    5. Preview frequently to check layout
    
    💡 Tip: Less is often more - focus on the most important controls.
    """
}

def get_workflow_help(workflow_name):
    """Get help text for a specific workflow"""
    return WORKFLOW_HELP.get(workflow_name, "")

def create_tooltip_widget(tooltip_text, parent=None):
    """Create a rich tooltip widget with formatting"""
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtCore import Qt
    
    label = QLabel(tooltip_text, parent)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    label.setStyleSheet("""
        QLabel {
            background-color: rgba(50, 50, 50, 240);
            color: white;
            border: 1px solid #666;
            border-radius: 6px;
            padding: 8px;
            font-size: 11px;
            max-width: 300px;
        }
    """)
    return label