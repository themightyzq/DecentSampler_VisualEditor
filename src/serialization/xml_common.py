"""Helpers shared by the .dspreset reader and writer.

The reader keeps the XML tree it parsed and the attribute values the editor
models at that moment. The writer patches a copy of that tree, touching an
attribute only when the model value differs from the value read. Both sides
must therefore compute "the attributes the model controls" the same way, which
is why those functions live here.
"""
import xml.etree.ElementTree as ET

BOOL_FLAGS = (
    ("haveReverb", "have_reverb"),
    ("haveTone", "have_tone"),
    ("haveChorus", "have_chorus"),
    ("haveMidicc1", "have_midicc1"),
    ("noAttack", "no_attack"),
    ("noDecay", "no_decay"),
)


def is_element(node):
    """True for real elements; False for comments and processing instructions."""
    return isinstance(node.tag, str)


def parse_tree(path):
    """Parse an XML file keeping comments (Python 3.8+), return the ElementTree."""
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    except TypeError:  # Python 3.7: comments are dropped
        parser = ET.XMLParser()
    return ET.parse(path, parser=parser)


def to_number(raw, cast, default):
    """Lenient numeric parse: a value the editor cannot read becomes the default.

    The original attribute text stays in the preserved XML tree, so an
    unreadable value is never rewritten unless the user edits that field.
    """
    if raw is None:
        return default
    try:
        return cast(raw)
    except (TypeError, ValueError):
        try:
            return cast(float(raw))
        except (TypeError, ValueError, OverflowError):
            return default


def normalize_color(raw):
    """Return an 8-digit AARRGGBB string for a colour, or None if unusable."""
    if not raw:
        return None
    text = str(raw).strip()
    if text.startswith("#"):
        text = text[1:]
    if len(text) == 6:
        text = "FF" + text
    if len(text) != 8:
        return None
    try:
        int(text, 16)
    except ValueError:
        return None
    return text.upper()


def zone_attrs(zone):
    """Attributes of a <sample> the model controls, defaults omitted. Excludes path."""
    attrs = {
        "rootNote": str(zone.rootNote),
        "loNote": str(zone.loNote),
        "hiNote": str(zone.hiNote),
    }
    if tuple(zone.velocityRange) != (0, 127):
        attrs["velocityRange"] = f"{zone.velocityRange[0]},{zone.velocityRange[1]}"
    if zone.tags:
        attrs["tags"] = ",".join(zone.tags)
    if zone.seqMode != "round_robin":
        attrs["seqMode"] = zone.seqMode
    if zone.seqPosition != 1:
        attrs["seqPosition"] = str(zone.seqPosition)
    if zone.volume != 0.0:
        attrs["volume"] = str(zone.volume)
    if zone.pan != 0.0:
        attrs["pan"] = str(zone.pan)
    if zone.tune != 0.0:
        attrs["tune"] = str(zone.tune)
    if zone.start != 0:
        attrs["start"] = str(zone.start)
    if zone.end is not None:
        attrs["end"] = str(zone.end)
    if zone.loopEnabled:
        attrs["loopEnabled"] = "true"
        if zone.loopStart is not None:
            attrs["loopStart"] = str(zone.loopStart)
        if zone.loopEnd is not None:
            attrs["loopEnd"] = str(zone.loopEnd)
        if zone.loopCrossfade != 0.0:
            attrs["loopCrossfade"] = str(zone.loopCrossfade)
        if zone.loopMode != "forward":
            attrs["loopMode"] = zone.loopMode
    return attrs


def lfo_attrs(lfo):
    return {
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


def binding_attrs(route):
    attrs = {
        "type": route.target.target_type,
        "parameter": route.target.parameter,
        "level": route.target.level,
        "position": str(route.target.position),
        "amount": str(route.amount),
    }
    if route.target.group_index is not None:
        attrs["groupIndex"] = str(route.target.group_index)
    if route.target.effect_index is not None:
        attrs["effectIndex"] = str(route.target.effect_index)
    if route.invert:
        attrs["invert"] = "true"
    return attrs


def ui_root_attrs(preset):
    """Attributes of <ui> the model controls (patch mode; no label heuristics)."""
    attrs = {
        "width": str(preset.ui_width),
        "height": str(preset.ui_height),
        "layoutMode": str(preset.layout_mode),
        "bgMode": str(preset.bg_mode),
    }
    if preset.bg_image:
        attrs["bgImage"] = str(preset.bg_image)
    color = normalize_color(getattr(preset, "bg_color", None))
    if color:
        attrs["bgColor"] = color
    for xml_name, field in BOOL_FLAGS:
        attrs[xml_name] = "true" if getattr(preset, field, False) else "false"
    return attrs


def ui_element_attrs(el):
    """Geometry (and label, where the XML element has one) of a UI control."""
    return {
        "x": str(el.x),
        "y": str(el.y),
        "width": str(el.width),
        "height": str(el.height),
        "label": str(el.label),
    }


def color_range_tuples(el):
    return [
        (r.lo_note, r.hi_note, r.color, r.pressed_color)
        for r in (getattr(el, "color_ranges", None) or [])
    ]


def global_block_flags(preset):
    """Whether the writer's heuristics would emit each root-level global block."""
    targets = {getattr(el, "target", None) for el in getattr(preset.ui, "elements", [])}
    return {
        "ampeg": any(t in ("ENV_ATTACK", "ENV_DECAY", "ENV_SUSTAIN", "ENV_RELEASE")
                     for t in targets),
        "reverb": any(isinstance(t, str) and t.startswith("REVERB_") for t in targets)
                  or bool(getattr(preset, "have_reverb", False)),
        "chorus": any(isinstance(t, str) and t.startswith("CHORUS_") for t in targets)
                  or bool(getattr(preset, "have_chorus", False)),
        "filter": any(isinstance(t, str) and t.startswith("FILTER_") for t in targets)
                  or bool(getattr(preset, "have_tone", False)),
    }


def patch_attrs(elem, current, baseline):
    """Set attributes whose value differs from the value read; drop ones removed."""
    for key, value in current.items():
        if baseline.get(key) != value:
            elem.set(key, value)
    for key in baseline:
        if key not in current and key in elem.attrib:
            del elem.attrib[key]


def indent_tree(elem, level=0, unit="  "):
    """Pretty-print in place without disturbing real text content.

    Whitespace-only text and tail are replaced; text that carries data is kept.
    """
    children = list(elem)
    pad = "\n" + level * unit
    child_pad = "\n" + (level + 1) * unit
    if children:
        if elem.text is None or not elem.text.strip():
            elem.text = child_pad
        for index, child in enumerate(children):
            indent_tree(child, level + 1, unit)
            if child.tail is None or not child.tail.strip():
                child.tail = child_pad if index < len(children) - 1 else pad
