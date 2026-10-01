"""Opening and re-saving a preset must not lose what the editor does not model.

The reader keeps the parsed XML; the writer patches a copy of it. These tests
build presets shaped like real libraries (UI controls with bindings, menus,
several tabs, groups with attributes and child elements, MIDI mappings, effects,
modulators, tags, notes, comments), round-trip them through read_dspreset and
write_dspreset, and compare the XML element by element: tag, attributes, text,
child order.
"""
import os
import shutil
import sys
import wave
import xml.etree.ElementTree as ET

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.data_classes import (
    LFO, ModulationRoute, ModulatorTarget, SampleZone,
)
from serialization.dspreset_reader import read_dspreset
from serialization.dspreset_writer import write_dspreset

def parse_tree(path):
    """Parse keeping comments, so comments count in the comparison."""
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    return ET.parse(path, parser=parser)


EXAMPLES = os.path.join(os.path.dirname(__file__), '..', 'Examples')

RICH = """<?xml version="1.0" encoding="UTF-8"?>
<DecentSampler minVersion="1.1.0" presetName="Rich Fixture" author="Tester" description="Everything the editor does not model">
  <!-- user interface -->
  <ui width="900" height="400" layoutMode="relative" bgMode="top_left" bgColor="FF112233" bgImage="bg.png" haveReverb="true" haveMidicc1="true" noDecay="true" coverArt="cover.png">
    <tab name="main">
      <!-- gain -->
      <label x="40" y="55" width="50" height="20" text="Gain" textColor="FFFFFFFF" textSize="14" hAlign="center"/>
      <control x="50" y="75" width="30" height="90" parameterName="Gain" style="linear_vertical" minValue="0" maxValue="1" value="0.8" textColor="FFFFFFFF" trackForegroundColor="FFCCCCCC">
        <binding type="amp" level="instrument" position="0" parameter="AMP_VOLUME"/>
      </control>
      <labeled-knob x="220" y="75" width="90" label="Drive" type="float" minValue="0" maxValue="1" value="0.1" textSize="14">
        <binding type="effect" level="group" groupIndex="0" effectIndex="0" parameter="FX_DRIVE" translation="table" translationTable="0,1;0.2,10;1,100"/>
        <binding type="effect" level="group" groupIndex="1" effectIndex="0" parameter="FX_DRIVE" translation="table" translationTable="0,2;1,400"/>
      </labeled-knob>
      <menu x="620" y="165" width="150" height="25" value="1" textColor="FFFFFFFF">
        <option name="Warm">
          <binding type="general" level="group" position="0" parameter="ENABLED" translation="fixed_value" translationValue="true"/>
          <binding type="general" level="group" position="1" parameter="ENABLED" translation="fixed_value" translationValue="false"/>
        </option>
        <option name="Driven">
          <binding type="general" level="group" position="0" parameter="ENABLED" translation="fixed_value" translationValue="false"/>
        </option>
      </menu>
      <image x="0" y="0" width="100" height="40" path="logo.png"/>
      <button x="10" y="300" width="80" height="24" style="image" mainImage="b.png" value="0">
        <binding type="general" level="group" position="0" parameter="ENABLED" translation="fixed_value" translationValue="true"/>
      </button>
    </tab>
    <tab name="second">
      <labeled-knob x="30" y="40" width="80" label="Second" type="float" minValue="0" maxValue="5" value="1">
        <binding type="effect" level="instrument" position="0" parameter="FX_MIX"/>
      </labeled-knob>
    </tab>
    <keyboard>
      <color loNote="0" hiNote="59" color="FF444444" pressedColor="FF888888"/>
      <color loNote="60" hiNote="127" color="FF224466" pressedColor="FF88AACC"/>
    </keyboard>
  </ui>
  <modulators>
    <lfo name="Wobble" frequency="2.5" waveform="triangle" amplitude="0.5" offset="0.0" phase="0.0" sync="free" syncLength="1" retrigger="true" scope="global" modAmount="1">
      <binding type="amp" level="instrument" position="0" parameter="AMP_VOLUME" amount="0.3" translation="linear" modBehavior="add"/>
    </lfo>
    <envelope name="ModEnv" attack="0.1" decay="0.5" sustain="0.7" release="0.9">
      <binding type="effect" level="instrument" position="0" parameter="FX_MIX" amount="0.5"/>
    </envelope>
  </modulators>
  <effects>
    <effect type="reverb" wetLevel="0.3" roomSize="0.5"/>
    <effect type="chorus" mix="0.25" modDepth="0.2" modRate="0.2"/>
    <effect type="reverb" wetLevel="0.9"/>
    <effect type="unknown_future_effect" foo="bar"/>
  </effects>
  <groups attack="0.001" decay="0.2" sustain="0.9" release="0.4" volume="-3dB" glideTime="0.1" glideMode="legato" seqMode="round_robin">
    <group name="Close" tags="mic_close" ampVelTrack="0.5" enabled="true" volume="2dB" silencedByTags="cut" silencingMode="fast">
      <effects>
        <effect type="gain" level="0.9"/>
      </effects>
      <sample path="Samples/Close/C3.wav" rootNote="60" loNote="48" hiNote="71" loVel="0" hiVel="63" trigger="attack" volume="3dB" tags="x"/>
      <sample path="Samples/Close/C4.wav" rootNote="72" loNote="72" hiNote="95" velocityRange="64,127" loopEnabled="true" loopStart="10" loopEnd="40" loopCrossfade="5" loopCrossfadeMode="equal_power"/>
    </group>
    <group name="Distant" tags="mic_distant" enabled="false">
      <sample path="Samples/Distant/C3.wav" rootNote="60" loNote="48" hiNote="71" seqMode="always" seqPosition="2" tune="0.5"/>
    </group>
  </groups>
  <midi>
    <cc number="1">
      <binding level="ui" type="control" parameter="VALUE" position="0" translation="linear" translationOutputMin="0" translationOutputMax="1"/>
    </cc>
    <note>
      <binding level="instrument" type="amp" parameter="AMP_VOLUME" translation="linear"/>
    </note>
  </midi>
  <tags>
    <tag name="mic_close" enabled="true"/>
  </tags>
  <notes>Free text kept as is</notes>
  <buses>
    <bus busVolume="1.0"/>
  </buses>
</DecentSampler>
"""

