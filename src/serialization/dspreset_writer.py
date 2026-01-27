"""Export InstrumentPreset to .dspreset XML files."""
import os
import shutil
import xml.dom.minidom
import xml.etree.ElementTree as ET
from models.data_classes import SampleZone


def write_dspreset(preset, path: str):
    """Write an InstrumentPreset to a .dspreset XML file."""
    # --- VALIDATION ---
    zones = preset.sample_manager.get_zones() if preset.sample_manager and preset.sample_manager.get_zones() else [
        SampleZone(m.path, m.root, m.lo, m.hi) for m in preset.mappings
    ]
    if not zones:
        raise Exception("Export aborted: At least one sample must be loaded.")

    controls = [el for el in getattr(preset.ui, "elements", [])
                if str(getattr(el, "widget_type", "")).lower() in ("knob", "slider")]

    for el in controls:
        label = getattr(el, "label", None)
        min_val = getattr(el, "min_val", None)
        max_val = getattr(el, "max_val", None)
        if min_val is None:
            el.min_val = 0
        if max_val is None:
            el.max_val = 1

    # Build control name map
    export_controls = [
        el for el in controls
        if getattr(el, "target", None) and isinstance(getattr(el, "target", None), str) and getattr(el, "target", "").strip()
    ]
    used_names = set()
    control_name_map = {}
    for el in export_controls:
        base_name = str(getattr(el, "label", "Control"))
        name = base_name
        i = 1
        while name in used_names:
            name = f"{base_name}_{i}"
            i += 1
        used_names.add(name)
        control_name_map[el] = name

    # --- BUILD XML ---
    root = ET.Element("DecentSampler", {"minVersion": "1.0.2", "presetName": preset.name})

    _write_ui_section(preset, root, control_name_map)
    _write_lfo_modulators(preset, root)
    _write_effects_section(preset, root)
    _write_groups_section(preset, root, zones, path)
    _write_midi_and_params(preset, root, control_name_map)

    # Pretty-print
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")
    with open(path, "wb") as f:
        f.write(pretty_xml)


def _write_ui_section(preset, root, control_name_map):
    """Write the <ui> section with controls, menus, and keyboard."""
    custom_labels = [el.label for el in getattr(preset.ui, "elements", [])]
    bg_color = getattr(preset, "bg_color", None)
    if not bg_color or len(bg_color) not in (8, 9):
        bg_color = "FF222222"
    if bg_color.startswith("#"):
        bg_color = bg_color[1:]

    ui_attribs = {
        "width": str(preset.ui_width),
        "height": str(preset.ui_height),
        "bgColor": bg_color,
        "layoutMode": preset.layout_mode,
        "bgMode": preset.bg_mode,
        "haveReverb": "false" if "Reverb" in custom_labels else ("true" if getattr(preset, "have_reverb", False) else "false"),
        "haveTone": "false" if "Tone" in custom_labels else ("true" if getattr(preset, "have_tone", False) else "false"),
        "haveChorus": "false" if "Chorus" in custom_labels else ("true" if getattr(preset, "have_chorus", False) else "false"),
        "haveMidicc1": "false" if "MIDI CC1" in custom_labels else ("true" if getattr(preset, "have_midicc1", False) else "false"),
        "noAttack": "true" if getattr(preset, "no_attack", False) else "false",
        "noDecay": "true" if getattr(preset, "no_decay", False) else "false",
    }
    if preset.bg_image:
        ui_attribs["bgImage"] = preset.bg_image

    ui_elem = ET.SubElement(root, "ui", ui_attribs)
    tab_elem = ET.SubElement(ui_elem, "tab", {"name": "main"})

    used_names = set()
    for el in getattr(preset.ui, "elements", []):
        # Menu/option support
        if getattr(el, "tag", None) == "Menu" or getattr(el, "widget_type", None) == "Menu":
            _write_menu_element(el, tab_elem)
            continue

        control_type = str(getattr(el, "widget_type", "Knob")).lower()
        target = getattr(el, "target", None)
        if control_type not in ("knob", "slider", "control") or not target or not isinstance(target, str) or not target.strip():
            continue

        base_name = str(getattr(el, "label", "Control"))
        name = base_name
        i = 1
        while name in used_names:
            name = f"{base_name}_{i}"
            i += 1
        used_names.add(name)

        if str(getattr(el, "widget_type", "Knob")).lower() == "slider":
            _write_slider_element(el, name, tab_elem)
        else:
            _write_knob_element(el, name, tab_elem)

    # Keyboard widget
    keyboard_elements = [el for el in getattr(preset.ui, "elements", []) if getattr(el, "tag", None) == "keyboard"]
    if keyboard_elements:
        keyboard_elem = ET.SubElement(ui_elem, "keyboard")
        for color_range in getattr(keyboard_elements[0], "color_ranges", []):
            ET.SubElement(keyboard_elem, "color", {
                "loNote": str(color_range.lo_note),
                "hiNote": str(color_range.hi_note),
                "color": color_range.color,
                "pressedColor": color_range.pressed_color,
            })


