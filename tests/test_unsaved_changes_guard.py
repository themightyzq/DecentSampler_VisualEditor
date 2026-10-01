"""Closing, opening or creating a preset must not silently discard edits.

These tests build the real main window offscreen and answer the Save / Don't Save /
Cancel prompt through MainWindow._ask_unsaved, which they replace with a stub.
"""
import os
import sys
import wave
import xml.etree.ElementTree as ET

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from types import SimpleNamespace

from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from serialization.dspreset_reader import read_dspreset

def parse_tree(path):
    """Parse keeping comments, so comments count in the comparison."""
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.parse(path, parser=parser)


PRESET_XML = """<?xml version="1.0" encoding="UTF-8"?>
<DecentSampler minVersion="1.1.0" presetName="Guarded" author="Tester">
  <ui width="900" height="400" layoutMode="relative" bgMode="top_left" bgColor="FF112233" bgImage="bg.png" haveReverb="true" haveTone="true" haveChorus="true" haveMidicc1="true" noDecay="true">
    <tab name="main">
      <labeled-knob x="220" y="75" width="90" label="Drive" type="float" minValue="0" maxValue="1" value="0.1">
        <binding type="effect" level="group" groupIndex="0" effectIndex="0" parameter="FX_DRIVE"/>
      </labeled-knob>
    </tab>
    <keyboard>
      <color loNote="0" hiNote="127" color="FF444444" pressedColor="FF888888"/>
    </keyboard>
  </ui>
  <effects>
    <effect type="reverb" wetLevel="0.3"/>
  </effects>
  <groups attack="0.001" volume="-3dB" glideMode="legato">
    <group name="Close" tags="mic_close">
      <sample path="Samples/C3.wav" rootNote="60" loNote="48" hiNote="71" trigger="attack"/>
    </group>
  </groups>
  <midi>
    <cc number="1"><binding level="ui" type="control" parameter="VALUE" position="0"/></cc>
  </midi>
  <notes>kept</notes>
</DecentSampler>
"""


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def preset_file(tmp_path):
    folder = tmp_path / "lib"
    (folder / "Samples").mkdir(parents=True)
    with wave.open(str(folder / "Samples" / "C3.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"\x00\x00" * 32)
    path = folder / "guarded.dspreset"
    path.write_text(PRESET_XML, encoding="utf-8")
    return path


@pytest.fixture
def window(qapp):
    from views.windows.main_window import MainWindow
    w = MainWindow()
    yield w
    w._ask_unsaved = lambda action: "discard"  # never block teardown on a prompt
    w.close()


def canonical(node):
    if not isinstance(node.tag, str):
        return ("#comment", (node.text or "").strip())
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            [canonical(c) for c in node])


def load(window, path):
    """What the load worker does once the file has been read."""
    window.load_worker = SimpleNamespace(file_path=str(path), isRunning=lambda: False)
    window._on_preset_loaded(read_dspreset(str(path)))


def never_asked(action):
    raise AssertionError(f"prompted although nothing changed ({action})")


def test_fresh_window_is_clean_and_closes_without_a_prompt(window):
    assert not window.is_dirty()
    window._ask_unsaved = never_asked
    assert window.close() is True


def test_a_freshly_opened_preset_is_clean(window, preset_file):
    load(window, preset_file)
    assert not window.is_dirty()
    assert window.current_path == str(preset_file)
    window._ask_unsaved = never_asked
    assert window.close() is True


def test_open_then_save_keeps_everything_the_panels_do_not_show(window, preset_file):
    """The options panel has no checkboxes for these flags; saving must not reset them."""
    before = canonical(parse_tree(str(preset_file)).getroot())
    load(window, preset_file)
    assert window._save_current_sync() is True
    after = canonical(parse_tree(str(preset_file)).getroot())
    assert after == before


def test_editing_through_the_properties_panel_marks_dirty(window, preset_file):
    load(window, preset_file)
    window.global_options_panel.preset_name_edit.setText("Renamed")
    assert window.is_dirty()


def test_editing_the_envelope_marks_dirty(window, preset_file):
    load(window, preset_file)
    window.group_properties_panel_widget.attack_card.value_spin.setValue(0.75)
    assert window.is_dirty()


def test_adding_a_group_or_lfo_marks_dirty(window, preset_file):
    from models.data_classes import LFO
    load(window, preset_file)
    window.preset.lfos.append(LFO("New"))
    assert window.is_dirty()


def test_save_makes_the_preset_clean_again(window, preset_file):
    load(window, preset_file)
    window.preset.name = "Saved Name"
    assert window.is_dirty()
    assert window._save_current_sync() is True
    assert not window.is_dirty()
    assert ET.parse(str(preset_file)).getroot().get("presetName") == "Saved Name"


# --- close ----------------------------------------------------------------------------

def test_close_cancel_keeps_window_and_edits(window, preset_file):
    load(window, preset_file)
    window.preset.name = "Edited"
    original = preset_file.read_bytes()
    asked = []
    window._ask_unsaved = lambda action: asked.append(action) or "cancel"

    assert window.close() is False
    assert asked and window.preset.name == "Edited"
    assert preset_file.read_bytes() == original


def test_close_dont_save_closes_and_leaves_file(window, preset_file):
    load(window, preset_file)
    window.preset.name = "Edited"
    original = preset_file.read_bytes()
    window._ask_unsaved = lambda action: "discard"
    assert window.close() is True
    assert preset_file.read_bytes() == original


def test_close_save_writes_then_closes(window, preset_file):
    load(window, preset_file)
    window.preset.name = "Edited"
    window._ask_unsaved = lambda action: "save"
    assert window.close() is True
    assert ET.parse(str(preset_file)).getroot().get("presetName") == "Edited"


def test_close_is_cancelled_when_the_save_fails(window, preset_file, monkeypatch):
    load(window, preset_file)
    window.preset.name = "Edited"
    original = preset_file.read_bytes()
    shown = []
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a, **k: shown.append(a)))

    def broken(path):
        raise OSError("disk full")

    window.preset.to_dspreset = broken
    window._ask_unsaved = lambda action: "save"

    assert window.close() is False  # the user's edits are still in the open window
    assert shown, "the save error must be shown"
    assert preset_file.read_bytes() == original
    assert window.is_dirty()


