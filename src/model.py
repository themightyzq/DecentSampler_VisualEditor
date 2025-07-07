import xml.etree.ElementTree as ET
from typing import List, Optional

class SampleMapping:
    def __init__(self, path: str, lo: int, hi: int, root: int):
        self.path = path
        self.lo = lo
        self.hi = hi
        self.root = root

    def __repr__(self):
        return f"SampleMapping(path={self.path!r}, lo={self.lo}, hi={self.hi}, root={self.root})"

class UIElement:
    def __init__(self, x, y, width, height, label, skin=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.skin = skin  # path to skin image or None

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
        ui_elements: Optional[list] = None
    ):
        self.name = name
        self.ui_width = ui_width
        self.ui_height = ui_height
        self.bg_image = bg_image
        self.layout_mode = layout_mode
        self.bg_mode = bg_mode
        self.mappings = mappings if mappings is not None else []
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

    @staticmethod
    def from_dspreset(path: str) -> "InstrumentPreset":
        tree = ET.parse(path)
        root = tree.getroot()
        name = root.attrib.get("presetName", "Untitled")
        ui_elem = root.find(".//ui")
        ui_width = int(ui_elem.attrib.get("width", 812)) if ui_elem is not None else 812
        ui_height = int(ui_elem.attrib.get("height", 375)) if ui_elem is not None else 375
        bg_image = ui_elem.attrib.get("bgImage") if ui_elem is not None else None
        layout_mode = ui_elem.attrib.get("layoutMode", "relative") if ui_elem is not None else "relative"
        bg_mode = ui_elem.attrib.get("bgMode", "top_left") if ui_elem is not None else "top_left"
        # DSPreset UI flags
        have_reverb = ui_elem is not None and ui_elem.attrib.get("haveReverb", "false").lower() == "true"
        have_tone = ui_elem is not None and ui_elem.attrib.get("haveTone", "false").lower() == "true"
        have_chorus = ui_elem is not None and ui_elem.attrib.get("haveChorus", "false").lower() == "true"
        have_midicc1 = ui_elem is not None and ui_elem.attrib.get("haveMidicc1", "false").lower() == "true"
        no_attack = ui_elem is not None and ui_elem.attrib.get("noAttack", "false").lower() == "true"
        no_decay = ui_elem is not None and ui_elem.attrib.get("noDecay", "false").lower() == "true"
        # Parse UI elements
        ui_elements = []
        if ui_elem is not None:
            for tab in ui_elem.findall("tab"):
                for el in tab:
                    x = int(el.attrib.get("x", 0))
                    y = int(el.attrib.get("y", 0))
                    w = int(el.attrib.get("width", 64))
                    h = int(el.attrib.get("height", 64))
                    label = el.attrib.get("label", el.tag)
                    skin = el.attrib.get("skin", None)
                    ui_elements.append(UIElement(x, y, w, h, label, skin))
        mappings = []
        groups_elem = root.find(".//groups")
        if groups_elem is not None:
            for group in groups_elem.findall("group"):
                for sample in group.findall("sample"):
                    sample_path = sample.attrib.get("path", "")
                    lo = int(sample.attrib.get("loNote", 0))
                    hi = int(sample.attrib.get("hiNote", 127))
                    root_note = int(sample.attrib.get("rootNote", 60))
                    mappings.append(SampleMapping(sample_path, lo, hi, root_note))
        return InstrumentPreset(
            name, ui_width, ui_height, bg_image, layout_mode, bg_mode, mappings,
            have_reverb=have_reverb, have_tone=have_tone, have_chorus=have_chorus, have_midicc1=have_midicc1,
            no_attack=no_attack, no_decay=no_decay, ui_elements=ui_elements
        )

    def auto_map(self, folder_path: str):
        """
        Auto-map all .wav files in the given folder to consecutive MIDI notes starting from self.start_note.
        """
        import os
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
                root=note
            ))
            note += 1
        self.mappings = mappings

    def to_dspreset(self, path: str):
        root = ET.Element("DecentSampler", {"minVersion": "1.0.2", "presetName": self.name})
        ui_attribs = {
            "width": str(self.ui_width),
            "height": str(self.ui_height),
            "layoutMode": self.layout_mode,
            "bgMode": self.bg_mode,
            "haveReverb": "true" if getattr(self, "have_reverb", False) else "false",
            "haveTone": "true" if getattr(self, "have_tone", False) else "false",
            "haveChorus": "true" if getattr(self, "have_chorus", False) else "false",
            "haveMidicc1": "true" if getattr(self, "have_midicc1", False) else "false",
            "noAttack": "true" if getattr(self, "no_attack", False) else "false",
            "noDecay": "true" if getattr(self, "no_decay", False) else "false",
        }
        if self.bg_image:
            ui_attribs["bgImage"] = self.bg_image
        ui_elem = ET.SubElement(root, "ui", ui_attribs)
        tab_elem = ET.SubElement(ui_elem, "tab", {"name": "main"})
        # Write UI elements
        for el in getattr(self.ui, "elements", []):
            attribs = {
                "x": str(el.x),
                "y": str(el.y),
                "width": str(el.width),
                "height": str(el.height),
                "label": el.label
            }
            if el.skin:
                attribs["skin"] = el.skin
            ET.SubElement(tab_elem, "control", attribs)

        # Add controls as labeled-knobs with bindings
        knob_x = 200
        knob_y = 75
        knob_spacing = 70
        knob_idx = 0
        fx_position = -1
        def add_knob(label, min_val, max_val, value, param, binding_type, binding_level, binding_param, translation=None, translation_table=None):
            nonlocal knob_idx
            knob = ET.SubElement(tab_elem, "labeled-knob", {
                "x": str(knob_x + knob_idx * knob_spacing),
                "y": str(knob_y),
                "textSize": "16",
                "textColor": "AA000000",
                "trackForegroundColor": "CC000000",
                "trackBackgroundColor": "66999999",
                "label": label,
                "type": "float" if label != "Reverb" else "percent",
                "minValue": str(min_val),
                "maxValue": str(max_val),
                "value": str(value)
            })
            binding = ET.SubElement(knob, "binding", {
                "type": binding_type,
                "level": binding_level,
                "position": str(0 if binding_type == "amp" else fx_position),
                "parameter": binding_param
            })
            if translation:
                binding.set("translation", translation)
            if translation_table:
                binding.set("translationTable", translation_table)
            knob_idx += 1

        if self.have_attack:
            add_knob("Attack", 0.0, 10.0, 0.01, "ENV_ATTACK", "amp", "instrument", "ENV_ATTACK")
        if self.have_decay:
            add_knob("Decay", 0.0, 25.0, 1.0, "ENV_DECAY", "amp", "instrument", "ENV_DECAY")
        if self.have_sustain:
            add_knob("Sustain", 0.0, 1.0, 1.0, "ENV_SUSTAIN", "amp", "instrument", "ENV_SUSTAIN")
        if self.have_release:
            add_knob("Release", 0.0, 25.0, 0.43, "ENV_RELEASE", "amp", "instrument", "ENV_RELEASE")
        if self.have_chorus:
            fx_position += 1
            add_knob("Chorus", 0.0, 1.0, 0.0, "FX_MIX", "effect", "instrument", "FX_MIX")
        if self.have_tone:
            fx_position += 1
            add_knob("Tone", 0, 1, 1, "FX_FILTER_FREQUENCY", "effect", "instrument", "FX_FILTER_FREQUENCY", translation="table", translation_table="0,33;0.3,150;0.4,450;0.5,1100;0.7,4100;0.9,11000;1.0001,22000")
        if self.have_reverb:
            fx_position += 1
            add_knob("Reverb", 0, 100, 50, "FX_REVERB_WET_LEVEL", "effect", "instrument", "FX_REVERB_WET_LEVEL", translation="linear")

        # Groups and sample mapping
        groups_elem = ET.SubElement(root, "groups", {
            "attack": "0.000",
            "decay": "25",
            "sustain": "1.0",
            "release": "0.430",
            "volume": "-3dB"
        })
        group_elem = ET.SubElement(groups_elem, "group")
        if self.cut_all_by_all:
            group_elem.set("tags", "cutgroup0")
            group_elem.set("silencedByTags", "cutgroup0")
            group_elem.set("silencingMode", self.silencing_mode)
        for mapping in self.mappings:
            ET.SubElement(group_elem, "sample", {
                "path": mapping.path,
                "loNote": str(mapping.lo),
                "hiNote": str(mapping.hi),
                "rootNote": str(mapping.root)
            })

        # Effects section
        effects_elem = ET.SubElement(root, "effects")
        if self.have_chorus:
            ET.SubElement(effects_elem, "effect", {
                "type": "chorus",
                "mix": "0.0",
                "modDepth": "0.2",
                "modRate": "0.2"
            })
        if self.have_tone:
            ET.SubElement(effects_elem, "effect", {
                "type": "lowpass",
                "frequency": "22000.0"
            })
        if self.have_reverb:
            ET.SubElement(effects_elem, "effect", {
                "type": "reverb",
                "wetLevel": "0.5"
            })

        # MIDI CC mapping for tone knob
        if self.have_midicc1 and self.have_tone:
            midi_elem = ET.SubElement(root, "midi")
            cc_elem = ET.SubElement(midi_elem, "cc", {"number": "1"})
            binding = ET.SubElement(cc_elem, "binding", {
                "level": "ui",
                "type": "control",
                "parameter": "VALUE",
                "position": str(knob_idx - 1),
                "translation": "linear",
                "translationOutputMin": "0",
                "translationOutputMax": "1"
            })

        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)