GROUPS_ONLY = """<?xml version="1.0" encoding="UTF-8"?>
<DecentSampler minVersion="1.0.0" presetName="Groups">
  <groups attack="0.001" decay="0.0" sustain="1.0" release="0.3" volume="0dB">
    <group>
      <sample path="Samples/a.wav" loNote="0" hiNote="63" rootNote="60"/>
    </group>
    <group tags="alt" seqMode="random">
      <sample path="Samples/b.wav" loNote="64" hiNote="127" rootNote="72"/>
    </group>
  </groups>
</DecentSampler>
"""

MODULATORS_AND_EFFECTS = """<?xml version="1.0" encoding="UTF-8"?>
<DecentSampler presetName="Mod">
  <modulators>
    <lfo name="A" frequency="1" waveform="sine" retrigger="false"/>
    <lfo name="B" frequency="0.25" waveform="square" scope="voice">
      <binding type="effect" level="instrument" position="0" parameter="FX_FILTER_FREQUENCY" amount="0.5" invert="true"/>
      <binding type="amp" level="group" groupIndex="1" parameter="AMP_VOLUME" amount="1.0"/>
    </lfo>
  </modulators>
  <effects>
    <effect type="lowpass" frequency="22000.0"/>
  </effects>
  <groups>
    <group>
      <sample path="Samples/a.wav" loNote="0" hiNote="127" rootNote="60"/>
    </group>
  </groups>
</DecentSampler>
"""

FIXTURES = {
    "rich": RICH,
    "groups_only": GROUPS_ONLY,
    "modulators_and_effects": MODULATORS_AND_EFFECTS,
}


def canonical(node):
    """Order-sensitive structural form: tag, attributes (order-free), text, children."""
    if not isinstance(node.tag, str):
        return ("#comment", (node.text or "").strip())
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        (node.text or "").strip(),
        [canonical(child) for child in node],
    )


def canonical_file(path):
    return canonical(parse_tree(str(path)).getroot())


def count(path):
    elements = list(ET.parse(str(path)).getroot().iter())
    return len(elements), sum(len(e.attrib) for e in elements)


def _wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"\x00\x00" * 32)


def _library(tmp_path, name, xml, with_samples=True):
    """Write a preset and the sample files it refers to."""
    folder = tmp_path / name
    folder.mkdir()
    preset_file = folder / "preset.dspreset"
    preset_file.write_text(xml, encoding="utf-8")
    if with_samples:
        for sample in ET.fromstring(xml.split("?>", 1)[1]).iter("sample"):
            _wav(folder / sample.get("path"))
    return preset_file


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_resave_in_place_preserves_everything(tmp_path, name):
    preset_file = _library(tmp_path, name, FIXTURES[name])
    before = canonical_file(preset_file)

    write_dspreset(read_dspreset(str(preset_file)), str(preset_file))

    assert canonical_file(preset_file) == before