def _write_menu_element(el, tab_elem):
    menu_attribs = {
        "x": str(getattr(el, "x", 0)),
        "y": str(getattr(el, "y", 0)),
        "width": str(getattr(el, "width", 120)),
        "height": str(getattr(el, "height", 30)),
        "value": str(getattr(el, "value", 1)),
        "textColor": getattr(el, "textColor", "FF000000"),
    }
    menu_elem = ET.SubElement(tab_elem, "menu", menu_attribs)
    for opt in getattr(el, "options", []):
        option_elem = ET.SubElement(menu_elem, "option", {"name": getattr(opt, "name", "Option")})
        for binding in getattr(opt, "bindings", []):
            ET.SubElement(option_elem, "binding", {k: str(v) for k, v in binding.items() if v is not None})


def _build_control_attribs(el, name):
    """Build common control attribute dict."""
    min_val = getattr(el, "min_val", None)
    max_val = getattr(el, "max_val", None)
    if min_val is None:
        min_val = 0
    if max_val is None:
        max_val = 1
    value = getattr(el, "default", min_val)
    attribs = {
        "x": str(getattr(el, "x", 0)),
        "y": str(getattr(el, "y", 0)),
        "width": str(getattr(el, "width", 64)),
        "height": str(getattr(el, "height", 64)),
        "type": "float",
        "minValue": str(min_val),
        "maxValue": str(max_val),
        "value": str(value),
        "textColor": getattr(el, "textColor", "FF000000"),
        "textSize": getattr(el, "textSize", "12"),
    }
    style = getattr(el, "style", None)
    orientation = getattr(el, "orientation", None)
    track_fg = getattr(el, "trackForegroundColor", None)
    track_bg = getattr(el, "trackBackgroundColor", None)
    show_label = getattr(el, "showLabel", None)
    default_value = getattr(el, "default", None)
    if style:
        attribs["style"] = style
    if orientation:
        attribs["orientation"] = orientation
    if track_fg:
        attribs["trackForegroundColor"] = track_fg
    if track_bg:
        attribs["trackBackgroundColor"] = track_bg
    if show_label is not None:
        attribs["showLabel"] = str(show_label).lower()
    if default_value is not None:
        attribs["defaultValue"] = str(default_value)
    return attribs


def _write_knob_element(el, name, tab_elem):
    attribs = _build_control_attribs(el, name)
    attribs["label"] = name
    knob_elem = ET.SubElement(tab_elem, "labeled-knob", attribs)
    for binding in getattr(el, "bindings", []):
        ET.SubElement(knob_elem, "binding", {k: str(v) for k, v in binding.items() if v is not None})


def _write_slider_element(el, name, tab_elem):
    attribs = _build_control_attribs(el, name)
    attribs["parameterName"] = name
    style = "linear_vertical" if getattr(el, "orientation", None) == "vertical" else "linear_horizontal"
    attribs["style"] = style
    control_elem = ET.SubElement(tab_elem, "control", attribs)
    for binding in getattr(el, "bindings", []):
        ET.SubElement(control_elem, "binding", {k: str(v) for k, v in binding.items() if v is not None})


def _write_lfo_modulators(preset, root):
    """Write <modulators> section."""
    if not preset.lfos:
        return
    modulators_elem = ET.SubElement(root, "modulators")
    for lfo in preset.lfos:
        lfo_attribs = {
            "name": lfo.name,
            "frequency": str(lfo.frequency),
            "waveform": lfo.waveform,
            "amplitude": str(lfo.amplitude),
            "offset": str(lfo.offset),
            "phase": str(lfo.phase),
            "sync": lfo.sync,
            "syncLength": lfo.sync_length,
            "retrigger": str(lfo.retrigger).lower(),
        }
        lfo_elem = ET.SubElement(modulators_elem, "lfo", lfo_attribs)

        lfo_routes = [route for route in preset.modulation_routes if route.modulator_name == lfo.name]
        for route in lfo_routes:
            binding_attribs = {
                "type": route.target.target_type,
                "parameter": route.target.parameter,
                "level": route.target.level,
                "position": str(route.target.position),
                "amount": str(route.amount),
            }
            if route.target.group_index is not None:
                binding_attribs["groupIndex"] = str(route.target.group_index)
            if route.target.effect_index is not None:
                binding_attribs["effectIndex"] = str(route.target.effect_index)
            if route.invert:
                binding_attribs["invert"] = "true"
            ET.SubElement(lfo_elem, "binding", binding_attribs)


