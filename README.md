# DecentSampler Visual Editor

A cross-platform desktop application for visually editing DecentSampler `.dspreset` files. Built with Python and PyQt5.

## Features

- Visual editor for DecentSampler XML features (samples, groups, effects, modulation)
- Piano keyboard widget with note-range visualization
- Dark theme with accessibility support
- Background-threaded file I/O
- Graceful degradation when optional audio packages are missing

## Getting Started

### Prerequisites

- Python 3.7+

### Installation

```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt  # Optional: pygame, numpy, librosa, pydub, soundfile
```

### Running

```bash
cd src && python main.py
```

### Testing

```bash
pip install pytest
cd src && python -m pytest ../tests/ -v
```

### Distribution (Standalone Executable)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

## Architecture

```
src/
├── main.py                      # Entry point
├── model.py                     # Backward-compat shim (re-exports from models/)
├── models/                      # Data model classes
│   ├── data_classes.py          # SampleZone, SampleMapping, LFO, UIElement, etc.
│   └── instrument_preset.py     # InstrumentPreset (core preset object)
├── serialization/               # XML I/O
│   ├── dspreset_reader.py       # .dspreset XML → InstrumentPreset
│   └── dspreset_writer.py       # InstrumentPreset → .dspreset XML
├── views/
│   ├── windows/main_window.py   # Main UI coordinator
│   └── panels/                  # View-layer panels (sample mapping, preview, etc.)
├── panels/                      # Core panels (piano keyboard, groups, modulation, etc.)
├── widgets/                     # Custom widgets (knobs, sliders, audio preview)
├── utils/                       # Utilities (theme, errors, accessibility, layout)
├── styles/main_theme.qss        # QSS stylesheet
└── commands/commands.py         # Undo/redo (stub)
```

See [docs/UI_STYLE_GUIDE.md](docs/UI_STYLE_GUIDE.md) for the design system reference.

## License

MIT License