@pytest.mark.parametrize("name", sorted(FIXTURES))
def test_save_to_another_folder_preserves_everything_and_copies_samples(tmp_path, name):
    preset_file = _library(tmp_path, name, FIXTURES[name])
    before = canonical_file(preset_file)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    out = elsewhere / "copy.dspreset"

    write_dspreset(read_dspreset(str(preset_file)), str(out))

    assert canonical_file(out) == before
    for sample in ET.parse(str(out)).getroot().iter("sample"):
        copied = elsewhere / sample.get("path")  # same relative layout as the original
        assert copied.is_file(), sample.get("path")


def test_resave_when_sample_files_are_missing_still_preserves_everything(tmp_path):
    """Presets are often opened before their samples are unpacked; saving in place must not fail."""
    preset_file = _library(tmp_path, "nosamples", RICH, with_samples=False)
    before = canonical_file(preset_file)
    write_dspreset(read_dspreset(str(preset_file)), str(preset_file))
    assert canonical_file(preset_file) == before


@pytest.mark.parametrize("example", ["BrokenPiano.dspreset", "boilerplate.dspreset"])
def test_repo_examples_round_trip(tmp_path, example):
    source = os.path.join(EXAMPLES, example)
    if not os.path.exists(source):
        pytest.skip("example not present")
    copy = tmp_path / example
    shutil.copy(source, copy)
    before_counts = count(copy)
    before = canonical_file(copy)

    write_dspreset(read_dspreset(str(copy)), str(copy))

    assert count(copy) == before_counts
    assert canonical_file(copy) == before


def test_unmodelled_blocks_are_kept_in_place_and_order(tmp_path):
    preset_file = _library(tmp_path, "order", RICH)
    write_dspreset(read_dspreset(str(preset_file)), str(preset_file))
    root = ET.parse(str(preset_file)).getroot()
    assert [c.tag for c in root] == ["ui", "modulators", "effects", "groups", "midi", "tags", "notes", "buses"]
    assert root.get("author") == "Tester"
    assert root.find("notes").text == "Free text kept as is"
    ui = root.find("ui")
    assert ui.get("coverArt") == "cover.png"
    assert [t.get("name") for t in ui.findall("tab")] == ["main", "second"]
    knob = ui.find("tab/labeled-knob")
    assert len(knob.findall("binding")) == 2
    assert knob.find("binding").get("translationTable") == "0,1;0.2,10;1,100"
    assert [o.get("name") for o in ui.find("tab/menu").findall("option")] == ["Warm", "Driven"]
    groups = root.find("groups")
    assert groups.get("glideMode") == "legato" and groups.get("volume") == "-3dB"
    assert groups.find("group").get("silencingMode") == "fast"
    assert groups.find("group/effects/effect").get("type") == "gain"
    assert root.find("midi/note") is not None
    assert root.find("modulators/envelope") is not None
    assert root.find("effects/effect[@type='unknown_future_effect']") is not None
    assert len(root.findall("effects/effect")) == 4  # duplicate reverb effects not collapsed


def test_unreadable_numbers_do_not_stop_the_preset_opening(tmp_path):
    """Real presets use values like volume="3dB" on samples; they must open and survive."""
    preset_file = _library(tmp_path, "db", RICH)
    preset = read_dspreset(str(preset_file))
    assert preset.sample_manager.get_zones()[0].volume == 0.0  # not readable as a number
    write_dspreset(preset, str(preset_file))
    first = ET.parse(str(preset_file)).getroot().find("groups/group/sample")
    assert first.get("volume") == "3dB"


# --- edits reach the file; everything else still survives -----------------------------

def _edit_and_save(tmp_path, edit, name="edit", xml=RICH):
    preset_file = _library(tmp_path, name, xml)
    preset = read_dspreset(str(preset_file))
    edit(preset)
    write_dspreset(preset, str(preset_file))
    return ET.parse(str(preset_file)).getroot()


def test_rename_changes_only_the_name(tmp_path):
    original = canonical(ET.fromstring(RICH.split("?>", 1)[1]))

    def edit(preset):
        preset.name = "Renamed"

    root = _edit_and_save(tmp_path, edit)
    assert root.get("presetName") == "Renamed"
    root.set("presetName", "Rich Fixture")
    assert [canonical(c) for c in root] == original[3]


