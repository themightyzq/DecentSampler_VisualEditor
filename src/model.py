import xml.etree.ElementTree as ET
from typing import List, Optional
from utils.effects_catalog import EFFECTS_CATALOG

class SampleMapping:
    def __init__(self, path: str, lo: int, hi: int, root: int):
        self.path = path
        self.lo = lo
        self.hi = hi
        self.root = root

    def __repr__(self):
        return f"SampleMapping(path={self.path!r}, lo={self.lo}, hi={self.hi}, root={self.root})"

class GroupEnvelope:
    def __init__(self, attack=0.01, decay=1.0, sustain=1.0, release=0.43):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

class UIElement:
    def __init__(self, x, y, width, height, label, skin=None, tag=None, widget_type=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.skin = skin  # path to skin image or None
        self.tag = tag
        self.widget_type = widget_type

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
        effects: Optional[dict] = None,  # New: effect parameter values
        advanced_mode: bool = False      # New: simple/advanced toggle
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
        self.envelope = envelope if envelope is not None else GroupEnvelope()
        self.effects = effects if effects is not None else {}  # {effect_name: {param: value, ...}}
        self.advanced_mode = advanced_mode

    @staticmethod
    def from_dspreset(path: str) -> "InstrumentPreset":
        # (Legacy loading: not yet data-driven for all effects, but can be extended)
        tree = ET.parse(path)
        root = tree.getroot()
        name = root.attrib.get("presetName", "Untitled")
        ui_elem = root.find(".//ui")
        ui_width = int(ui_elem.attrib.get("width", 812)) if ui_elem is not None else 812
        ui_height = int(ui_elem.attrib.get("height", 375)) if ui_elem is not None else 375
        bg_image = ui_elem.attrib.get("bgImage") if ui_elem is not None else None
        layout_mode = ui_elem.attrib.get("layoutMode", "relative") if ui_elem is not None else "relative"
        bg_mode = ui_elem.attrib.get("bgMode", "top_left") if ui_elem is not None else "top_left"
        have_reverb = ui_elem is not None and ui_elem.attrib.get("haveReverb", "false").lower() == "true"
        have_tone = ui_elem is not None and ui_elem.attrib.get("haveTone", "false").lower() == "true"
        have_chorus = ui_elem is not None and ui_elem.attrib.get("haveChorus", "false").lower() == "true"
        have_midicc1 = ui_elem is not None and ui_elem.attrib.get("haveMidicc1", "false").lower() == "true"
        no_attack = ui_elem is not None and ui_elem.attrib.get("noAttack", "false").lower() == "true"
        no_decay = ui_elem is not None and ui_elem.attrib.get("noDecay", "false").lower() == "true"
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
                    tag = el.tag
                    widget_type = el.attrib.get("widgetType", None)
                    ui_elements.append(UIElement(x, y, w, h, label, skin, tag, widget_type))
        mappings = []
        envelope = GroupEnvelope()
        groups_elem = root.find(".//groups")
        if groups_elem is not None:
            for group in groups_elem.findall("group"):
                env_elem = group.find("envelope")
                if env_elem is not None:
                    envelope.attack = float(env_elem.attrib.get("attack", 0.01))
                    envelope.decay = float(env_elem.attrib.get("decay", 1.0))
                    envelope.sustain = float(env_elem.attrib.get("sustain", 1.0))
                    envelope.release = float(env_elem.attrib.get("release", 0.43))
                for sample in group.findall("sample"):
                    sample_path = sample.attrib.get("path", "")
                    lo = int(sample.attrib.get("loNote", 0))
                    hi = int(sample.attrib.get("hiNote", 127))
                    root_note = int(sample.attrib.get("rootNote", 60))
                    mappings.append(SampleMapping(sample_path, lo, hi, root_note))
        # Effects loading (basic, can be extended for full param support)
        effects_elem = root.find(".//effects")
        effects = {}
        if effects_elem is not None:
            for eff in effects_elem.findall("effect"):
                eff_type = eff.attrib.get("type", "")
                for name, meta in EFFECTS_CATALOG.items():
                    if meta["type"] == eff_type:
                        effects[name] = {}
                        for param in eff.attrib:
                            if param != "type":
                                effects[name][param] = eff.attrib[param]
        return InstrumentPreset(
            name, ui_width, ui_height, bg_image, layout_mode, bg_mode, mappings,
            have_reverb=have_reverb, have_tone=have_tone, have_chorus=have_chorus, have_midicc1=have_midicc1,
            no_attack=no_attack, no_decay=no_decay, ui_elements=ui_elements, envelope=envelope,
            effects=effects
        )

    def auto_map(self, folder_path: str):
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
        custom_labels = [el.label for el in getattr(self.ui, "elements", [])]
        ui_attribs = {
            "width": str(self.ui_width),
            "height": str(self.ui_height),
            "layoutMode": self.layout_mode,
            "bgMode": self.bg_mode,
            "haveReverb": "false" if "Reverb" in custom_labels else ("true" if getattr(self, "have_reverb", False) else "false"),
            "haveTone": "false" if "Tone" in custom_labels else ("true" if getattr(self, "have_tone", False) else "false"),
            "haveChorus": "false" if "Chorus" in custom_labels else ("true" if getattr(self, "have_chorus", False) else "false"),
            "haveMidicc1": "false" if "MIDI CC1" in custom_labels else ("true" if getattr(self, "have_midicc1", False) else "false"),
            "noAttack": "true" if getattr(self, "no_attack", False) else "false",
            "noDecay": "true" if getattr(self, "no_decay", False) else "false",
        }
        if self.bg_image:
            ui_attribs["bgImage"] = self.bg_image
        ui_elem = ET.SubElement(root, "ui", ui_attribs)
        tab_elem = ET.SubElement(ui_elem, "tab", {"name": "main"})
        # Write UI elements
        used_labels = {}
        for el in getattr(self.ui, "elements", []):
            # Ensure unique label
            base_label = str(getattr(el, "label", "Control"))
            label = base_label
            count = used_labels.get(base_label, 0)
            if count > 0:
                label = f"{base_label}_{count+1}"
            used_labels[base_label] = count + 1

            # Validate min/max/default
            min_val = float(getattr(el, "min", 0.0))
            max_val = float(getattr(el, "max", 1.0))
            default_val = float(getattr(el, "default", (min_val + max_val) / 2.0))
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            if not (min_val <= default_val <= max_val):
                default_val = (min_val + max_val) / 2.0

            # UIControl type
            control_type = str(getattr(el, "widget_type", "Knob")).lower()
            if control_type not in ("knob", "slider"):
                control_type = "knob"

            # <uiControl> element
            ui_control_attribs = {
                "name": label,
                "type": control_type,
                "x": str(getattr(el, "x", 0)),
                "y": str(getattr(el, "y", 0)),
                "min": str(min_val),
                "max": str(max_val),
                "default": str(default_val)
            }
            ET.SubElement(tab_elem, "uiControl", ui_control_attribs)

            # <modulator> or parameter mapping
            effect_type = getattr(el, "effect_type", None)
            parameter = getattr(el, "parameter", None)
            if effect_type and parameter:
                # Route to <fx> node by effect type and parameter
                mod_attribs = {
                    "source": label,
                    "target": f"{effect_type}.{parameter}"
                }
                ET.SubElement(tab_elem, "modulator", mod_attribs)

            # (Legacy: also add label and control for backward compatibility)
            style_map = {
                "knob": "rotary",
                "slider": "linear_vertical",
                "button": "button",
                "menu": "menu"
            }
            style = style_map.get((el.widget_type or "").lower(), "rotary")
            if style == "rotary":
                width, height = 64, 64
            elif style == "linear_vertical":
                width, height = 30, 90
            elif style == "button":
                width, height = 64, 32
            elif style == "menu":
                width, height = 150, 25
            else:
                width, height = el.width, el.height
            param_map = {
                "Reverb": "FX_REVERB_WET_LEVEL",
                "Tone": "FX_FILTER_FREQUENCY",
                "Chorus": "FX_MIX",
                "MIDI CC1": "VALUE"
            }
            param = param_map.get(el.label, el.label.upper())
            label_attribs = {
                "x": str(el.x),
                "y": str(max(0, el.y - 20)),
                "width": str(width),
                "height": "20",
                "text": el.label,
                "textColor": "FFFFFFFF",
                "textSize": "14",
                "hAlign": "center"
            }
            ET.SubElement(tab_elem, "label", label_attribs)
            attribs = {
                "x": str(el.x),
                "y": str(el.y),
                "width": str(width),
                "height": str(height),
                "parameterName": param,
                "style": style,
                "minValue": "0",
                "maxValue": "1",
                "value": "0.5",
                "textColor": "FFFFFFFF",
                "trackForegroundColor": "FFCCCCCC",
                "trackBackgroundColor": "66999999"
            }
            if el.skin:
                attribs["skin"] = el.skin
            control_elem = ET.SubElement(tab_elem, "control", attribs)
            binding_attribs = {
                "type": "effect" if el.label in ("Reverb", "Tone", "Chorus") else "control",
                "level": "instrument",
                "position": "0",
                "parameter": param
            }
            ET.SubElement(control_elem, "binding", binding_attribs)

        # Add controls as labeled-knobs with bindings (legacy, for ADSR and legacy effects)
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

        custom_labels_set = set(custom_labels)
        if self.have_attack and "Attack" not in custom_labels_set:
            add_knob("Attack", 0.0, 10.0, getattr(self.envelope, "attack", 0.01), "ENV_ATTACK", "amp", "instrument", "ENV_ATTACK")
        if self.have_decay and "Decay" not in custom_labels_set:
            add_knob("Decay", 0.0, 25.0, getattr(self.envelope, "decay", 1.0), "ENV_DECAY", "amp", "instrument", "ENV_DECAY")
        if self.have_sustain and "Sustain" not in custom_labels_set:
            add_knob("Sustain", 0.0, 1.0, getattr(self.envelope, "sustain", 1.0), "ENV_SUSTAIN", "amp", "instrument", "ENV_SUSTAIN")
        if self.have_release and "Release" not in custom_labels_set:
            add_knob("Release", 0.0, 25.0, getattr(self.envelope, "release", 0.43), "ENV_RELEASE", "amp", "instrument", "ENV_RELEASE")

        # Data-driven effects section
        effects_elem = ET.SubElement(root, "effects")
        for effect_name, params in self.effects.items():
            if effect_name in EFFECTS_CATALOG:
                eff_meta = EFFECTS_CATALOG[effect_name]
                eff_type = eff_meta["type"]
                eff_params = {"type": eff_type}
                # Use advanced or simple param set
                param_defs = eff_meta["advanced"] if self.advanced_mode else eff_meta["simple"]
                for param_def in param_defs:
                    pname = param_def["name"]
                    if pname in params:
                        eff_params[pname] = str(params[pname])
                    else:
                        eff_params[pname] = str(param_def.get("default", ""))
                ET.SubElement(effects_elem, "effect", eff_params)

        # Groups and sample mapping
        groups_elem = ET.SubElement(root, "groups", {
            "attack": "0.000",
            "decay": "25",
            "sustain": "1.0",
            "release": "0.430",
            "volume": "-3dB"
        })
        group_elem = ET.SubElement(groups_elem, "group")
        if hasattr(self, "envelope"):
            ET.SubElement(group_elem, "envelope", {
                "attack": str(getattr(self.envelope, "attack", 0.01)),
                "decay": str(getattr(self.envelope, "decay", 1.0)),
                "sustain": str(getattr(self.envelope, "sustain", 1.0)),
                "release": str(getattr(self.envelope, "release", 0.43)),
            })
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

        # MIDI CC mapping for tone knob (legacy)
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

        # Pretty-print XML using minidom
        import xml.dom.minidom
        rough_string = ET.tostring(root, encoding="utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")
        with open(path, "wb") as f:
            f.write(pretty_xml)
