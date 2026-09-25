# DecentSampler Visual Editor

A desktop application for visually editing DecentSampler .dspreset preset files. It is for sound designers and sample library builders who use Decent Sampler, a free third-party sampler plugin, and it covers sample-to-key and velocity mapping, groups, effects, and modulation routing. Built with Python and PyQt5, and packaged as standalone apps for Windows, macOS, and Linux.

## Install

Pre-built standalone apps for Windows, macOS, and Linux are attached to the
[v0.1.0 release](https://github.com/themightyzq/DecentSampler_VisualEditor/releases/tag/v0.1.0)
on GitHub. These builds are unsigned, so you may need to bypass OS gatekeeper
warnings on first launch.

To run from source instead, see Build below.

## Use

- File > New starts a blank preset; File > Open... loads an existing .dspreset file.
- The sample mapping panel maps samples to key and velocity ranges on the keyboard.
- The group manager organizes samples into groups, including velocity layers,
  round robin, and blend groups.
- The effects panel adds and configures effects such as reverb, delay, and
  chorus from the built-in effects catalog.
- The modulation panel routes LFOs to parameters.
- File > Save writes the result back to a .dspreset file for use in Decent Sampler.

See the [official Decent Sampler developer guide](https://decentsampler-developers-guide.readthedocs.io/)
for the .dspreset file format itself.

## Build

### Run from source

Requires Python 3.7 or newer.

```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt  # optional: pygame, numpy, librosa, pydub, soundfile
cd src && python main.py
```

### Build a standalone executable

Standalone executables are built with PyInstaller, using the same command CI runs:

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name DecentSamplerEditor --paths src src/main.py
```

Output lands in `dist/DecentSamplerEditor/` (or `dist/DecentSamplerEditor.app` on macOS).

### Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

CI runs this across Windows, macOS, and Linux on Python 3.9, 3.11, and 3.12,
then builds standalone apps with PyInstaller on push to main and on pull requests.

## License

GNU General Public License v3.0 or later (GPL-3.0-or-later). See [LICENSE](LICENSE)
for the full text.

Copyright ZQ SFX. https://www.zq-sfx.com  connect@zq-sfx.com