def test_ui_settings_edit_patches_only_those_attributes(tmp_path):
    def edit(preset):
        preset.ui_width = 1000
        preset.bg_image = ""
        preset.have_reverb = False
        preset.bg_color = "#aabbcc"

    root = _edit_and_save(tmp_path, edit)
    ui = root.find("ui")
    assert ui.get("width") == "1000"
    assert "bgImage" not in ui.attrib
    assert ui.get("haveReverb") == "false"
    assert ui.get("bgColor") == "FFAABBCC"
    assert ui.get("haveMidicc1") == "true" and ui.get("coverArt") == "cover.png"
    assert ui.get("height") == "400"


def test_sample_edit_patches_that_sample_only(tmp_path):
    def edit(preset):
        zone = preset.sample_manager.get_zones()[1]
        zone.loNote = 70
        zone.tune = 1.5

    root = _edit_and_save(tmp_path, edit)
    samples = root.findall("groups/group/sample")
    assert samples[1].get("loNote") == "70" and samples[1].get("tune") == "1.5"
    assert samples[1].get("loopCrossfadeMode") == "equal_power"  # unmodelled attribute kept
    assert samples[0].get("trigger") == "attack" and samples[0].get("hiVel") == "63"
    assert samples[2].get("seqMode") == "always"


def test_deleting_a_sample_removes_only_its_element(tmp_path):
    def edit(preset):
        zones = preset.sample_manager.get_zones()
        preset.sample_manager.zones = [z for z in zones if z.path != zones[1].path]

    root = _edit_and_save(tmp_path, edit)
    paths = [s.get("path") for s in root.findall("groups/group/sample")]
    assert paths == ["Samples/Close/C3.wav", "Samples/Distant/C3.wav"]
    assert root.find("groups/group/effects") is not None


def test_new_sample_is_added_to_the_last_group_with_a_copied_file(tmp_path):
    preset_file = _library(tmp_path, "add", RICH)
    extra = tmp_path / "extra" / "snare.wav"
    _wav(extra)
    preset = read_dspreset(str(preset_file))
    preset.sample_manager.zones.append(SampleZone(str(extra), 62, 62, 62))
    write_dspreset(preset, str(preset_file))

    root = ET.parse(str(preset_file)).getroot()
    last_group = root.findall("groups/group")[-1]
    assert [s.get("path") for s in last_group.findall("sample")][-1] == "samples/snare.wav"
    assert (preset_file.parent / "samples" / "snare.wav").is_file()
    assert last_group.get("name") == "Distant"
    assert len(root.findall("groups/group/sample")) == 4


def test_envelope_edit_goes_to_the_first_group_only_when_changed(tmp_path):
    def edit(preset):
        preset.envelope.attack = 0.5

    root = _edit_and_save(tmp_path, edit)
    env = root.find("groups/group/envelope")
    assert env is not None and env.get("attack") == "0.5"
    assert root.find("groups").get("attack") == "0.001"


def test_ui_control_move_and_delete(tmp_path):
    def edit(preset):
        elements = preset.ui.elements
        knob = next(e for e in elements if e.label == "Drive")
        knob.x = 300
        elements.remove(next(e for e in elements if e.label == "Second"))

    root = _edit_and_save(tmp_path, edit)
    drive = root.find("ui/tab/labeled-knob")
    assert drive.get("x") == "300" and drive.get("y") == "75"
    assert len(drive.findall("binding")) == 2
    assert root.find("ui/tab[@name='second']") is not None  # the tab itself stays
    assert root.find("ui/tab[@name='second']/labeled-knob") is None


def test_lfo_edit_keeps_unmodelled_attributes_and_bindings(tmp_path):
    def edit(preset):
        preset.lfos[0].frequency = 4.0

    root = _edit_and_save(tmp_path, edit)
    lfo = root.find("modulators/lfo")
    assert lfo.get("frequency") == "4.0"
    assert lfo.get("scope") == "global" and lfo.get("modAmount") == "1"
    binding = lfo.find("binding")
    assert binding.get("modBehavior") == "add" and binding.get("translation") == "linear"
    assert root.find("modulators/envelope") is not None


def test_new_lfo_and_route_are_added_and_removed_lfo_is_dropped(tmp_path):
    def edit(preset):
        new = LFO("Fresh", frequency=3.0)
        preset.lfos.append(new)
        preset.modulation_routes.append(
            ModulationRoute("Fresh", ModulatorTarget("amp", "AMP_VOLUME"), amount=0.2))
        gone = next(l for l in preset.lfos if l.name == "A")
        preset.lfos.remove(gone)

    root = _edit_and_save(tmp_path, edit, name="mods", xml=MODULATORS_AND_EFFECTS)
    names = [l.get("name") for l in root.findall("modulators/lfo")]
    assert names == ["B", "Fresh"]
    fresh = root.findall("modulators/lfo")[1]
    assert fresh.get("frequency") == "3.0" and fresh.find("binding").get("amount") == "0.2"
    assert len(root.findall("modulators/lfo")[0].findall("binding")) == 2
    assert root.find("modulators/lfo[@name='B']").get("scope") == "voice"