def _write_effects_section(preset, root):
    """Write <effects> section."""
    effects_elem = ET.SubElement(root, "effects")
    effect_controls = [el for el in getattr(preset.ui, "elements", []) if any(
        b.get("type") == "effect" for b in getattr(el, "bindings", []))]

    effect_param_map = {}
    for el in effect_controls:
        for binding in getattr(el, "bindings", []):
            if binding.get("type") == "effect":
                effect_type = binding.get("effectType")
                param = binding.get("parameter")
                value = getattr(el, "default", getattr(el, "min_val", 0))
                if effect_type and param:
                    if effect_type not in effect_param_map:
                        effect_param_map[effect_type] = {}
                    effect_param_map[effect_type][param] = str(value)

    for effect_type, params in effect_param_map.items():
        eff_params = {"type": effect_type}
        eff_params.update(params)
        ET.SubElement(effects_elem, "effect", eff_params)


def _write_groups_section(preset, root, zones, path):
    """Write <groups> section with samples."""
    groups_elem = ET.SubElement(root, "groups", {"volume": "-3dB"})
    samples_dir = os.path.join(os.path.dirname(path), "samples")
    os.makedirs(samples_dir, exist_ok=True)
    used_filenames = set()

    if hasattr(preset, 'sample_groups') and preset.sample_groups:
        for group in preset.sample_groups:
            if not group.samples:
                continue

            group_attribs = {"enabled": str(group.enabled).lower()}
            if group.volume != 0.0:
                group_attribs["volume"] = f"{group.volume}dB"
            if group.pan != 0.0:
                group_attribs["pan"] = str(group.pan)
            if group.tags:
                group_attribs["tags"] = ",".join(group.tags)

            if any(x is not None for x in [group.attack, group.decay, group.sustain, group.release]):
                if group.attack is not None:
                    group_attribs["attack"] = str(group.attack)
                if group.decay is not None:
                    group_attribs["decay"] = str(group.decay)
                if group.sustain is not None:
                    group_attribs["sustain"] = str(group.sustain)
                if group.release is not None:
                    group_attribs["release"] = str(group.release)

            if preset.cut_all_by_all:
                group_attribs["tags"] = "cutgroup0"
                group_attribs["silencedByTags"] = "cutgroup0"
                group_attribs["silencingMode"] = preset.silencing_mode

            group_elem = ET.SubElement(groups_elem, "group", group_attribs)
            for zone in group.samples:
                _export_sample_to_group(zone, group_elem, samples_dir, used_filenames, path)
    else:
        for zone in zones:
            group_elem = ET.SubElement(groups_elem, "group", {"enabled": "true"})
            if preset.cut_all_by_all:
                group_elem.set("tags", "cutgroup0")
                group_elem.set("silencedByTags", "cutgroup0")
                group_elem.set("silencingMode", preset.silencing_mode)
            _export_sample_to_group(zone, group_elem, samples_dir, used_filenames, path)


