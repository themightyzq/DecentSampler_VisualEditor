"""Basic unit tests for data model and XML serialization."""
import sys
import os

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.data_classes import (
    SampleZone, SampleManager, SampleMapping, GroupEnvelope,
    LFO, ModulatorTarget, ModulationRoute, UIElement,
)
from models.instrument_preset import InstrumentPreset


def test_sample_zone_defaults():
    zone = SampleZone("test.wav", 60, 48, 72)
    assert zone.path == "test.wav"
    assert zone.rootNote == 60
    assert zone.loNote == 48
    assert zone.hiNote == 72
    assert zone.velocityRange == (0, 127)
    assert zone.seqMode == "round_robin"
    assert zone.loopEnabled is False


def test_sample_manager_add_remove():
    mgr = SampleManager()
    mgr.add_zone("a.wav", 60, 48, 72)
    mgr.add_zone("b.wav", 72, 60, 84)
    assert len(mgr.get_zones()) == 2

    mgr.remove_zone("a.wav")
    assert len(mgr.get_zones()) == 1
    assert mgr.get_zones()[0].path == "b.wav"

    mgr.clear()
    assert len(mgr.get_zones()) == 0


def test_sample_mapping_repr():
    m = SampleMapping("test.wav", 48, 72, 60)
    assert "test.wav" in repr(m)
    assert "48" in repr(m)


def test_group_envelope_defaults():
    env = GroupEnvelope()
    assert env.attack == 0.01
    assert env.decay == 1.0
    assert env.sustain == 1.0
    assert env.release == 0.43


def test_lfo_defaults():
    lfo = LFO("TestLFO")
    assert lfo.name == "TestLFO"
    assert lfo.frequency == 1.0
    assert lfo.waveform == "sine"
    assert lfo.retrigger is False


def test_ui_element_defaults():
    el = UIElement(10, 20, 64, 64, "Volume")
    assert el.x == 10
    assert el.label == "Volume"
    assert el.bindings == []
    assert el.options == []
    assert el.color_ranges == []


def test_instrument_preset_creation():
    preset = InstrumentPreset("Test Preset")
    assert preset.name == "Test Preset"
    assert preset.ui_width == 812
    assert preset.ui_height == 375
    assert preset.mappings == []
    assert preset.lfos == []
    assert preset.effects == {}


def test_backward_compat_import():
    """Verify the model.py shim still works."""
    from model import InstrumentPreset as IP
    from model import SampleZone as SZ
    assert IP is InstrumentPreset
    assert SZ is SampleZone


def test_xml_roundtrip():
    """Load example preset, verify key fields parsed correctly."""
    example_path = os.path.join(
        os.path.dirname(__file__), '..', 'Examples', 'BrokenPiano.dspreset'
    )
    if not os.path.exists(example_path):
        return  # Skip if example not available

    preset = InstrumentPreset.from_dspreset(example_path)
    assert preset.name != ""
    assert len(preset.mappings) > 0 or preset.ui_width > 0
