"""Round-trip tests for dspreset XML serialization.

These tests construct InstrumentPreset objects, write them to XML,
read them back, and verify all properties survive the round-trip.
"""
import os
import sys
import tempfile
import shutil
import xml.etree.ElementTree as ET

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.data_classes import (
    SampleZone, SampleManager, SampleMapping, GroupEnvelope,
    LFO, ModulatorTarget, ModulationRoute, UIElement,
)
from models.instrument_preset import InstrumentPreset
from serialization.dspreset_reader import read_dspreset
from serialization.dspreset_writer import write_dspreset


@pytest.fixture
def tmp_preset_dir(tmp_path):
    """Create a temp directory with a dummy sample file."""
    sample_dir = tmp_path / "samples"
    sample_dir.mkdir()
    # Create a minimal WAV file (44-byte header, no data)
    sample_file = tmp_path / "test.wav"
    sample_file.write_bytes(
        b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00'
        b'\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00'
        b'\x02\x00\x10\x00data\x00\x00\x00\x00'
    )
    return tmp_path, str(sample_file)


def _write_and_read(preset, tmp_path):
    """Write a preset to XML and read it back."""
    out_path = str(tmp_path / "output.dspreset")
    write_dspreset(preset, out_path)
    return read_dspreset(out_path), out_path