def _export_sample_to_group(zone, group_elem, samples_dir, used_filenames, preset_path):
    """Export a single sample to a group element."""
    orig_path = zone.path
    if not os.path.isfile(orig_path):
        raise Exception(f"Sample file not found: {orig_path}")

    base_filename = os.path.basename(orig_path)
    unique_filename = base_filename
    i = 1
    while unique_filename in used_filenames:
        name, ext = os.path.splitext(base_filename)
        unique_filename = f"{name}_{i}{ext}"
        i += 1
    used_filenames.add(unique_filename)

    dest_path = os.path.join(samples_dir, unique_filename)
    xml_rel_path = os.path.join("samples", unique_filename)

    if not os.path.exists(dest_path) or os.path.getmtime(orig_path) > os.path.getmtime(dest_path):
        shutil.copy2(orig_path, dest_path)

    xml_rel_path = xml_rel_path.replace("\\", "/")

    sample_attribs = {
        "path": xml_rel_path,
        "rootNote": str(zone.rootNote),
        "loNote": str(zone.loNote),
        "hiNote": str(zone.hiNote),
    }

    if hasattr(zone, "velocityRange") and zone.velocityRange != (0, 127):
        sample_attribs["velocityRange"] = f"{zone.velocityRange[0]},{zone.velocityRange[1]}"
    if hasattr(zone, "tags") and zone.tags:
        sample_attribs["tags"] = ",".join(zone.tags)
    if hasattr(zone, "seqMode") and zone.seqMode != "round_robin":
        sample_attribs["seqMode"] = zone.seqMode
    if hasattr(zone, "seqPosition") and zone.seqPosition != 1:
        sample_attribs["seqPosition"] = str(zone.seqPosition)
    if hasattr(zone, "volume") and zone.volume != 0.0:
        sample_attribs["volume"] = str(zone.volume)
    if hasattr(zone, "pan") and zone.pan != 0.0:
        sample_attribs["pan"] = str(zone.pan)
    if hasattr(zone, "tune") and zone.tune != 0.0:
        sample_attribs["tune"] = str(zone.tune)
    if hasattr(zone, "start") and zone.start != 0:
        sample_attribs["start"] = str(zone.start)
    if hasattr(zone, "end") and zone.end is not None:
        sample_attribs["end"] = str(zone.end)

    if hasattr(zone, "loopEnabled") and zone.loopEnabled:
        sample_attribs["loopEnabled"] = "true"
        if hasattr(zone, "loopStart") and zone.loopStart is not None:
            sample_attribs["loopStart"] = str(zone.loopStart)
        if hasattr(zone, "loopEnd") and zone.loopEnd is not None:
            sample_attribs["loopEnd"] = str(zone.loopEnd)
        if hasattr(zone, "loopCrossfade") and zone.loopCrossfade != 0.0:
            sample_attribs["loopCrossfade"] = str(zone.loopCrossfade)
        if hasattr(zone, "loopMode") and zone.loopMode != "forward":
            sample_attribs["loopMode"] = zone.loopMode

    ET.SubElement(group_elem, "sample", sample_attribs)


def _write_midi_and_params(preset, root, control_name_map):
    """Write MIDI CC mapping and global parameter blocks."""
    # MIDI CC mapping
    midi_controls = [el for el in getattr(preset.ui, "elements", []) if getattr(el, "midi_cc", None) is not None]
    if midi_controls:
        midi_elem = ET.SubElement(root, "midi")
        cc_map = {}
        for el in midi_controls:
            cc_num = str(getattr(el, "midi_cc"))
            if cc_num not in cc_map:
                cc_elem = ET.SubElement(midi_elem, "cc", {"number": cc_num})
                cc_map[cc_num] = cc_elem
            position = str(getattr(preset.ui.elements, "index", lambda x: None)(el)) if hasattr(preset.ui.elements, "index") else "0"
            if position == "None":
                position = str(midi_controls.index(el))
            ET.SubElement(cc_map[cc_num], "binding", {
                "level": "ui",
                "type": "control",
                "parameter": "VALUE",
                "position": position,
                "translation": "linear",
                "translationOutputMin": "0",
                "translationOutputMax": "1",
            })

    # Global parameter blocks
    control_targets = {getattr(el, "target", None) for el in getattr(preset.ui, "elements", [])}
    if any(t in ("ENV_ATTACK", "ENV_DECAY", "ENV_SUSTAIN", "ENV_RELEASE") for t in control_targets):
        ET.SubElement(root, "ampeg", {"attack": "0.01", "decay": "0.2", "sustain": "1.0", "release": "0.3"})
    if any(t and t.startswith("REVERB_") for t in control_targets) or getattr(preset, "have_reverb", False):
        ET.SubElement(root, "reverb", {"wetLevel": "0.5", "roomSize": "0.8"})
    if any(t and t.startswith("CHORUS_") for t in control_targets) or getattr(preset, "have_chorus", False):
        ET.SubElement(root, "chorus", {"delay": "20", "depth": "0.3", "rate": "0.25"})
    if any(t and t.startswith("FILTER_") for t in control_targets) or getattr(preset, "have_tone", False):
        ET.SubElement(root, "filter", {"type": "lowpass", "cutoff": "20000", "resonance": "0.1"})
