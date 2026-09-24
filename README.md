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

### Downloads

Pre-built standalone apps for Windows, macOS, and Linux are available on the [Releases](../../releases) page. No Python installation required.

### Building from Source (Standalone Executable)

```bash
pip install pyinstaller
pyinstaller DecentSamplerEditor.spec
```

Output lands in `dist/DecentSamplerEditor/` (or `dist/DecentSamplerEditor.app` on macOS).

### CI / Releases

CI runs automatically on push to `main` and on pull requests:

1. **Test**: runs `pytest` across Windows, macOS, Linux with Python 3.9/3.11/3.12
2. **Build**: if tests pass, produces standalone apps via PyInstaller (Python 3.11)
3. **Release**: when a version tag (`v*`) is pushed, build artifacts are automatically attached to the corresponding GitHub release

To cut a new release:

```bash
git tag v0.2.0
git push origin v0.2.0
```

Then create a release on GitHub for that tag (or use `gh release create v0.2.0`). CI will attach the platform builds automatically.

## Architecture

```
src/
|-- main.py                      # Entry point
|-- model.py                     # Backward-compat shim (re-exports from models/)
|-- models/                      # Data model classes
|   |-- data_classes.py          # SampleZone, SampleMapping, LFO, UIElement, etc.
|   `-- instrument_preset.py     # InstrumentPreset (core preset object)
|-- serialization/               # XML I/O
|   |-- dspreset_reader.py       # .dspreset XML -> InstrumentPreset
|   `-- dspreset_writer.py       # InstrumentPreset -> .dspreset XML
|-- views/
|   |-- windows/main_window.py   # Main UI coordinator
|   `-- panels/                  # View-layer panels (sample mapping, preview, etc.)
|-- panels/                      # Core panels (piano keyboard, groups, modulation, etc.)
|-- widgets/                     # Custom widgets (knobs, sliders, audio preview)
|-- utils/                       # Utilities (theme, errors, accessibility, layout)
|-- styles/main_theme.qss        # QSS stylesheet
`-- commands/commands.py         # Undo/redo (stub)
```

See [docs/UI_STYLE_GUIDE.md](docs/UI_STYLE_GUIDE.md) for the design system reference.

## License

MIT License
