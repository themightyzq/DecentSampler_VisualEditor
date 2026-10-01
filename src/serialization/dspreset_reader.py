"""Read .dspreset XML files into InstrumentPreset objects.

The reader builds the editor's model and also keeps the parsed XML tree, the
element each model object came from and the values it read. The writer patches
a copy of that tree, so anything the model does not represent (UI controls and
their bindings, group attributes, MIDI mappings, effect and modulator details,
tags, unknown elements and comments) is written back as it was read.
"""
import copy
import os
from models.data_classes import (
    SampleZone, SampleMapping, GroupEnvelope, LFO,
    ModulatorTarget, ModulationRoute, UIElement,
)
from utils.effects_catalog import EFFECTS_CATALOG
from serialization.xml_common import (
    is_element, parse_tree, to_number, zone_attrs, lfo_attrs, binding_attrs,
    ui_root_attrs, ui_element_attrs, color_range_tuples, global_block_flags,
)


def read_dspreset(path: str):
    """Load a .dspreset file and return an InstrumentPreset instance."""
    from models.instrument_preset import InstrumentPreset

    tree = parse_tree(path)
    root = tree.getroot()
    bound = []  # (source element, model object) pairs for the writer
    # Sample paths in a .dspreset are relative to the preset file's folder.
    preset_dir = os.path.dirname(os.path.abspath(path))
    name = root.attrib.get("presetName", "Untitled")

    ui_elem = root.find("ui")
    ui_width = to_number(ui_elem.attrib.get("width"), int, 812) if ui_elem is not None else 812
    ui_height = to_number(ui_elem.attrib.get("height"), int, 375) if ui_elem is not None else 375
    bg_color = ui_elem.attrib.get("bgColor") if ui_elem is not None else None
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
        ui_elements = _parse_ui_elements(ui_elem, bound)

    mappings = []
    zones = []
    envelope = GroupEnvelope()

    groups_elem = root.find("groups")
    if groups_elem is not None:
        for group in groups_elem.findall("group"):
            env_elem = group.find("envelope")
            if env_elem is not None:
                envelope.attack = to_number(env_elem.attrib.get("attack"), float, 0.01)
                envelope.decay = to_number(env_elem.attrib.get("decay"), float, 1.0)
                envelope.sustain = to_number(env_elem.attrib.get("sustain"), float, 1.0)
                envelope.release = to_number(env_elem.attrib.get("release"), float, 0.43)
            for sample in group.findall("sample"):
                _parse_sample(sample, mappings, zones, preset_dir, bound)

    lfos, modulation_routes = _parse_modulators(root, bound)

    effects = _parse_effects(root)

    from models.data_classes import SampleManager
    sample_manager = SampleManager()
    sample_manager.zones = zones

    preset = InstrumentPreset(
        name, ui_width, ui_height, bg_image, layout_mode, bg_mode, mappings,
        have_reverb=have_reverb, have_tone=have_tone, have_chorus=have_chorus,
        have_midicc1=have_midicc1, no_attack=no_attack, no_decay=no_decay,
        ui_elements=ui_elements, envelope=envelope, effects=effects,
        lfos=lfos, modulation_routes=modulation_routes,
        sample_manager=sample_manager,
    )
    preset.bg_color = bg_color

    # Source tree and the values the editor modelled, for patch-style writing.
    preset.source_root = root
    preset.source_path = os.path.abspath(path)
    preset.source_bound = bound
    preset.as_read = {
        "name": name,
        "ui_attrs": ui_root_attrs(preset),
        "envelope": (envelope.attack, envelope.decay, envelope.sustain, envelope.release),
        "effects": copy.deepcopy(effects),
        "global_blocks": global_block_flags(preset),
    }
    return preset


def _parse_ui_elements(ui_elem, bound):
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
            lo_note = to_number(color_elem.attrib.get("loNote"), int, 0)
            hi_note = to_number(color_elem.attrib.get("hiNote"), int, 127)
            color = color_elem.attrib.get("color", "FF444444")
            pressed_color = color_elem.attrib.get("pressedColor", "FF888888")
            keyboard_color_ranges.append(KeyboardColorRange(lo_note, hi_note, color, pressed_color))

        keyboard = UIElement(
            0, 0, 812, 60, "Keyboard", None, "keyboard", "keyboard",
            color_ranges=keyboard_color_ranges,
        )
        keyboard.source_elem = keyboard_elem
        keyboard.source_color_ranges = color_range_tuples(keyboard)
        bound.append((keyboard_elem, keyboard))
        ui_elements.append(keyboard)

    for tab in ui_elem.findall("tab"):
        for el in tab:
            if not is_element(el):  # comment or processing instruction
                continue
            x = to_number(el.attrib.get("x"), int, 0)
            y = to_number(el.attrib.get("y"), int, 0)
            w = to_number(el.attrib.get("width"), int, 64)
            h = to_number(el.attrib.get("height"), int, 64)
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
            element = UIElement(x, y, w, h, label, skin, tag, widget_type)
            element.source_elem = el
            element.source_attrs = ui_element_attrs(element)
            bound.append((el, element))
            ui_elements.append(element)

    return ui_elements


