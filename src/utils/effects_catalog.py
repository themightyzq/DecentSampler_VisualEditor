# DecentSampler Effects Catalog
# This module defines all supported effects, their parameters, and sensible defaults for both simple and advanced modes.

EFFECTS_CATALOG = {
    "Reverb": {
        "type": "reverb",
        "simple": [
            {"name": "wetLevel", "label": "Amount", "min": 0.0, "max": 1.0, "default": 0.5, "ds_param": "FX_REVERB_WET_LEVEL"}
        ],
        "advanced": [
            {"name": "wetLevel", "label": "Wet Level", "min": 0.0, "max": 1.0, "default": 0.5, "ds_param": "FX_REVERB_WET_LEVEL"},
            {"name": "roomSize", "label": "Room Size", "min": 0.0, "max": 1.0, "default": 0.7},
            {"name": "damping", "label": "Damping", "min": 0.0, "max": 1.0, "default": 0.3}
        ]
    },
    "Delay": {
        "type": "delay",
        "simple": [
            {"name": "wetLevel", "label": "Amount", "min": 0.0, "max": 1.0, "default": 0.5}
        ],
        "advanced": [
            {"name": "wetLevel", "label": "Wet Level", "min": 0.0, "max": 1.0, "default": 0.5},
            {"name": "delayTime", "label": "Delay Time (s)", "min": 0.0, "max": 20.0, "default": 0.7},
            {"name": "feedback", "label": "Feedback", "min": 0.0, "max": 1.0, "default": 0.2},
            {"name": "stereoOffset", "label": "Stereo Offset", "min": -10.0, "max": 10.0, "default": 0.0},
            {"name": "delayTimeFormat", "label": "Time Format", "options": ["seconds", "musical_time"], "default": "seconds"}
        ]
    },
    "Chorus": {
        "type": "chorus",
        "simple": [
            {"name": "mix", "label": "Amount", "min": 0.0, "max": 1.0, "default": 0.5, "ds_param": "FX_MIX"}
        ],
        "advanced": [
            {"name": "mix", "label": "Mix", "min": 0.0, "max": 1.0, "default": 0.5, "ds_param": "FX_MIX"},
            {"name": "modDepth", "label": "Mod Depth", "min": 0.0, "max": 1.0, "default": 0.2},
            {"name": "modRate", "label": "Mod Rate (Hz)", "min": 0.0, "max": 10.0, "default": 0.2}
        ]
    },
    "Phaser": {
        "type": "phaser",
        "simple": [
            {"name": "mix", "label": "Amount", "min": 0.0, "max": 1.0, "default": 0.5}
        ],
        "advanced": [
            {"name": "mix", "label": "Mix", "min": 0.0, "max": 1.0, "default": 0.5},
            {"name": "modDepth", "label": "Mod Depth", "min": 0.0, "max": 1.0, "default": 0.2},
            {"name": "modRate", "label": "Mod Rate (Hz)", "min": 0.0, "max": 10.0, "default": 0.2},
            {"name": "centerFrequency", "label": "Center Freq (Hz)", "min": 0.0, "max": 22000.0, "default": 400.0},
            {"name": "feedback", "label": "Feedback", "min": -1.0, "max": 1.0, "default": 0.7}
        ]
    },
    "Convolution": {
        "type": "convolution",
        "simple": [
            {"name": "mix", "label": "Amount", "min": 0.0, "max": 1.0, "default": 0.5}
        ],
        "advanced": [
            {"name": "mix", "label": "Mix", "min": 0.0, "max": 1.0, "default": 0.5},
            {"name": "irFile", "label": "Impulse Response File", "type": "file", "default": ""}
        ]
    },
    "Lowpass": {
        "type": "lowpass",
        "simple": [
            {"name": "frequency", "label": "Cutoff", "min": 0.0, "max": 22000.0, "default": 22000.0, "ds_param": "FX_FILTER_FREQUENCY"}
        ],
        "advanced": [
            {"name": "frequency", "label": "Cutoff", "min": 0.0, "max": 22000.0, "default": 22000.0, "ds_param": "FX_FILTER_FREQUENCY"},
            {"name": "resonance", "label": "Resonance", "min": 0.0, "max": 1.0, "default": 0.7}
        ]
    },
    "Highpass": {
        "type": "highpass",
        "simple": [
            {"name": "frequency", "label": "Cutoff", "min": 0.0, "max": 22000.0, "default": 22000.0}
        ],
        "advanced": [
            {"name": "frequency", "label": "Cutoff", "min": 0.0, "max": 22000.0, "default": 22000.0},
            {"name": "resonance", "label": "Resonance", "min": 0.0, "max": 1.0, "default": 0.7}
        ]
    },
    "Bandpass": {
        "type": "bandpass",
        "simple": [
            {"name": "frequency", "label": "Center Freq", "min": 0.0, "max": 22000.0, "default": 22000.0}
        ],
        "advanced": [
            {"name": "frequency", "label": "Center Freq", "min": 0.0, "max": 22000.0, "default": 22000.0},
            {"name": "resonance", "label": "Resonance", "min": 0.0, "max": 1.0, "default": 0.7}
        ]
    },
    "Notch": {
        "type": "notch",
        "simple": [
            {"name": "frequency", "label": "Freq", "min": 60.0, "max": 22000.0, "default": 10000.0}
        ],
        "advanced": [
            {"name": "frequency", "label": "Freq", "min": 60.0, "max": 22000.0, "default": 10000.0},
            {"name": "q", "label": "Q", "min": 0.01, "max": 18.0, "default": 0.7}
        ]
    },
    "Peak": {
        "type": "peak",
        "simple": [
            {"name": "frequency", "label": "Freq", "min": 60.0, "max": 22000.0, "default": 10000.0}
        ],
        "advanced": [
            {"name": "frequency", "label": "Freq", "min": 60.0, "max": 22000.0, "default": 10000.0},
            {"name": "q", "label": "Q", "min": 0.01, "max": 18.0, "default": 0.7},
            {"name": "gain", "label": "Gain", "min": 0.0, "max": 10.0, "default": 1.0}
        ]
    },
    "Gain": {
        "type": "gain",
        "simple": [
            {"name": "level", "label": "Level (dB)", "min": -99.0, "max": 24.0, "default": 0.0}
        ],
        "advanced": [
            {"name": "level", "label": "Level (dB)", "min": -99.0, "max": 24.0, "default": 0.0}
        ]
    },
    "Wave Folder": {
        "type": "wave_folder",
        "simple": [
            {"name": "drive", "label": "Drive", "min": 1.0, "max": 100.0, "default": 1.0}
        ],
        "advanced": [
            {"name": "drive", "label": "Drive", "min": 1.0, "max": 100.0, "default": 1.0},
            {"name": "threshold", "label": "Threshold", "min": 0.0, "max": 10.0, "default": 0.25}
        ]
    },
    "Wave Shaper": {
        "type": "wave_shaper",
        "simple": [
            {"name": "drive", "label": "Drive", "min": 1.0, "max": 1000.0, "default": 1.0}
        ],
        "advanced": [
            {"name": "drive", "label": "Drive", "min": 1.0, "max": 1000.0, "default": 1.0},
            {"name": "driveBoost", "label": "Drive Boost", "min": 0.0, "max": 1.0, "default": 1.0},
            {"name": "outputLevel", "label": "Output Level", "min": 0.0, "max": 1.0, "default": 0.1},
            {"name": "highQuality", "label": "High Quality", "type": "bool", "default": True}
        ]
    }
}
