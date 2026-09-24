"""Backward-compatibility shim. All classes now live in models/ and serialization/."""
from models.data_classes import (
    SampleZone,
    SampleManager,
    SampleMapping,
    GroupEnvelope,
    LFO,
    ModulatorTarget,
    ModulationRoute,
    UIElement,
)
from models.instrument_preset import InstrumentPreset

__all__ = [
    "SampleZone",
    "SampleManager",
    "SampleMapping",
    "GroupEnvelope",
    "LFO",
    "ModulatorTarget",
    "ModulationRoute",
    "UIElement",
    "InstrumentPreset",
]
