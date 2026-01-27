import os
from typing import List, Optional
from models.data_classes import (
    SampleZone, SampleManager, SampleMapping, GroupEnvelope,
    LFO, ModulationRoute, UIElement,
)


class InstrumentPreset:
    def __init__(
        self,
        name: str,
        ui_width: int = 812,
        ui_height: int = 375,
        bg_image: Optional[str] = None,
        layout_mode: str = "relative",
        bg_mode: str = "top_left",
        mappings: Optional[List[SampleMapping]] = None,
        start_note: int = 21,
        have_attack: bool = True,
        have_decay: bool = True,
        have_sustain: bool = True,
        have_release: bool = True,
        have_tone: bool = False,
        have_chorus: bool = False,
        have_reverb: bool = False,
        have_midicc1: bool = False,
        no_attack: bool = False,
        no_decay: bool = False,
        cut_all_by_all: bool = False,
        silencing_mode: str = "normal",
        ui_elements: Optional[list] = None,
        envelope: Optional[GroupEnvelope] = None,
        effects: Optional[dict] = None,
        advanced_mode: bool = False,
        sample_manager: Optional[SampleManager] = None,
        lfos: Optional[List[LFO]] = None,
        modulation_routes: Optional[List[ModulationRoute]] = None,
        sample_groups: Optional[List] = None,
    ):
        self.name = name
        self.ui_width = ui_width
        self.ui_height = ui_height
        self.bg_image = bg_image
        self.layout_mode = layout_mode
        self.bg_mode = bg_mode
        self.mappings = mappings if mappings is not None else []
        self.sample_manager = sample_manager if sample_manager is not None else SampleManager()
        self.start_note = start_note
        self.have_attack = have_attack
        self.have_decay = have_decay
        self.have_sustain = have_sustain
        self.have_release = have_release
        self.have_tone = have_tone
        self.have_chorus = have_chorus
        self.have_reverb = have_reverb
        self.have_midicc1 = have_midicc1
        self.no_attack = no_attack
        self.no_decay = no_decay
        self.cut_all_by_all = cut_all_by_all
        self.silencing_mode = silencing_mode
        self.ui = type("UI", (), {})()
        self.ui.elements = ui_elements if ui_elements is not None else []
        self.envelope = envelope if envelope is not None else GroupEnvelope()
        self.effects = effects if effects is not None else {}
        self.advanced_mode = advanced_mode
        self.lfos = lfos if lfos is not None else []
        self.modulation_routes = modulation_routes if modulation_routes is not None else []
        self.sample_groups = sample_groups if sample_groups is not None else []

    @staticmethod
    def from_dspreset(path: str) -> "InstrumentPreset":
        from serialization.dspreset_reader import read_dspreset
        return read_dspreset(path)

    def to_dspreset(self, path: str):
        from serialization.dspreset_writer import write_dspreset
        write_dspreset(self, path)

    def auto_map(self, folder_path: str):
        wavs = sorted(
            [f for f in os.listdir(folder_path) if f.lower().endswith(".wav")]
        )
        mappings = []
        note = self.start_note
        for wav in wavs:
            mappings.append(SampleMapping(
                path=os.path.join(folder_path, wav),
                lo=note,
                hi=note,
                root=note,
            ))
            note += 1
        self.mappings = mappings
