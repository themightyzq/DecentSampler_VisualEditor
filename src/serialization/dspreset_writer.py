"""Export InstrumentPreset to .dspreset XML files.

Two modes:

* Preset opened from a file (``preset.source_root`` is set by the reader): the
  writer patches a copy of the parsed XML. An attribute is changed only when the
  model value differs from the value the reader saw, controls and groups the
  editor did not touch stay as they were, and every element or attribute the
  editor does not model is written back unchanged.
* Preset built in the editor: the XML is generated from the model.

Either way the file is written to a temporary file in the same folder, flushed
and fsynced, then moved over the target with ``os.replace``, so a failed write
never damages an existing preset.
"""
import copy
import filecmp
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from models.data_classes import SampleZone
from serialization.xml_common import (
    BOOL_FLAGS, patch_attrs, indent_tree, normalize_color, zone_attrs, lfo_attrs,
    binding_attrs, ui_root_attrs, ui_element_attrs, color_range_tuples,
    global_block_flags,
)

_XML_DECLARATION = b'<?xml version="1.0" encoding="UTF-8"?>\n'

# Root-level blocks the editor writes for effect-style controls.
_GLOBAL_BLOCKS = {
    "ampeg": {"attack": "0.01", "decay": "0.2", "sustain": "1.0", "release": "0.3"},
    "reverb": {"wetLevel": "0.5", "roomSize": "0.8"},
    "chorus": {"delay": "20", "depth": "0.3", "rate": "0.25"},
    "filter": {"type": "lowpass", "cutoff": "20000", "resonance": "0.1"},
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def write_dspreset(preset, path: str):
    """Write an InstrumentPreset to a .dspreset XML file (atomically)."""
    root = build_tree(preset, path)
    _atomic_write_bytes(path, _serialize(root))


def preset_fingerprint(preset) -> bytes:
    """Deterministic bytes describing everything the editor would save.

    Used to tell whether a preset changed since it was opened or saved. It
    touches no files: no sample copies, no existence checks, no validation.
    """
    root = build_tree(preset, "preset.dspreset", dry_run=True)
    mappings = [(m.path, m.lo, m.hi, m.root) for m in getattr(preset, "mappings", [])]
    return _serialize(root) + repr(mappings).encode("utf-8")


def build_tree(preset, path: str, dry_run: bool = False):
    """Build the XML tree for a preset. With dry_run, nothing touches the disk."""
    zones = preset.sample_manager.get_zones() if preset.sample_manager and preset.sample_manager.get_zones() else [
        SampleZone(m.path, m.root, m.lo, m.hi) for m in preset.mappings
    ]
    if not zones and not dry_run:
        raise Exception("Export aborted: At least one sample must be loaded.")

    exporter = _SampleExporter(preset, path, dry_run)
    if getattr(preset, "source_root", None) is not None and getattr(preset, "as_read", None) is not None:
        return _build_patched(preset, zones, exporter, dry_run)
    return _build_generated(preset, zones, exporter, dry_run)


# ---------------------------------------------------------------------------
# Atomic file output
# ---------------------------------------------------------------------------

def _serialize(root) -> bytes:
    indent_tree(root)
    return _XML_DECLARATION + ET.tostring(root, encoding="utf-8")


def _atomic_write_bytes(path, data: bytes):
    """Write data to path via a temp file in the same folder and os.replace."""
    path = os.path.abspath(path)
    folder = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(
        dir=folder, prefix="." + os.path.basename(path) + ".", suffix=".tmp")
    os.close(fd)
    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        try:
            shutil.copymode(path, tmp_path)  # keep the permissions of a file we replace
        except OSError:
            os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Sample files
# ---------------------------------------------------------------------------

def _same_file(a, b):
    try:
        return os.path.exists(a) and os.path.exists(b) and os.path.samefile(a, b)
    except OSError:
        return False


def _usable_destination(src, dest):
    """True if dest is free, is src itself, or already holds identical bytes."""
    if not os.path.exists(dest):
        return True
    if _same_file(src, dest):
        return True
    try:
        # Same size and modification time counts as identical (copy2 preserves the
        # time), so a repeat save does not read every sample again; otherwise the
        # bytes are compared.
        return filecmp.cmp(src, dest, shallow=True)
    except OSError:
        return False


def _copy_atomic(src, dest):
    """Copy src to dest through a temp file; never overwrites a different file.

    Does nothing if dest already holds the same file, so repeat saves do not copy
    the whole library again.
    """
    if os.path.exists(dest) and _usable_destination(src, dest):
        return
    folder = os.path.dirname(dest)
    os.makedirs(folder, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=folder, prefix="." + os.path.basename(dest) + ".", suffix=".tmp")
    os.close(fd)
    try:
        shutil.copy2(src, tmp_path)
        os.replace(tmp_path, dest)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


class _SampleExporter:
    """Decides the path attribute written for a sample and copies files as needed."""

    def __init__(self, preset, out_path, dry_run=False):
        self.dry_run = dry_run
        self.out_dir = os.path.dirname(os.path.abspath(out_path))
        self.samples_dir = os.path.join(self.out_dir, "samples")
        self.used = set()
        source_path = getattr(preset, "source_path", None)
        self.in_place = bool(source_path) and _same_file(os.path.dirname(source_path), self.out_dir)

    def path_attr(self, zone):
        orig = zone.path
        if self.dry_run:
            return orig

        # A sample read from the file and not changed keeps the path text it had.
        attr = getattr(zone, "source_path_attr", None)
        if attr is not None and zone.source_elem is not None and orig == zone.source_path:
            if self.in_place:
                return attr
            if attr and not os.path.isabs(attr):
                rel = os.path.normpath(attr)
                if not rel.startswith(os.pardir):
                    dest = os.path.join(self.out_dir, rel)
                    if _same_file(orig, dest):
                        return attr
                    if os.path.isfile(orig) and _usable_destination(orig, dest):
                        _copy_atomic(orig, dest)
                        return attr

        if not os.path.isfile(orig):
            raise Exception(f"Sample file not found: {orig}")

        base_filename = os.path.basename(orig)
        name, ext = os.path.splitext(base_filename)
        unique_filename = base_filename
        i = 1
        while unique_filename in self.used or not _usable_destination(
                orig, os.path.join(self.samples_dir, unique_filename)):
            unique_filename = f"{name}_{i}{ext}"
            i += 1
        self.used.add(unique_filename)
        _copy_atomic(orig, os.path.join(self.samples_dir, unique_filename))
        return "samples/" + unique_filename


# ---------------------------------------------------------------------------
# Shared element builders
# ---------------------------------------------------------------------------

def _ui_attribs_generated(preset):
    custom_labels = [el.label for el in getattr(preset.ui, "elements", [])]
    bg_color = normalize_color(getattr(preset, "bg_color", None)) or "FF222222"
    attribs = {
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
        attribs["bgImage"] = preset.bg_image
    return attribs


def _write_ui_controls(elements, tab_elem, used_names):
    """Write UI elements (controls, menus, labels, buttons, images) into a tab."""
    for el in elements:
        if getattr(el, "tag", None) == "keyboard":
            continue
        # Menu/option support
        if getattr(el, "tag", None) == "Menu" or getattr(el, "widget_type", None) == "Menu":
            _write_menu_element(el, tab_elem)
            continue

        tag = getattr(el, "tag", None)
        control_type = str(getattr(el, "widget_type", "") or "").lower()

        # Export label, button, image elements directly
        if control_type in ("label", "button", "image") or tag in ("label", "button", "image"):
            _write_simple_element(el, tab_elem)
            continue

        target = getattr(el, "target", None)
        if control_type not in ("knob", "slider", "control") or not target or not isinstance(target, str) or not target.strip():
            continue

        if getattr(el, "min_val", None) is None:
            el.min_val = 0
        if getattr(el, "max_val", None) is None:
            el.max_val = 1

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


def _write_keyboard(ui_elem, keyboard_el):
    keyboard_elem = ET.SubElement(ui_elem, "keyboard")
    for color_range in getattr(keyboard_el, "color_ranges", []):
        ET.SubElement(keyboard_elem, "color", {
            "loNote": str(color_range.lo_note),
            "hiNote": str(color_range.hi_note),
            "color": color_range.color,
            "pressedColor": color_range.pressed_color,
        })
    return keyboard_elem


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


def _write_simple_element(el, tab_elem):
    """Write a label, button, or image element."""
    tag = getattr(el, "tag", None) or str(getattr(el, "widget_type", "label")).lower()
    attribs = {
        "x": str(getattr(el, "x", 0)),
        "y": str(getattr(el, "y", 0)),
        "width": str(getattr(el, "width", 64)),
        "height": str(getattr(el, "height", 64)),
    }
    label = getattr(el, "label", None)
    if label:
        attribs["label"] = label
    skin = getattr(el, "skin", None)
    if skin:
        attribs["skin"] = skin
    ET.SubElement(tab_elem, tag, attribs)


def _write_lfo_modulators(preset, root):
    """Write <modulators> section."""
    if not preset.lfos:
        return
    modulators_elem = ET.SubElement(root, "modulators")
    for lfo in preset.lfos:
        lfo_elem = ET.SubElement(modulators_elem, "lfo", lfo_attrs(lfo))
        for route in preset.modulation_routes:
            if route.modulator_name == lfo.name:
                ET.SubElement(lfo_elem, "binding", binding_attrs(route))


def _effects_from_ui_bindings(preset, effects_elem, written_types):
    """Add <effect> entries implied by effect bindings on UI controls."""
    effect_controls = [el for el in getattr(preset.ui, "elements", []) if any(
        b.get("type") == "effect" for b in getattr(el, "bindings", []))]

    effect_param_map = {}
    for el in effect_controls:
        for binding in getattr(el, "bindings", []):
            if binding.get("type") == "effect":
                effect_type = binding.get("effectType")
                param = binding.get("parameter")
                value = getattr(el, "default", getattr(el, "min_val", 0))
                if effect_type and param and effect_type not in written_types:
                    if effect_type not in effect_param_map:
                        effect_param_map[effect_type] = {}
                    effect_param_map[effect_type][param] = str(value)

    for effect_type, params in effect_param_map.items():
        eff_params = {"type": effect_type}
        eff_params.update(params)
        ET.SubElement(effects_elem, "effect", eff_params)


def _write_effects_section(preset, root):
    """Write <effects> section."""
    from utils.effects_catalog import EFFECTS_CATALOG

    effects_elem = ET.SubElement(root, "effects")

    # Track which effect types have been written (to avoid duplicates)
    written_types = set()

    # First, write effects from preset.effects dict (loaded from XML)
    for catalog_name, params in getattr(preset, "effects", {}).items():
        meta = EFFECTS_CATALOG.get(catalog_name)
        if meta:
            effect_type = meta["type"]
            eff_params = {"type": effect_type}
            eff_params.update(params)
            ET.SubElement(effects_elem, "effect", eff_params)
            written_types.add(effect_type)

    # Then, write effects derived from UI element bindings (if not already written)
    _effects_from_ui_bindings(preset, effects_elem, written_types)


def _add_sample(zone, group_elem, exporter, reuse=None):
    """Add a <sample> for zone to group_elem; reuse a patched source element if given."""
    attr = exporter.path_attr(zone)
    source = getattr(zone, "source_elem", None)
    if reuse is not None and source is not None and id(source) in reuse:
        elem = reuse.pop(id(source))
        group_elem.append(elem)
        patch_attrs(elem, zone_attrs(zone), zone.source_attrs or {})
        if elem.get("path") != attr:
            elem.set("path", attr)
        return elem
    attribs = {"path": attr}
    attribs.update(zone_attrs(zone))
    return ET.SubElement(group_elem, "sample", attribs)


def _envelope_is_default(env):
    return (abs(env.attack - 0.01) < 1e-6 and abs(env.decay - 1.0) < 1e-6
            and abs(env.sustain - 1.0) < 1e-6 and abs(env.release - 0.43) < 1e-6)


def _fill_groups(preset, groups_elem, zones, exporter, reuse=None):
    """Write <group> children (with samples) into groups_elem from the model."""

    def _maybe_write_envelope(group_elem):
        env = getattr(preset, "envelope", None)
        if env is not None and not _envelope_is_default(env):
            ET.SubElement(group_elem, "envelope", {
                "attack": str(env.attack),
                "decay": str(env.decay),
                "sustain": str(env.sustain),
                "release": str(env.release),
            })

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
            _maybe_write_envelope(group_elem)
            for zone in group.samples:
                _add_sample(zone, group_elem, exporter, reuse)
    else:
        first_group = True
        for zone in zones:
            group_elem = ET.SubElement(groups_elem, "group", {"enabled": "true"})
            if first_group:
                _maybe_write_envelope(group_elem)
                first_group = False
            if preset.cut_all_by_all:
                group_elem.set("tags", "cutgroup0")
                group_elem.set("silencedByTags", "cutgroup0")
                group_elem.set("silencingMode", preset.silencing_mode)
            _add_sample(zone, group_elem, exporter, reuse)


def _add_midi_ccs(preset, root, midi_controls):
    """Write MIDI CC bindings for controls into the <midi> element."""
    midi_elem = root.find("midi")
    if midi_elem is None:
        midi_elem = ET.SubElement(root, "midi")
    cc_map = {}
    for cc_elem in midi_elem.findall("cc"):
        cc_map.setdefault(cc_elem.get("number"), cc_elem)
    for el in midi_controls:
        cc_num = str(getattr(el, "midi_cc"))
        if cc_num not in cc_map:
            cc_map[cc_num] = ET.SubElement(midi_elem, "cc", {"number": cc_num})
        try:
            position = str(preset.ui.elements.index(el))
        except (ValueError, AttributeError):
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


def _add_global_block(root, tag):
    if root.find(tag) is None:
        ET.SubElement(root, tag, dict(_GLOBAL_BLOCKS[tag]))


# ---------------------------------------------------------------------------
# Generated mode (preset built in the editor)
# ---------------------------------------------------------------------------

def _build_generated(preset, zones, exporter, dry_run):
    elements = getattr(preset.ui, "elements", [])
    if not dry_run:
        for el in elements:
            if str(getattr(el, "widget_type", "")).lower() in ("knob", "slider"):
                if getattr(el, "min_val", None) is None:
                    el.min_val = 0
                if getattr(el, "max_val", None) is None:
                    el.max_val = 1

    root = ET.Element("DecentSampler", {"minVersion": "1.0.2", "presetName": preset.name})

    ui_elem = ET.SubElement(root, "ui", _ui_attribs_generated(preset))
    tab_elem = ET.SubElement(ui_elem, "tab", {"name": "main"})
    _write_ui_controls(elements, tab_elem, set())
    keyboard_elements = [el for el in elements if getattr(el, "tag", None) == "keyboard"]
    if keyboard_elements:
        _write_keyboard(ui_elem, keyboard_elements[0])

    _write_lfo_modulators(preset, root)
    _write_effects_section(preset, root)
    groups_elem = ET.SubElement(root, "groups", {"volume": "-3dB"})
    _fill_groups(preset, groups_elem, zones, exporter)

    midi_controls = [el for el in elements if getattr(el, "midi_cc", None) is not None]
    if midi_controls:
        _add_midi_ccs(preset, root, midi_controls)
    flags = global_block_flags(preset)
    for tag in ("ampeg", "reverb", "chorus", "filter"):
        if flags[tag]:
            _add_global_block(root, tag)
    return root


# ---------------------------------------------------------------------------
# Patched mode (preset opened from a file)
# ---------------------------------------------------------------------------

def _insert_root_child(root, elem, before):
    """Insert elem before the first existing child whose tag is in `before`."""
    for index, child in enumerate(list(root)):
        if child.tag in before:
            root.insert(index, elem)
            return elem
    root.append(elem)
    return elem


def _build_patched(preset, zones, exporter, dry_run):
    src_root = preset.source_root
    as_read = preset.as_read
    root = copy.deepcopy(src_root)  # the preserved tree is never modified
    cmap = {id(o): c for o, c in zip(src_root.iter(), root.iter())}

    def live(source_elem):
        return cmap.get(id(source_elem)) if source_elem is not None else None

    def parents_of():
        return {child: parent for parent in root.iter() for child in parent}

    elements = list(getattr(preset.ui, "elements", []))
    groups_custom = any(g.samples for g in (getattr(preset, "sample_groups", None) or []))

    # Everything the model still holds; bound source elements outside it are removed.
    present = {id(z) for z in zones}
    present.update(id(el) for el in elements)
    present.update(id(l) for l in preset.lfos)
    present.update(id(r) for r in preset.modulation_routes)
    if groups_custom:
        for g in preset.sample_groups:
            present.update(id(z) for z in g.samples)
    parents = parents_of()
    for source_elem, obj in preset.source_bound:
        if id(obj) not in present:
            elem = live(source_elem)
            if elem is not None and elem in parents:
                parents[elem].remove(elem)

    # Root attributes
    if preset.name != as_read["name"]:
        root.set("presetName", preset.name)

    _patch_ui(preset, root, src_root, cmap, elements, as_read)
    _patch_modulators(preset, root, src_root, cmap, parents_of())
    _patch_effects(preset, root, src_root, cmap, as_read)
    _patch_groups(preset, root, src_root, cmap, zones, exporter, groups_custom, as_read)

    # MIDI mappings for controls added in this session; global blocks newly implied.
    new_midi = [el for el in elements
                if getattr(el, "source_elem", None) is None and getattr(el, "midi_cc", None) is not None]
    if new_midi:
        _add_midi_ccs(preset, root, new_midi)
    flags = global_block_flags(preset)
    for tag in ("ampeg", "reverb", "chorus", "filter"):
        if flags[tag] and not as_read["global_blocks"][tag]:
            _add_global_block(root, tag)
    return root


def _patch_ui(preset, root, src_root, cmap, elements, as_read):
    ui_src = src_root.find("ui")
    ui_elem = cmap.get(id(ui_src)) if ui_src is not None else None
    current = ui_root_attrs(preset)
    new_controls = [el for el in elements
                    if getattr(el, "source_elem", None) is None and getattr(el, "tag", None) != "keyboard"]
    new_keyboard = [el for el in elements
                    if getattr(el, "source_elem", None) is None and getattr(el, "tag", None) == "keyboard"]

    if ui_elem is None:
        if current == as_read["ui_attrs"] and not new_controls and not new_keyboard:
            return
        ui_elem = ET.Element("ui", current)
        root.insert(0, ui_elem)
    else:
        patch_attrs(ui_elem, current, as_read["ui_attrs"])

    # Existing controls: geometry (and label, where the element has one) only.
    for el in elements:
        elem = cmap.get(id(el.source_elem)) if getattr(el, "source_elem", None) is not None else None
        if elem is None:
            continue
        if getattr(el, "tag", None) == "keyboard":
            if color_range_tuples(el) != el.source_color_ranges:
                for color in elem.findall("color"):
                    elem.remove(color)
                for lo, hi, color, pressed in color_range_tuples(el):
                    ET.SubElement(elem, "color", {
                        "loNote": str(lo), "hiNote": str(hi),
                        "color": color, "pressedColor": pressed})
            continue
        now = ui_element_attrs(el)
        base = el.source_attrs or {}
        for key in ("x", "y", "width", "height", "label"):
            if now[key] != base.get(key) and (key != "label" or "label" in elem.attrib):
                elem.set(key, now[key])

    if new_controls:
        tab_elem = ui_elem.find("tab")
        if tab_elem is None:
            tab_elem = ET.Element("tab", {"name": "main"})
            keyboard = ui_elem.find("keyboard")
            if keyboard is not None:
                ui_elem.insert(list(ui_elem).index(keyboard), tab_elem)
            else:
                ui_elem.append(tab_elem)
        used_names = {child.get("label") or child.get("parameterName")
                      for child in tab_elem if isinstance(child.tag, str)}
        _write_ui_controls(new_controls, tab_elem, used_names)
    if new_keyboard and ui_elem.find("keyboard") is None:
        _write_keyboard(ui_elem, new_keyboard[0])


def _patch_modulators(preset, root, src_root, cmap, parents):
    mod_src = src_root.find("modulators")
    mod_elem = cmap.get(id(mod_src)) if mod_src is not None else None

    lfo_elems = {}   # first LFO element per name, where routes attach
    for lfo in preset.lfos:
        source = getattr(lfo, "source_elem", None)
        elem = cmap.get(id(source)) if source is not None else None
        if elem is not None:
            patch_attrs(elem, lfo_attrs(lfo), lfo.source_attrs or {})
        else:
            if mod_elem is None:
                mod_elem = _insert_root_child(root, ET.Element("modulators"), ("effects", "groups", "midi"))
            elem = ET.SubElement(mod_elem, "lfo", lfo_attrs(lfo))
        lfo_elems.setdefault(lfo.name, elem)
    same_name = {}
    for lfo in preset.lfos:
        elem = cmap.get(id(lfo.source_elem)) if getattr(lfo, "source_elem", None) is not None else None
        if elem is not None:
            same_name.setdefault(lfo.name, set()).add(elem)

    for route in preset.modulation_routes:
        target = lfo_elems.get(route.modulator_name)
        if target is None:
            continue
        source = getattr(route, "source_elem", None)
        binding = cmap.get(id(source)) if source is not None else None
        if binding is not None and binding in parents:
            patch_attrs(binding, binding_attrs(route), route.source_attrs or {})
            holder = parents[binding]
            if holder is not target and holder not in same_name.get(route.modulator_name, ()):
                holder.remove(binding)
                target.append(binding)
        else:
            ET.SubElement(target, "binding", binding_attrs(route))


def _patch_effects(preset, root, src_root, cmap, as_read):
    from utils.effects_catalog import EFFECTS_CATALOG

    fx_src = src_root.find("effects")
    fx_elem = cmap.get(id(fx_src)) if fx_src is not None else None
    base, now = as_read["effects"], getattr(preset, "effects", {})

    def ensure():
        nonlocal fx_elem
        if fx_elem is None:
            fx_elem = _insert_root_child(root, ET.Element("effects"), ("groups", "midi"))
        return fx_elem

    def first_of_type(effect_type):
        if fx_elem is None:
            return None
        for child in fx_elem.findall("effect"):
            if child.get("type") == effect_type:
                return child
        return None

    if now != base:
        for name in base:
            if name not in now and name in EFFECTS_CATALOG:
                elem = first_of_type(EFFECTS_CATALOG[name]["type"])
                if elem is not None:
                    fx_elem.remove(elem)
        for name, params in now.items():
            meta = EFFECTS_CATALOG.get(name)
            if not meta:
                continue
            elem = first_of_type(meta["type"]) if name in base else None
            if elem is not None:
                patch_attrs(elem, dict(params), dict(base[name]))
            else:
                attribs = {"type": meta["type"]}
                attribs.update(params)
                ET.SubElement(ensure(), "effect", attribs)

    # Effects implied by bindings on controls added in this session.
    written = {c.get("type") for c in fx_elem.findall("effect")} if fx_elem is not None else set()
    holder = ET.Element("effects")
    _effects_from_ui_bindings(preset, holder, written)
    for child in list(holder):
        ensure().append(child)


def _patch_groups(preset, root, src_root, cmap, zones, exporter, groups_custom, as_read):
    groups_src = src_root.find("groups")
    groups_elem = cmap.get(id(groups_src)) if groups_src is not None else None

    def ensure_groups():
        nonlocal groups_elem
        if groups_elem is None:
            groups_elem = _insert_root_child(root, ET.Element("groups"), ("midi",))
        return groups_elem

    if groups_custom:
        ensure_groups()
        # The user rebuilt the grouping in the Groups tab: lay the groups out from the
        # model, but keep the <groups> attributes and each sample's original element.
        reuse = {}
        for g in preset.sample_groups:
            for zone in g.samples:
                source = getattr(zone, "source_elem", None)
                if source is not None and id(source) in cmap:
                    reuse[id(source)] = cmap[id(source)]
        for child in list(groups_elem):
            groups_elem.remove(child)
        _fill_groups(preset, groups_elem, zones, exporter, reuse)
        return

    # Envelope edits go to the first group's <envelope>.
    env = getattr(preset, "envelope", None)
    if env is not None and (env.attack, env.decay, env.sustain, env.release) != as_read["envelope"]:
        first_group = ensure_groups().find("group")
        if first_group is None:
            first_group = ET.SubElement(groups_elem, "group", {"enabled": "true"})
        env_elem = first_group.find("envelope")
        if env_elem is None:
            env_elem = ET.SubElement(first_group, "envelope")
        env_elem.set("attack", str(env.attack))
        env_elem.set("decay", str(env.decay))
        env_elem.set("sustain", str(env.sustain))
        env_elem.set("release", str(env.release))

    for zone in zones:
        source = getattr(zone, "source_elem", None)
        elem = cmap.get(id(source)) if source is not None else None
        if elem is not None:
            patch_attrs(elem, zone_attrs(zone), zone.source_attrs or {})
            attr = exporter.path_attr(zone)
            if elem.get("path") != attr:
                elem.set("path", attr)
        else:
            group_elems = ensure_groups().findall("group")
            group_elem = group_elems[-1] if group_elems else ET.SubElement(
                groups_elem, "group", {"enabled": "true"})
            _add_sample(zone, group_elem, exporter)
