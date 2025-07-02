# Decent Sampler Visual Editor

A cross-platform, local desktop application for visually editing Decent Sampler `.dspreset` files. Built with Python and PyQt5 for a native look and feel on Windows, macOS, and Linux.

## Features (Planned)

- Visual editor for all Decent Sampler XML features
- Drag-and-drop audio file assignment to MIDI notes
- Modern UI for building and editing `.dspreset` files
- Immediate refresh and live validation of changes
- 1:1 mapping to Decent Sampler's featureset and documentation
- Cross-platform: Windows, macOS, Linux

## Getting Started

### Prerequisites

- Python 3.7 or newer

### Installation

1. Clone this repository or download the source code.
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

### Running the App

```
python src/main.py
```

## Project Structure

- `src/main.py` — Main application entry point
- `requirements.txt` — Python dependencies

## Roadmap

- XML parsing and writing for `.dspreset` files
- Drag-and-drop audio file support
- MIDI note assignment UI
- Visual UI builder for Decent Sampler `<ui>` XML
- Immediate preview/refresh
- Modular codebase for future expansion

## License

MIT License

---

This project is in early development. Contributions and feedback are welcome!
