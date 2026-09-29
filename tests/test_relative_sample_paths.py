"""Relative <sample path> attributes must resolve against the preset's folder.

DecentSampler presets store sample paths relative to the .dspreset file. The
reader must resolve them so that a preset opened from disk can be re-saved
regardless of the process's current working directory.
"""
import os
import sys
import wave
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from serialization.dspreset_reader import read_dspreset
from serialization.dspreset_writer import write_dspreset

PRESET_XML = """<?xml version="1.0" encoding="UTF-8"?>
<DecentSampler minVersion="1.0.2" presetName="RelTest">
  <groups>
    <group>
      <sample path="samples/kick.wav" rootNote="60" loNote="60" hiNote="60"/>
    </group>
  </groups>
</DecentSampler>
"""


def _write_wav(path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"\x00\x00" * 64)


def _make_preset_dir(tmp_path):
    preset_dir = tmp_path / "presetA"
    (preset_dir / "samples").mkdir(parents=True)
    wav = preset_dir / "samples" / "kick.wav"
    _write_wav(wav)
    preset_file = preset_dir / "test.dspreset"
    preset_file.write_text(PRESET_XML, encoding="utf-8")
    return preset_file, wav


def test_relative_sample_path_resolved_and_resaveable(tmp_path, monkeypatch):
    preset_file, wav = _make_preset_dir(tmp_path)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    preset = read_dspreset(str(preset_file))

    zone = preset.sample_manager.get_zones()[0]
    assert os.path.isabs(zone.path)
    assert os.path.samefile(zone.path, wav)
    assert os.path.isfile(preset.mappings[0].path)
    assert os.path.samefile(preset.mappings[0].path, wav)

    out_dir = tmp_path / "saved"
    out_dir.mkdir()
    out_path = out_dir / "out.dspreset"
    write_dspreset(preset, str(out_path))  # raised "Sample file not found" before the fix

    sample_elem = ET.parse(str(out_path)).getroot().find(".//sample")
    rel = sample_elem.attrib["path"]
    assert not os.path.isabs(rel)
    assert os.path.isfile(out_dir / rel)


def test_absolute_sample_path_unchanged(tmp_path, monkeypatch):
    _, wav = _make_preset_dir(tmp_path)
    preset_file = tmp_path / "abs.dspreset"
    preset_file.write_text(
        PRESET_XML.replace("samples/kick.wav", str(wav)), encoding="utf-8")
    monkeypatch.chdir(tmp_path / "presetA")

    preset = read_dspreset(str(preset_file))
    assert preset.sample_manager.get_zones()[0].path == str(wav)
