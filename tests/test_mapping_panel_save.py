"""Edits made in the sample mapping panel must reach the saved file.

The panel edits key range and root on mapping objects and imports new samples as
mappings; the writer saves sample zones. Saving reconciles the two, for presets
opened from a file (each sample's original element and unknown attributes survive)
and for presets built in the editor.
"""
import copy
import os
import sys
import wave
import xml.etree.ElementTree as ET

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from test_reader_fidelity import RICH, canonical, parse_tree
from test_unsaved_changes_guard import load, qapp, window  # noqa: F401  (fixtures)


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A validation or save error must fail the test, not block it on a dialog."""
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected dialog: {args[1:3]}")
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(refuse))
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(refuse))


def _wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"\x00\x00" * 32)


@pytest.fixture
def rich_file(tmp_path):
    folder = tmp_path / "lib"
    folder.mkdir()
    path = folder / "rich.dspreset"
    path.write_text(RICH, encoding="utf-8")
    for sample in ET.fromstring(RICH.split("?>", 1)[1]).iter("sample"):
        _wav(folder / sample.get("path"))
    return path


def _row_of(panel, filename):
    for row, mapping in enumerate(panel.samples):
        if os.path.basename(mapping.path) == filename:
            return row
    raise AssertionError(filename)


def test_mapping_panel_edit_import_and_remove_reach_the_file(window, rich_file, tmp_path):
    new_wav = tmp_path / "extra" / "snare.wav"
    _wav(new_wav)
    load(window, rich_file)
    panel = window.sample_mapping_panel
    assert len(panel.samples) == 3

    # 1. edit a mapping through the panel's own controls: key range and root
    panel.table_widget.selectRow(_row_of(panel, "C4.wav"))
    panel.lo_spin.setValue(50)
    panel.hi_spin.setValue(80)
    panel.root_spin.setValue(66)

    # 2. a velocity edit on a zone (the panel has no velocity control)
    first_zone = window.preset.sample_manager.get_zones()[0]
    first_zone.velocityRange = (20, 100)

    # 3. import a new sample through the panel, with a detected velocity range
    panel._on_import_completed([{
        "path": str(new_wav), "lo": 62, "hi": 62, "root": 62,
        "auto_detected": True, "velocity_range": (10, 90), "velocity_detected": True}])

    # 4. remove one mapping (what undo of an import or a refresh does)
    panel.set_samples([m for m in panel.samples if os.path.basename(m.path) != "C3.wav"
                       or "Distant" not in m.path])
    assert len(panel.samples) == 3  # Close/C3, Close/C4, snare

    assert window.is_dirty()
    assert window._save_current_sync() is True

    # expected: the original document with exactly those four changes applied
    original = ET.ElementTree(ET.fromstring(RICH.split("?>", 1)[1], ET.XMLParser(
        target=ET.TreeBuilder(insert_comments=True)))).getroot()
    groups = original.find("groups")
    close, distant = groups.findall("group")
    c3, c4 = close.findall("sample")
    c3.set("velocityRange", "20,100")
    c4.set("loNote", "50")
    c4.set("hiNote", "80")
    c4.set("rootNote", "66")
    distant.remove(distant.find("sample"))
    ET.SubElement(distant, "sample", {
        "path": "samples/snare.wav", "rootNote": "62", "loNote": "62", "hiNote": "62",
        "velocityRange": "10,90"})
    saved = parse_tree(str(rich_file)).getroot()
    assert canonical(saved) == canonical(original)

    # the copied sample is there and the file re-opens to the same mappings
    assert (rich_file.parent / "samples" / "snare.wav").is_file()
    from serialization.dspreset_reader import read_dspreset
    reopened = read_dspreset(str(rich_file))
    got = sorted((os.path.basename(m.path), m.lo, m.hi, m.root) for m in reopened.mappings)
    assert got == [("C3.wav", 48, 71, 60), ("C4.wav", 50, 80, 66), ("snare.wav", 62, 62, 62)]
    zones = {os.path.basename(z.path): z for z in reopened.sample_manager.get_zones()}
    assert zones["snare.wav"].velocityRange == (10, 90)
    assert zones["C3.wav"].velocityRange == (20, 100)
    assert not window.is_dirty()


def test_unrelated_untouched_parts_stay_equal_when_only_one_mapping_changes(window, rich_file):
    load(window, rich_file)
    panel = window.sample_mapping_panel
    panel.table_widget.selectRow(_row_of(panel, "C3.wav"))
    panel.root_spin.setValue(61)
    assert window._save_current_sync() is True

    original = ET.fromstring(RICH.split("?>", 1)[1], ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    original.find("groups/group/sample").set("rootNote", "61")
    assert canonical(parse_tree(str(rich_file)).getroot()) == canonical(original)


def test_editor_built_preset_saves_panel_mappings_and_edits(window, tmp_path, monkeypatch):
    a, b = tmp_path / "a" / "low.wav", tmp_path / "a" / "high.wav"
    _wav(a)
    _wav(b)
    target = tmp_path / "built" / "built.dspreset"
    target.parent.mkdir()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    panel = window.sample_mapping_panel
    panel.set_samples([
        {"path": str(a), "lo": 36, "hi": 59, "root": 48, "velocity_range": (0, 63)},
        {"path": str(b), "lo": 60, "hi": 83, "root": 72},
    ])
    assert window._save_current_sync() is True
    root = ET.parse(str(target)).getroot()
    samples = root.findall("groups/group/sample")
    assert [(s.get("path"), s.get("loNote"), s.get("hiNote"), s.get("rootNote")) for s in samples] == [
        ("samples/low.wav", "36", "59", "48"), ("samples/high.wav", "60", "83", "72")]
    assert samples[0].get("velocityRange") == "0,63" and samples[1].get("velocityRange") is None

    # edit one mapping and save again to the same file
    panel.table_widget.selectRow(1)
    panel.lo_spin.setValue(55)
    assert window.is_dirty()
    assert window._save_current_sync() is True
    samples = ET.parse(str(target)).getroot().findall("groups/group/sample")
    assert samples[1].get("loNote") == "55"
    assert len(samples) == 2


def test_sync_pairs_zones_by_path_and_range_when_a_duplicate_is_removed():
    from models.data_classes import SampleMapping, SampleZone
    from models.instrument_preset import InstrumentPreset

    preset = InstrumentPreset("P")
    first = SampleZone("/s/a.wav", 60, 0, 59)
    second = SampleZone("/s/a.wav", 72, 60, 127)
    second.tune = 1.5
    preset.sample_manager.zones = [first, second]
    # the user removed the first mapping of the same file
    preset.sync_zones_from_mappings([SampleMapping("/s/a.wav", 60, 127, 72)])
    assert preset.sample_manager.zones == [second]
    assert second.tune == 1.5 and second.loNote == 60


def test_opening_a_preset_with_an_lfo_does_not_change_the_lfo(window, rich_file):
    """Selecting the first LFO used to overwrite it with the editor widgets' defaults."""
    load(window, rich_file)
    lfo = window.preset.lfos[0]
    assert (lfo.frequency, lfo.waveform, lfo.amplitude, lfo.retrigger) == (2.5, "triangle", 0.5, True)
    assert window._save_current_sync() is True
    saved = ET.parse(str(rich_file)).getroot().find("modulators/lfo")
    assert saved.get("frequency") == "2.5" and saved.get("waveform") == "triangle"
    assert saved.get("retrigger") == "true" and saved.get("syncLength") == "1"
