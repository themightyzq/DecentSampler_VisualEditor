"""Read .dspreset XML files into InstrumentPreset objects."""
import xml.etree.ElementTree as ET
from models.data_classes import (
    SampleZone, SampleMapping, GroupEnvelope, LFO,
    ModulatorTarget, ModulationRoute, UIElement,
)
from utils.effects_catalog import EFFECTS_CATALOG


def read_dspreset(path: str):
    """Load a .dspreset file and return an InstrumentPreset instance."""
    from models.instrument_preset import InstrumentPreset

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
        ui_elements = _parse_ui_elements(ui_elem)

    mappings = []
    zones = []
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
                _parse_sample(sample, mappings, zones)

    lfos, modulation_routes = _parse_modulators(root)

    effects = _parse_effects(root)

    from models.data_classes import SampleManager
    sample_manager = SampleManager()
    sample_manager.zones = zones

    return InstrumentPreset(
        name, ui_width, ui_height, bg_image, layout_mode, bg_mode, mappings,
        have_reverb=have_reverb, have_tone=have_tone, have_chorus=have_chorus,
        have_midicc1=have_midicc1, no_attack=no_attack, no_decay=no_decay,
        ui_elements=ui_elements, envelope=envelope, effects=effects,
        lfos=lfos, modulation_routes=modulation_routes,
        sample_manager=sample_manager,
    )


def _parse_ui_elements(ui_elem):
    """Parse UI elements from the <ui> XML element."""
    ui_elements = []
    keyboard_elem = ui_elem.find("keyboard")
    if keyboard_elem is not None:
        class KeyboardColorRange:
            def __init__(self, lo_note=0, hi_note=127, color="FF444444", pressed_color="FF888888"):
                self.lo_note = lo_note
                self.hi_note = hi_note
                self.color = color
                self.pressed_color = pressed_color

        keyboard_color_ranges = []
        for color_elem in keyboard_elem.findall("color"):
            lo_note = int(color_elem.attrib.get("loNote", 0))
            hi_note = int(color_elem.attrib.get("hiNote", 127))
            color = color_elem.attrib.get("color", "FF444444")
            pressed_color = color_elem.attrib.get("pressedColor", "FF888888")
            keyboard_color_ranges.append(KeyboardColorRange(lo_note, hi_note, color, pressed_color))

        ui_elements.append(UIElement(
            0, 0, 812, 60, "Keyboard", None, "keyboard", "keyboard",
            color_ranges=keyboard_color_ranges,
        ))

    for tab in ui_elem.findall("tab"):
        for el in tab:
            x = int(el.attrib.get("x", 0))
            y = int(el.attrib.get("y", 0))
            w = int(el.attrib.get("width", 64))
            h = int(el.attrib.get("height", 64))
            label = el.attrib.get("label", el.tag)
            skin = el.attrib.get("skin", None)
            tag = el.tag
            # Infer widget_type from XML tag name if not explicitly set
            _TAG_TO_WIDGET = {
                "labeled-knob": "Knob",
                "control": "Slider",
                "menu": "Menu",
                "label": "Label",
                "button": "Button",
                "image": "Image",
            }
            widget_type = el.attrib.get("widgetType", None) or _TAG_TO_WIDGET.get(tag)
            ui_elements.append(UIElement(x, y, w, h, label, skin, tag, widget_type))

    return ui_elements


def _parse_sample(sample_elem, mappings, zones):
    """Parse a <sample> element and append to mappings and zones."""
    sample_path = sample_elem.attrib.get("path", "")
    lo = int(sample_elem.attrib.get("loNote", 0))
    hi = int(sample_elem.attrib.get("hiNote", 127))
    root_note = int(sample_elem.attrib.get("rootNote", 60))

    velocity_range = (0, 127)
    if "velocityRange" in sample_elem.attrib:
        vel_str = sample_elem.attrib["velocityRange"]
        if "," in vel_str:
            vel_low, vel_high = map(int, vel_str.split(","))
            velocity_range = (vel_low, vel_high)

    seq_mode = sample_elem.attrib.get("seqMode", "round_robin")
    seq_position = int(sample_elem.attrib.get("seqPosition", 1))
    volume = float(sample_elem.attrib.get("volume", 0.0))
    pan = float(sample_elem.attrib.get("pan", 0.0))
    tune = float(sample_elem.attrib.get("tune", 0.0))
    start = int(sample_elem.attrib.get("start", 0))
    end = sample_elem.attrib.get("end")
    if end is not None:
        end = int(end)

    loop_enabled = sample_elem.attrib.get("loopEnabled", "false").lower() == "true"
    loop_start = sample_elem.attrib.get("loopStart")
    loop_end = sample_elem.attrib.get("loopEnd")
    loop_crossfade = float(sample_elem.attrib.get("loopCrossfade", 0.0))
    loop_mode = sample_elem.attrib.get("loopMode", "forward")

    if loop_start is not None:
        loop_start = int(loop_start)
    if loop_end is not None:
        loop_end = int(loop_end)

    zone = SampleZone(
        sample_path, root_note, lo, hi, velocity_range,
        seq_mode, seq_position, volume, pan, tune,
        start, end, loop_enabled, loop_start, loop_end,
        loop_crossfade, loop_mode,
    )
    zones.append(zone)

    mappings.append(SampleMapping(sample_path, lo, hi, root_note))


def _parse_modulators(root):
    """Parse <modulators> section, return (lfos, modulation_routes)."""
    lfos = []
    modulation_routes = []

    modulators_elem = root.find(".//modulators")
    if modulators_elem is None:
        return lfos, modulation_routes

    for lfo_elem in modulators_elem.findall("lfo"):
        lfo_name = lfo_elem.attrib.get("name", "LFO")
        lfo = LFO(
            lfo_name,
            float(lfo_elem.attrib.get("frequency", 1.0)),
            lfo_elem.attrib.get("waveform", "sine"),
            float(lfo_elem.attrib.get("amplitude", 1.0)),
            float(lfo_elem.attrib.get("offset", 0.0)),
            float(lfo_elem.attrib.get("phase", 0.0)),
            lfo_elem.attrib.get("sync", "free"),
            lfo_elem.attrib.get("syncLength", "1"),
            lfo_elem.attrib.get("retrigger", "false").lower() == "true",
        )
        lfos.append(lfo)

        for binding in lfo_elem.findall("binding"):
            target_type = binding.attrib.get("type", "amp")
            parameter = binding.attrib.get("parameter", "")
            level = binding.attrib.get("level", "instrument")
            position = int(binding.attrib.get("position", 0))
            group_index = binding.attrib.get("groupIndex")
            effect_index = binding.attrib.get("effectIndex")
            amount = float(binding.attrib.get("amount", 1.0))
            invert = binding.attrib.get("invert", "false").lower() == "true"

            if group_index is not None:
                group_index = int(group_index)
            if effect_index is not None:
                effect_index = int(effect_index)

            target = ModulatorTarget(target_type, parameter, level, position, group_index, effect_index)
            route = ModulationRoute(lfo_name, target, amount, invert)
            modulation_routes.append(route)

    return lfos, modulation_routes


def _parse_effects(root):
    """Parse <effects> section."""
    effects = {}
    effects_elem = root.find(".//effects")
    if effects_elem is None:
        return effects

    for eff in effects_elem.findall("effect"):
        eff_type = eff.attrib.get("type", "")
        for name, meta in EFFECTS_CATALOG.items():
            if meta["type"] == eff_type:
                effects[name] = {}
                for param in eff.attrib:
                    if param != "type":
                        effects[name][param] = eff.attrib[param]

    return effects