class TestBasicRoundTrip:
    def test_preset_name(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("My Instrument")
        zone = SampleZone(sample, 60, 48, 72)
        preset.sample_manager.zones = [zone]

        loaded, _ = _write_and_read(preset, tmp_path)
        assert loaded.name == "My Instrument"

    def test_ui_dimensions(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test", ui_width=900, ui_height=400)
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        loaded, _ = _write_and_read(preset, tmp_path)
        assert loaded.ui_width == 900
        assert loaded.ui_height == 400

    def test_layout_and_bg_mode(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test", layout_mode="relative", bg_mode="centered")
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        loaded, _ = _write_and_read(preset, tmp_path)
        assert loaded.layout_mode == "relative"
        assert loaded.bg_mode == "centered"

    def test_boolean_flags(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset(
            "Test", have_reverb=True, have_tone=True,
            have_chorus=True, have_midicc1=True,
            no_attack=True, no_decay=True,
        )
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        loaded, _ = _write_and_read(preset, tmp_path)
        assert loaded.have_reverb is True
        assert loaded.have_tone is True
        assert loaded.have_chorus is True
        assert loaded.have_midicc1 is True
        assert loaded.no_attack is True
        assert loaded.no_decay is True


class TestSampleZoneRoundTrip:
    def test_basic_note_range(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test")
        zone = SampleZone(sample, rootNote=64, loNote=50, hiNote=78)
        preset.sample_manager.zones = [zone]

        loaded, _ = _write_and_read(preset, tmp_path)
        zones = loaded.sample_manager.get_zones()
        assert len(zones) == 1
        assert zones[0].rootNote == 64
        assert zones[0].loNote == 50
        assert zones[0].hiNote == 78

    def test_velocity_range(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test")
        zone = SampleZone(sample, 60, 48, 72, velocityRange=(32, 96))
        preset.sample_manager.zones = [zone]

        loaded, _ = _write_and_read(preset, tmp_path)
        zones = loaded.sample_manager.get_zones()
        assert zones[0].velocityRange == (32, 96)

    def test_volume_pan_tune(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test")
        zone = SampleZone(sample, 60, 48, 72, volume=-3.0, pan=0.5, tune=1.5)
        preset.sample_manager.zones = [zone]

        loaded, _ = _write_and_read(preset, tmp_path)
        z = loaded.sample_manager.get_zones()[0]
        assert z.volume == -3.0
        assert z.pan == 0.5
        assert z.tune == 1.5

    def test_loop_properties(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test")
        zone = SampleZone(
            sample, 60, 48, 72,
            loopEnabled=True, loopStart=1000, loopEnd=5000,
            loopCrossfade=0.1, loopMode="alternate",
        )
        preset.sample_manager.zones = [zone]

        loaded, _ = _write_and_read(preset, tmp_path)
        z = loaded.sample_manager.get_zones()[0]
        assert z.loopEnabled is True
        assert z.loopStart == 1000
        assert z.loopEnd == 5000
        assert z.loopCrossfade == pytest.approx(0.1)
        assert z.loopMode == "alternate"

    def test_start_end(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test")
        zone = SampleZone(sample, 60, 48, 72, start=500, end=10000)
        preset.sample_manager.zones = [zone]

        loaded, _ = _write_and_read(preset, tmp_path)
        z = loaded.sample_manager.get_zones()[0]
        assert z.start == 500
        assert z.end == 10000

    def test_seq_mode_position(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test")
        zone = SampleZone(sample, 60, 48, 72, seqMode="always", seqPosition=3)
        preset.sample_manager.zones = [zone]

        loaded, _ = _write_and_read(preset, tmp_path)
        z = loaded.sample_manager.get_zones()[0]
        assert z.seqMode == "always"
        assert z.seqPosition == 3


class TestEnvelopeRoundTrip:
    def test_custom_envelope(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        env = GroupEnvelope(attack=0.05, decay=0.5, sustain=0.7, release=1.2)
        preset = InstrumentPreset("Test", envelope=env)
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        loaded, _ = _write_and_read(preset, tmp_path)
        assert loaded.envelope.attack == pytest.approx(0.05)
        assert loaded.envelope.decay == pytest.approx(0.5)
        assert loaded.envelope.sustain == pytest.approx(0.7)
        assert loaded.envelope.release == pytest.approx(1.2)

    def test_default_envelope_not_written(self, tmp_preset_dir):
        """Default envelope values should not produce an envelope element."""
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test")
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        _, out_path = _write_and_read(preset, tmp_path)
        tree = ET.parse(out_path)
        # Default envelope should not appear in XML
        assert tree.find(".//envelope") is None


class TestLFORoundTrip:
    def test_lfo_properties(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        lfo = LFO("Vibrato", frequency=5.0, waveform="triangle",
                   amplitude=0.5, offset=0.1, phase=0.25,
                   sync="tempo", sync_length="1/4", retrigger=True)
        preset = InstrumentPreset("Test", lfos=[lfo])
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        loaded, _ = _write_and_read(preset, tmp_path)
        assert len(loaded.lfos) == 1
        l = loaded.lfos[0]
        assert l.name == "Vibrato"
        assert l.frequency == 5.0
        assert l.waveform == "triangle"
        assert l.amplitude == 0.5
        assert l.offset == pytest.approx(0.1)
        assert l.phase == 0.25
        assert l.sync == "tempo"
        assert l.sync_length == "1/4"
        assert l.retrigger is True

    def test_modulation_route(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        lfo = LFO("Tremolo", frequency=3.0)
        target = ModulatorTarget("amp", "AMP_VOLUME", level="group", position=0, group_index=1)
        route = ModulationRoute("Tremolo", target, amount=0.8, invert=True)
        preset = InstrumentPreset("Test", lfos=[lfo], modulation_routes=[route])
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        loaded, _ = _write_and_read(preset, tmp_path)
        assert len(loaded.modulation_routes) == 1
        r = loaded.modulation_routes[0]
        assert r.modulator_name == "Tremolo"
        assert r.target.target_type == "amp"
        assert r.target.parameter == "AMP_VOLUME"
        assert r.target.level == "group"
        assert r.target.group_index == 1
        assert r.amount == pytest.approx(0.8)
        assert r.invert is True


class TestUIElementRoundTrip:
    def test_knob_element(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        el = UIElement(10, 20, 64, 64, "Volume", widget_type="Knob",
                       tag="labeled-knob", target="AMP_VOLUME",
                       min_val=0.0, max_val=1.0)
        preset = InstrumentPreset("Test", ui_elements=[el])
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        loaded, _ = _write_and_read(preset, tmp_path)
        knobs = [e for e in loaded.ui.elements if e.widget_type == "Knob"]
        assert len(knobs) >= 1
        assert knobs[0].label == "Volume"

    def test_label_element_preserved(self, tmp_preset_dir):
        """Labels should survive round-trip (previously silently dropped)."""
        tmp_path, sample = tmp_preset_dir
        el = UIElement(10, 20, 200, 30, "My Label", widget_type="Label", tag="label")
        preset = InstrumentPreset("Test", ui_elements=[el])
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        _, out_path = _write_and_read(preset, tmp_path)
        tree = ET.parse(out_path)
        labels = tree.findall(".//label")
        assert len(labels) >= 1
        assert labels[0].attrib.get("label") == "My Label"


class TestEffectsRoundTrip:
    def test_effects_from_preset_dict(self, tmp_preset_dir):
        """Effects stored in preset.effects dict should be written to XML."""
        tmp_path, sample = tmp_preset_dir
        preset = InstrumentPreset("Test", effects={
            "Reverb": {"wetLevel": "0.6", "roomSize": "0.8"},
        })
        preset.sample_manager.zones = [SampleZone(sample, 60, 48, 72)]

        _, out_path = _write_and_read(preset, tmp_path)
        tree = ET.parse(out_path)
        effects = tree.findall(".//effect")
        reverb = [e for e in effects if e.attrib.get("type") == "reverb"]
        assert len(reverb) == 1
        assert reverb[0].attrib["wetLevel"] == "0.6"
        assert reverb[0].attrib["roomSize"] == "0.8"


class TestMultipleZones:
    def test_multiple_samples(self, tmp_preset_dir):
        tmp_path, sample = tmp_preset_dir
        # Create a second sample file
        sample2 = str(tmp_path / "test2.wav")
        shutil.copy(sample, sample2)

        preset = InstrumentPreset("Test")
        preset.sample_manager.zones = [
            SampleZone(sample, 60, 48, 60),
            SampleZone(sample2, 72, 61, 72),
        ]

        loaded, _ = _write_and_read(preset, tmp_path)
        zones = loaded.sample_manager.get_zones()
        assert len(zones) == 2
        assert zones[0].rootNote == 60
        assert zones[1].rootNote == 72