def test_effect_parameter_edit_keeps_other_effects(tmp_path):
    def edit(preset):
        preset.effects["Chorus"]["mix"] = "0.5"

    root = _edit_and_save(tmp_path, edit)
    effects = root.findall("effects/effect")
    assert [e.get("type") for e in effects] == ["reverb", "chorus", "reverb", "unknown_future_effect"]
    assert effects[1].get("mix") == "0.5" and effects[1].get("modDepth") == "0.2"
    assert effects[3].get("foo") == "bar"


def test_keyboard_colour_edit_patches_the_keyboard(tmp_path):
    def edit(preset):
        keyboard = next(e for e in preset.ui.elements if e.tag == "keyboard")
        keyboard.color_ranges[0].color = "FF000000"

    root = _edit_and_save(tmp_path, edit)
    colors = root.findall("ui/keyboard/color")
    assert [c.get("color") for c in colors] == ["FF000000", "FF224466"]


def test_comments_survive_and_do_not_break_the_ui_reader(tmp_path):
    preset_file = _library(tmp_path, "comments", RICH)
    preset = read_dspreset(str(preset_file))
    assert all(isinstance(e.label, str) for e in preset.ui.elements)
    write_dspreset(preset, str(preset_file))
    text = preset_file.read_text(encoding="utf-8")
    assert "<!-- user interface -->" in text and "<!-- gain -->" in text


def test_source_tree_is_not_modified_by_saving(tmp_path):
    preset_file = _library(tmp_path, "pristine", RICH)
    preset = read_dspreset(str(preset_file))
    snapshot = canonical(preset.source_root)
    preset.name = "Changed"
    preset.lfos[0].frequency = 9.0
    write_dspreset(preset, str(preset_file))
    assert canonical(preset.source_root) == snapshot
    # saving again from the same object gives the same file
    first = preset_file.read_bytes()
    write_dspreset(preset, str(preset_file))
    assert preset_file.read_bytes() == first


def test_group_manager_layout_keeps_group_attributes_and_sample_elements(tmp_path):
    """Once the user builds groups in the Groups tab, groups are laid out from the model."""
    from panels.group_manager_panel import SampleGroup

    preset_file = _library(tmp_path, "custom", RICH)
    preset = read_dspreset(str(preset_file))
    zones = preset.sample_manager.get_zones()
    group = SampleGroup(name="All")
    for zone in zones:
        group.add_sample(zone)
    preset.sample_groups = [group]
    write_dspreset(preset, str(preset_file))

    root = ET.parse(str(preset_file)).getroot()
    assert root.find("groups").get("glideMode") == "legato"  # <groups> attributes kept
    samples = root.findall("groups/group/sample")
    assert len(samples) == 3
    assert samples[0].get("trigger") == "attack" and samples[0].get("hiVel") == "63"
    assert root.find("ui/tab/labeled-knob/binding") is not None


def test_generated_preset_still_writes_without_a_source(tmp_path):
    """A preset created in the editor (no source file) is generated from the model."""
    from models.instrument_preset import InstrumentPreset

    wav = tmp_path / "s.wav"
    _wav(wav)
    preset = InstrumentPreset("Fresh")
    preset.sample_manager.zones = [SampleZone(str(wav), 60, 48, 72)]
    out = tmp_path / "fresh.dspreset"
    write_dspreset(preset, str(out))
    root = ET.parse(str(out)).getroot()
    assert root.get("presetName") == "Fresh"
    assert root.find("groups/group/sample").get("path") == "samples/s.wav"
    assert root.find("ui").get("bgColor") == "FF222222"


def test_repeat_save_to_another_folder_does_not_copy_the_library_again(tmp_path, monkeypatch):
    import serialization.dspreset_writer as writer_module

    preset_file = _library(tmp_path, "lib", RICH)
    preset = read_dspreset(str(preset_file))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    out = elsewhere / "copy.dspreset"

    copies = []
    real_copy2 = writer_module.shutil.copy2
    monkeypatch.setattr(writer_module.shutil, "copy2",
                        lambda a, b, *args, **kw: copies.append(b) or real_copy2(a, b, *args, **kw))

    write_dspreset(preset, str(out))
    assert len(copies) == 3
    write_dspreset(preset, str(out))
    assert len(copies) == 3