def test_close_save_on_untitled_preset_asks_for_a_path(window, preset_file, tmp_path, monkeypatch):
    load(window, preset_file)
    window.current_path = None  # pretend it was never saved
    window.preset.name = "Edited"
    target = tmp_path / "chosen.dspreset"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))
    window._ask_unsaved = lambda action: "save"
    assert window.close() is True
    assert target.is_file()


def test_close_save_cancelled_in_the_file_dialog_keeps_window(window, preset_file, monkeypatch):
    load(window, preset_file)
    window.current_path = None
    window.preset.name = "Edited"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: ("", "")))
    window._ask_unsaved = lambda action: "save"
    assert window.close() is False


# --- new preset -----------------------------------------------------------------------

def test_new_preset_cancel_keeps_the_open_preset(window, preset_file):
    load(window, preset_file)
    window.preset.name = "Edited"
    current = window.preset
    window._ask_unsaved = lambda action: "cancel"
    window.new_preset()
    assert window.preset is current and window.preset.name == "Edited"


def test_new_preset_dont_save_replaces_it(window, preset_file):
    load(window, preset_file)
    window.preset.name = "Edited"
    window._ask_unsaved = lambda action: "discard"
    window.new_preset()
    assert window.preset.name == "Untitled"
    assert window.current_path is None
    assert not window.is_dirty()


def test_new_preset_save_writes_first(window, preset_file):
    load(window, preset_file)
    window.preset.name = "Edited"
    window._ask_unsaved = lambda action: "save"
    window.new_preset()
    assert ET.parse(str(preset_file)).getroot().get("presetName") == "Edited"
    assert window.preset.name == "Untitled"


def test_new_preset_on_clean_preset_does_not_prompt(window, preset_file):
    load(window, preset_file)
    window._ask_unsaved = never_asked
    window.new_preset()
    assert window.preset.name == "Untitled"


# --- open preset ----------------------------------------------------------------------

def test_open_cancel_does_not_start_loading(window, preset_file, tmp_path, monkeypatch):
    load(window, preset_file)
    window.preset.name = "Edited"
    other = tmp_path / "other.dspreset"
    other.write_text(PRESET_XML.replace("Guarded", "Other"), encoding="utf-8")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(other), "")))
    window._ask_unsaved = lambda action: "cancel"
    window.load_worker = None

    window.open_preset()

    assert window.load_worker is None
    assert window.preset.name == "Edited"


def test_open_dont_save_loads_the_other_preset(window, preset_file, tmp_path, monkeypatch, qapp):
    load(window, preset_file)
    window.preset.name = "Edited"
    other = tmp_path / "other.dspreset"
    other.write_text(PRESET_XML.replace('presetName="Guarded"', 'presetName="Other"'), encoding="utf-8")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(other), "")))
    window._ask_unsaved = lambda action: "discard"

    # the sample paths in "other" resolve against tmp_path, which has no Samples folder;
    # loading does not need them
    window.open_preset()
    window.load_worker.wait(10000)
    qapp.processEvents()

    assert window.preset.name == "Other"
    assert not window.is_dirty()