def _parse_sample(sample_elem, mappings, zones, preset_dir=None, bound=None):
    """Parse a <sample> element and append to mappings and zones.

    Relative sample paths are resolved against preset_dir (the directory of the
    .dspreset being read) so they stay valid regardless of the working directory.
    Absolute paths are left unchanged.
    """
    path_attr = sample_elem.attrib.get("path", "")
    sample_path = path_attr
    if sample_path and preset_dir and not os.path.isabs(sample_path):
        sample_path = os.path.normpath(os.path.join(preset_dir, sample_path))
    lo = to_number(sample_elem.attrib.get("loNote"), int, 0)
    hi = to_number(sample_elem.attrib.get("hiNote"), int, 127)
    root_note = to_number(sample_elem.attrib.get("rootNote"), int, 60)

    velocity_range = (0, 127)
    if "velocityRange" in sample_elem.attrib:
        vel_str = sample_elem.attrib["velocityRange"]
        if "," in vel_str:
            try:
                vel_low, vel_high = map(int, vel_str.split(","))
                velocity_range = (vel_low, vel_high)
            except ValueError:
                pass

    seq_mode = sample_elem.attrib.get("seqMode", "round_robin")
    seq_position = to_number(sample_elem.attrib.get("seqPosition"), int, 1)
    volume = to_number(sample_elem.attrib.get("volume"), float, 0.0)
    pan = to_number(sample_elem.attrib.get("pan"), float, 0.0)
    tune = to_number(sample_elem.attrib.get("tune"), float, 0.0)
    start = to_number(sample_elem.attrib.get("start"), int, 0)
    end = to_number(sample_elem.attrib.get("end"), int, None)

    loop_enabled = sample_elem.attrib.get("loopEnabled", "false").lower() == "true"
    loop_start = to_number(sample_elem.attrib.get("loopStart"), int, None)
    loop_end = to_number(sample_elem.attrib.get("loopEnd"), int, None)
    loop_crossfade = to_number(sample_elem.attrib.get("loopCrossfade"), float, 0.0)
    loop_mode = sample_elem.attrib.get("loopMode", "forward")

    zone = SampleZone(
        sample_path, root_note, lo, hi, velocity_range,
        seq_mode, seq_position, volume, pan, tune,
        start, end, loop_enabled, loop_start, loop_end,
        loop_crossfade, loop_mode,
    )
    zone.source_elem = sample_elem
    zone.source_path_attr = path_attr
    zone.source_path = sample_path
    zone.source_attrs = zone_attrs(zone)
    if bound is not None:
        bound.append((sample_elem, zone))
    zones.append(zone)

    mappings.append(SampleMapping(sample_path, lo, hi, root_note))


def _parse_modulators(root, bound=None):
    """Parse <modulators> section, return (lfos, modulation_routes)."""
    lfos = []
    modulation_routes = []

    modulators_elem = root.find("modulators")
    if modulators_elem is None:
        return lfos, modulation_routes

    for lfo_elem in modulators_elem.findall("lfo"):
        lfo_name = lfo_elem.attrib.get("name", "LFO")
        lfo = LFO(
            lfo_name,
            to_number(lfo_elem.attrib.get("frequency"), float, 1.0),
            lfo_elem.attrib.get("waveform", "sine"),
            to_number(lfo_elem.attrib.get("amplitude"), float, 1.0),
            to_number(lfo_elem.attrib.get("offset"), float, 0.0),
            to_number(lfo_elem.attrib.get("phase"), float, 0.0),
            lfo_elem.attrib.get("sync", "free"),
            lfo_elem.attrib.get("syncLength", "1"),
            lfo_elem.attrib.get("retrigger", "false").lower() == "true",
        )
        lfo.source_elem = lfo_elem
        lfo.source_attrs = lfo_attrs(lfo)
        if bound is not None:
            bound.append((lfo_elem, lfo))
        lfos.append(lfo)

        for binding in lfo_elem.findall("binding"):
            target_type = binding.attrib.get("type", "amp")
            parameter = binding.attrib.get("parameter", "")
            level = binding.attrib.get("level", "instrument")
            position = to_number(binding.attrib.get("position"), int, 0)
            group_index = binding.attrib.get("groupIndex")
            effect_index = binding.attrib.get("effectIndex")
            amount = to_number(binding.attrib.get("amount"), float, 1.0)
            invert = binding.attrib.get("invert", "false").lower() == "true"

            group_index = to_number(group_index, int, None)
            effect_index = to_number(effect_index, int, None)

            target = ModulatorTarget(target_type, parameter, level, position, group_index, effect_index)
            route = ModulationRoute(lfo_name, target, amount, invert)
            route.source_elem = binding
            route.source_attrs = binding_attrs(route)
            if bound is not None:
                bound.append((binding, route))
            modulation_routes.append(route)

    return lfos, modulation_routes


def _parse_effects(root):
    """Parse <effects> section."""
    effects = {}
    effects_elem = root.find("effects")
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
