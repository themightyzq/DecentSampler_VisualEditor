import xml.etree.ElementTree as ET
from typing import List, Optional
from utils.effects_catalog import EFFECTS_CATALOG

class SampleZone:
    def __init__(self, path: str, rootNote: int, loNote: int, hiNote: int, velocityRange=(0, 127),
                 seqMode="round_robin", seqPosition=1, volume=0.0, pan=0.0, tune=0.0,
                 start=0, end=None, loopEnabled=False, loopStart=None, loopEnd=None, 
                 loopCrossfade=0.0, loopMode="forward", tags=None):
        self.path = path
        self.rootNote = rootNote
        self.loNote = loNote
        self.hiNote = hiNote
        self.velocityRange = velocityRange
        
        # Advanced sampling attributes
        self.seqMode = seqMode  # "round_robin", "random", "true_random", "always"
        self.seqPosition = seqPosition  # Position in round-robin sequence
        self.volume = volume  # Volume offset in dB
        self.pan = pan  # Pan position (-1.0 to 1.0)
        self.tune = tune  # Tune offset in cents
        
        # Sample playback range
        self.start = start  # Start sample offset
        self.end = end  # End sample offset (None = end of file)
        
        # Loop settings
        self.loopEnabled = loopEnabled
        self.loopStart = loopStart  # Loop start point
        self.loopEnd = loopEnd  # Loop end point  
        self.loopCrossfade = loopCrossfade  # Crossfade amount in seconds
        self.loopMode = loopMode  # "forward", "backward", "bidirectional"
        
        # Sample tags for blending and organization
        self.tags = tags or []  # List of tags for this sample

    def __repr__(self):
        return (
            f"SampleZone(path={self.path!r}, rootNote={self.rootNote}, "
            f"loNote={self.loNote}, hiNote={self.hiNote}, velocityRange={self.velocityRange}, "
            f"seqMode={self.seqMode}, seqPosition={self.seqPosition})"
        )

class SampleManager:
    def __init__(self):
        self.zones = []

    def add_zone(self, path, rootNote, loNote, hiNote, velocityRange=(0, 127)):
        zone = SampleZone(path, rootNote, loNote, hiNote, velocityRange)
        self.zones.append(zone)

    def remove_zone(self, path):
        self.zones = [z for z in self.zones if z.path != path]

    def get_zones(self):
        return self.zones

    def clear(self):
        self.zones = []

    def update_zone(self, path, **kwargs):
        for z in self.zones:
            if z.path == path:
                for k, v in kwargs.items():
                    if hasattr(z, k):
                        setattr(z, k, v)
                break

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

class LFO:
    def __init__(self, name: str, frequency: float = 1.0, waveform: str = "sine", 
                 amplitude: float = 1.0, offset: float = 0.0, phase: float = 0.0,
                 sync: str = "free", sync_length: str = "1", retrigger: bool = False):
        self.name = name
        self.frequency = frequency
        self.waveform = waveform  # sine, triangle, sawtooth, square, s&h, envelope_follower
        self.amplitude = amplitude
        self.offset = offset
        self.phase = phase
        self.sync = sync  # free, tempo
        self.sync_length = sync_length  # 1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 4, 8, 16
        self.retrigger = retrigger

class ModulatorTarget:
    def __init__(self, target_type: str, parameter: str, level: str = "instrument", 
                 position: int = 0, group_index: int = None, effect_index: int = None):
        self.target_type = target_type  # amp, effect, general, etc.
        self.parameter = parameter      # ENV_ATTACK, FX_MIX, etc.
        self.level = level             # instrument, group, tag
        self.position = position       # position for instrument level
        self.group_index = group_index # for group level
        self.effect_index = effect_index # for effect targeting

class ModulationRoute:
    def __init__(self, modulator_name: str, target: ModulatorTarget, 
                 amount: float = 1.0, invert: bool = False):
        self.modulator_name = modulator_name
        self.target = target
        self.amount = amount
        self.invert = invert

class UIElement:
    def __init__(self, x, y, width, height, label, skin=None, tag=None, widget_type=None, target=None, min_val=None, max_val=None, bindings=None, options=None, midi_cc=None, orientation=None, color_ranges=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.skin = skin  # path to skin image or None
        self.tag = tag
        self.widget_type = widget_type
        self.target = target  # DecentSampler parameter name
        self.min_val = min_val
        self.max_val = max_val
        self.bindings = bindings if bindings is not None else []  # List of binding dicts
        self.options = options if options is not None else []     # For menu: list of option objects
        self.midi_cc = midi_cc
        self.orientation = orientation
        self.color_ranges = color_ranges if color_ranges is not None else []  # For keyboard widget

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
        advanced_mode: bool = False,     # New: simple/advanced toggle
        sample_manager: Optional[SampleManager] = None,
        lfos: Optional[List[LFO]] = None,
        modulation_routes: Optional[List[ModulationRoute]] = None,
        sample_groups: Optional[List] = None
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
        self.effects = effects if effects is not None else {}  # {effect_name: {param: value, ...}}
        self.advanced_mode = advanced_mode
        self.lfos = lfos if lfos is not None else []
        self.modulation_routes = modulation_routes if modulation_routes is not None else []
        self.sample_groups = sample_groups if sample_groups is not None else []

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
        keyboard_color_ranges = []
        if ui_elem is not None:
            # Parse keyboard color ranges
            keyboard_elem = ui_elem.find("keyboard")
            if keyboard_elem is not None:
                # Define KeyboardColorRange here to avoid circular imports
                class KeyboardColorRange:
                    def __init__(self, lo_note=0, hi_note=127, color="FF444444", pressed_color="FF888888"):
                        self.lo_note = lo_note
                        self.hi_note = hi_note
                        self.color = color
                        self.pressed_color = pressed_color
                        
                for color_elem in keyboard_elem.findall("color"):
                    lo_note = int(color_elem.attrib.get("loNote", 0))
                    hi_note = int(color_elem.attrib.get("hiNote", 127))
                    color = color_elem.attrib.get("color", "FF444444")
                    pressed_color = color_elem.attrib.get("pressedColor", "FF888888")
                    keyboard_color_ranges.append(KeyboardColorRange(lo_note, hi_note, color, pressed_color))
                
                # Add keyboard as UI element
                ui_elements.append(UIElement(
                    0, 0, 812, 60, "Keyboard", None, "keyboard", "keyboard", 
                    color_ranges=keyboard_color_ranges
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
                    widget_type = el.attrib.get("widgetType", None)
                    ui_elements.append(UIElement(x, y, w, h, label, skin, tag, widget_type))
        mappings = []
        envelope = GroupEnvelope()
        lfos = []
        modulation_routes = []
        
        # Load modulators
        modulators_elem = root.find(".//modulators")
        if modulators_elem is not None:
            for lfo_elem in modulators_elem.findall("lfo"):
                lfo_name = lfo_elem.attrib.get("name", "LFO")
                frequency = float(lfo_elem.attrib.get("frequency", 1.0))
                waveform = lfo_elem.attrib.get("waveform", "sine")
                amplitude = float(lfo_elem.attrib.get("amplitude", 1.0))
                offset = float(lfo_elem.attrib.get("offset", 0.0))
                phase = float(lfo_elem.attrib.get("phase", 0.0))
                sync = lfo_elem.attrib.get("sync", "free")
                sync_length = lfo_elem.attrib.get("syncLength", "1")
                retrigger = lfo_elem.attrib.get("retrigger", "false").lower() == "true"
                
                lfo = LFO(lfo_name, frequency, waveform, amplitude, offset, phase, sync, sync_length, retrigger)
                lfos.append(lfo)
                
                # Load modulation routes for this LFO
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
                    
                    # Parse velocity range if present
                    velocity_range = (0, 127)
                    if "velocityRange" in sample.attrib:
                        vel_str = sample.attrib["velocityRange"]
                        if "," in vel_str:
                            vel_low, vel_high = map(int, vel_str.split(","))
                            velocity_range = (vel_low, vel_high)
                    
                    # Parse advanced attributes
                    seq_mode = sample.attrib.get("seqMode", "round_robin")
                    seq_position = int(sample.attrib.get("seqPosition", 1))
                    volume = float(sample.attrib.get("volume", 0.0))
                    pan = float(sample.attrib.get("pan", 0.0))
                    tune = float(sample.attrib.get("tune", 0.0))
                    start = int(sample.attrib.get("start", 0))
                    end = sample.attrib.get("end")
                    if end is not None:
                        end = int(end)
                    
                    # Parse loop attributes
                    loop_enabled = sample.attrib.get("loopEnabled", "false").lower() == "true"
                    loop_start = sample.attrib.get("loopStart")
                    loop_end = sample.attrib.get("loopEnd")
                    loop_crossfade = float(sample.attrib.get("loopCrossfade", 0.0))
                    loop_mode = sample.attrib.get("loopMode", "forward")
                    
                    if loop_start is not None:
                        loop_start = int(loop_start)
                    if loop_end is not None:
                        loop_end = int(loop_end)
                    
                    # Create enhanced sample zone
                    zone = SampleZone(
                        sample_path, root_note, lo, hi, velocity_range,
                        seq_mode, seq_position, volume, pan, tune,
                        start, end, loop_enabled, loop_start, loop_end,
                        loop_crossfade, loop_mode
                    )
                    
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
            effects=effects, lfos=lfos, modulation_routes=modulation_routes
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
        # --- VALIDATION ---
        # 1. At least one sample loaded
        zones = self.sample_manager.get_zones() if self.sample_manager and self.sample_manager.get_zones() else [
            SampleZone(m.path, m.root, m.lo, m.hi) for m in self.mappings
        ]
        if not zones:
            raise Exception("Export aborted: At least one sample must be loaded.")

        # 2. All controls have required attributes and assigned targets
        controls = [el for el in getattr(self.ui, "elements", []) if str(getattr(el, "widget_type", "Knob")).lower() in ("knob", "slider")]
        if not controls:
            raise Exception("Export aborted: At least one UI control (knob or slider) is required.")
        for el in controls:
            label = getattr(el, "label", None)
            min_val = getattr(el, "min_val", None)
            max_val = getattr(el, "max_val", None)
            target = getattr(el, "target", None)
            # Default min/max if missing
            if min_val is None:
                min_val = 0
                el.min_val = 0
            if max_val is None:
                max_val = 1
                el.max_val = 1
            if not (label and isinstance(label, str) and label.strip()):
                raise Exception("Export aborted: All controls must have a non-empty label.")
            if min_val is None or max_val is None:
                raise Exception(f"Export aborted: Control '{label}' is missing min or max value.")
            if not (target and isinstance(target, str) and target.strip()):
                raise Exception(f"Export aborted: Control '{label}' is missing a target parameter.")

        # 3. Required XML sections will be present and populated
        if not zones:
            raise Exception("Export aborted: <groups> section would be empty.")
        if not controls:
            raise Exception("Export aborted: <ui> section would be empty.")
        if not any(getattr(el, "target", None) for el in controls):
            raise Exception("Export aborted: <modulators> section would be empty.")

        # 4. Validate modulator mapping and DSP blocks
        # Build the set of controls to be exported (with valid target)
        export_controls = [
            el for el in controls
            if getattr(el, "target", None) and isinstance(getattr(el, "target", None), str) and getattr(el, "target", "").strip()
        ]
        # Simulate label assignment logic to get unique names
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
        # Ensure 1:1 mapping between exported controls and modulators
        if len(control_name_map) != len(export_controls):
            raise Exception("Export aborted: Mismatch between exported controls and modulators.")
        # Validate required DSP blocks
        control_targets = {getattr(el, "target", None) for el in export_controls}
        missing_blocks = []
        if any(t in ("ENV_ATTACK", "ENV_DECAY", "ENV_SUSTAIN", "ENV_RELEASE") for t in control_targets):
            # ampeg must be present
            pass  # will be added below
        if any(t and t.startswith("REVERB_") for t in control_targets) or getattr(self, "have_reverb", False):
            pass  # reverb will be added
        if any(t and t.startswith("CHORUS_") for t in control_targets) or getattr(self, "have_chorus", False):
            pass  # chorus will be added
        if any(t and t.startswith("FILTER_") for t in control_targets) or getattr(self, "have_tone", False):
            pass  # filter will be added
        # No missing blocks if logic below is correct

        # --- EXPORT LOGIC ---
        root = ET.Element("DecentSampler", {"minVersion": "1.0.2", "presetName": self.name})
        custom_labels = [el.label for el in getattr(self.ui, "elements", [])]
        # DecentSampler requires bgColor (8-digit ARGB hex) on <ui>
        bg_color = getattr(self, "bg_color", None)
        if not bg_color or len(bg_color) not in (8, 9):  # Accepts #AARRGGBB or AARRGGBB
            bg_color = "FF222222"  # fallback: opaque dark gray
        if bg_color.startswith("#"):
            bg_color = bg_color[1:]
        ui_attribs = {
            "width": str(self.ui_width),
            "height": str(self.ui_height),
            "bgColor": bg_color,
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
        # Write <groups> first (already done above)
        # Write <ui> section with controls inside a <tab> (DecentSampler expects this)
        ui_elem = ET.SubElement(root, "ui", ui_attribs)
        tab_elem = ET.SubElement(ui_elem, "tab", {"name": "main"})
        used_names = set()
        control_name_map = {}
        for el in getattr(self.ui, "elements", []):
            # Menu/option support
            if getattr(el, "tag", None) == "Menu" or getattr(el, "widget_type", None) == "Menu":
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
            control_name_map[el] = name
            min_val = getattr(el, "min_val", None)
            max_val = getattr(el, "max_val", None)
            if min_val is None:
                min_val = 0
            if max_val is None:
                max_val = 1
            value = getattr(el, "default", min_val)
            style = getattr(el, "style", None)
            orientation = getattr(el, "orientation", None)
            text_color = getattr(el, "textColor", "FF000000")
            text_size = getattr(el, "textSize", "12")
            track_fg = getattr(el, "trackForegroundColor", None)
            track_bg = getattr(el, "trackBackgroundColor", None)
            show_label = getattr(el, "showLabel", None)
            default_value = getattr(el, "default", None)
            knob_attribs = {
                "x": str(getattr(el, "x", 0)),
                "y": str(getattr(el, "y", 0)),
                "width": str(getattr(el, "width", 64)),
                "height": str(getattr(el, "height", 64)),
                "label": name,
                "type": "float",
                "minValue": str(min_val),
                "maxValue": str(max_val),
                "value": str(value),
                "textColor": text_color,
                "textSize": text_size,
            }
            if style:
                knob_attribs["style"] = style
            if orientation:
                knob_attribs["orientation"] = orientation
            if track_fg:
                knob_attribs["trackForegroundColor"] = track_fg
            if track_bg:
                knob_attribs["trackBackgroundColor"] = track_bg
            if show_label is not None:
                knob_attribs["showLabel"] = str(show_label).lower()
            if default_value is not None:
                knob_attribs["defaultValue"] = str(default_value)
            control_attribs = {
                "x": str(getattr(el, "x", 0)),
                "y": str(getattr(el, "y", 0)),
                "width": str(getattr(el, "width", 64)),
                "height": str(getattr(el, "height", 64)),
                "parameterName": name,
                "type": "float",
                "minValue": str(min_val),
                "maxValue": str(max_val),
                "value": str(value),
                "textColor": text_color,
                "textSize": text_size,
            }
            if style:
                control_attribs["style"] = style
            if orientation:
                control_attribs["orientation"] = orientation
            if track_fg:
                control_attribs["trackForegroundColor"] = track_fg
            if track_bg:
                control_attribs["trackBackgroundColor"] = track_bg
            if show_label is not None:
                control_attribs["showLabel"] = str(show_label).lower()
            if default_value is not None:
                control_attribs["defaultValue"] = str(default_value)
            # Write all bindings for this control
            if str(getattr(el, "widget_type", "Knob")).lower() == "slider":
                # Export as <control> with style
                style = "linear_vertical" if getattr(el, "orientation", None) == "vertical" else "linear_horizontal"
                control_attribs["style"] = style
                control_elem = ET.SubElement(tab_elem, "control", control_attribs)
                for binding in getattr(el, "bindings", []):
                    ET.SubElement(control_elem, "binding", {k: str(v) for k, v in binding.items() if v is not None})
            else:
                # Export as <labeled-knob>
                knob_elem = ET.SubElement(tab_elem, "labeled-knob", knob_attribs)
                for binding in getattr(el, "bindings", []):
                    ET.SubElement(knob_elem, "binding", {k: str(v) for k, v in binding.items() if v is not None})
        
        # Add keyboard widget if present
        keyboard_elements = [el for el in getattr(self.ui, "elements", []) if getattr(el, "tag", None) == "keyboard"]
        if keyboard_elements:
            keyboard_elem = ET.SubElement(ui_elem, "keyboard")
            keyboard_config = keyboard_elements[0]
            
            # Add color ranges
            for color_range in getattr(keyboard_config, "color_ranges", []):
                color_attribs = {
                    "loNote": str(color_range.lo_note),
                    "hiNote": str(color_range.hi_note),
                    "color": color_range.color,
                    "pressedColor": color_range.pressed_color
                }
                ET.SubElement(keyboard_elem, "color", color_attribs)
        # Write <modulators> section as direct child of <DecentSampler>
        if self.lfos:
            modulators_elem = ET.SubElement(root, "modulators")
            for lfo in self.lfos:
                lfo_attribs = {
                    "name": lfo.name,
                    "frequency": str(lfo.frequency),
                    "waveform": lfo.waveform,
                    "amplitude": str(lfo.amplitude),
                    "offset": str(lfo.offset),
                    "phase": str(lfo.phase),
                    "sync": lfo.sync,
                    "syncLength": lfo.sync_length,
                    "retrigger": str(lfo.retrigger).lower()
                }
                lfo_elem = ET.SubElement(modulators_elem, "lfo", lfo_attribs)
                
                # Add modulation routes for this LFO
                lfo_routes = [route for route in self.modulation_routes if route.modulator_name == lfo.name]
                for route in lfo_routes:
                    binding_attribs = {
                        "type": route.target.target_type,
                        "parameter": route.target.parameter,
                        "level": route.target.level,
                        "position": str(route.target.position),
                        "amount": str(route.amount)
                    }
                    if route.target.group_index is not None:
                        binding_attribs["groupIndex"] = str(route.target.group_index)
                    if route.target.effect_index is not None:
                        binding_attribs["effectIndex"] = str(route.target.effect_index)
                    if route.invert:
                        binding_attribs["invert"] = "true"
                    
                    ET.SubElement(lfo_elem, "binding", binding_attribs)
        # Write <effects> section with all effects referenced by UI controls
        effects_elem = ET.SubElement(root, "effects")
        # Collect all effect controls and their parameters
        effect_controls = [el for el in getattr(self.ui, "elements", []) if any(
            b.get("type") == "effect" for b in getattr(el, "bindings", []))]
        # Map: {effect_type: {param: value}}
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
        # Write each effect with its parameters
        for effect_type, params in effect_param_map.items():
            eff_params = {"type": effect_type}
            eff_params.update(params)
            ET.SubElement(effects_elem, "effect", eff_params)
        # Do NOT write <parameter> elements at the top level (not supported by DecentSampler)

        # Groups and sample mapping
        # Remove any previous/legacy <groups> writing above this point!
        # Only write the correct <groups> and <group> section with <sample> elements
        groups_elem = ET.SubElement(root, "groups", {
            "volume": "-3dB"
        })
        import os
        import shutil
        samples_dir = os.path.join(os.path.dirname(path), "samples")
        os.makedirs(samples_dir, exist_ok=True)
        used_filenames = set()
        
        # Handle proper sample groups if they exist
        if hasattr(self, 'sample_groups') and self.sample_groups:
            # Export organized sample groups
            for group in self.sample_groups:
                if not group.samples:
                    continue  # Skip empty groups
                    
                group_attribs = {"enabled": str(group.enabled).lower()}
                
                # Add group-level attributes
                if group.volume != 0.0:
                    group_attribs["volume"] = f"{group.volume}dB"
                if group.pan != 0.0:
                    group_attribs["pan"] = str(group.pan)
                
                # Add tags if present
                if group.tags:
                    group_attribs["tags"] = ",".join(group.tags)
                
                # Add group-level envelope if present
                if any(x is not None for x in [group.attack, group.decay, group.sustain, group.release]):
                    if group.attack is not None:
                        group_attribs["attack"] = str(group.attack)
                    if group.decay is not None:
                        group_attribs["decay"] = str(group.decay)
                    if group.sustain is not None:
                        group_attribs["sustain"] = str(group.sustain)
                    if group.release is not None:
                        group_attribs["release"] = str(group.release)
                
                if self.cut_all_by_all:
                    group_attribs["tags"] = "cutgroup0"
                    group_attribs["silencedByTags"] = "cutgroup0"
                    group_attribs["silencingMode"] = self.silencing_mode
                
                group_elem = ET.SubElement(groups_elem, "group", group_attribs)
                
                # Add all samples in this group
                for zone in group.samples:
                    self._export_sample_to_group(zone, group_elem, samples_dir, used_filenames, path)
        else:
            # Fallback: create individual groups for each sample (legacy behavior)
            zones = self.sample_manager.get_zones() if self.sample_manager and self.sample_manager.get_zones() else [
                SampleZone(m.path, m.root, m.lo, m.hi) for m in self.mappings
            ]
            for zone in zones:
                group_elem = ET.SubElement(groups_elem, "group", {
                    "enabled": "true"
                })
                if self.cut_all_by_all:
                    group_elem.set("tags", "cutgroup0")
                    group_elem.set("silencedByTags", "cutgroup0")
                    group_elem.set("silencingMode", self.silencing_mode)
                self._export_sample_to_group(zone, group_elem, samples_dir, used_filenames, path)
        
        # Write modulator mapping and text display to XML tree, after groups section
        self._write_modulators_to_xml(root, control_name_map)
        
        # Pretty-print XML using minidom
        import xml.dom.minidom
        rough_string = ET.tostring(root, encoding="utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")
        with open(path, "wb") as f:
            f.write(pretty_xml)
    
    def _export_sample_to_group(self, zone, group_elem, samples_dir, used_filenames, preset_path):
        """Export a single sample to a group element"""
        import os
        import shutil
        
        orig_path = zone.path
        if not os.path.isfile(orig_path):
            raise Exception(f"Sample file not found: {orig_path}")
        
        # Always use just the basename for the sample in the export
        base_filename = os.path.basename(orig_path)
        # Ensure no filename collisions
        unique_filename = base_filename
        i = 1
        while unique_filename in used_filenames:
            name, ext = os.path.splitext(base_filename)
            unique_filename = f"{name}_{i}{ext}"
            i += 1
        used_filenames.add(unique_filename)
        
        dest_path = os.path.join(samples_dir, unique_filename)
        xml_rel_path = os.path.join("samples", unique_filename)
        
        # Copy the file if not already present or if source is newer
        if not os.path.exists(dest_path) or os.path.getmtime(orig_path) > os.path.getmtime(dest_path):
            shutil.copy2(orig_path, dest_path)
        
        xml_rel_path = xml_rel_path.replace("\\", "/")
        
        sample_attribs = {
            "path": xml_rel_path,
            "rootNote": str(zone.rootNote),
            "loNote": str(zone.loNote),
            "hiNote": str(zone.hiNote)
        }
        
        # Add velocity range if not default
        if hasattr(zone, "velocityRange") and zone.velocityRange != (0, 127):
            sample_attribs["velocityRange"] = f"{zone.velocityRange[0]},{zone.velocityRange[1]}"
        
        # Add sample tags if present
        if hasattr(zone, "tags") and zone.tags:
            sample_attribs["tags"] = ",".join(zone.tags)
        
        # Add advanced sampling attributes if not default
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
        
        # Add loop attributes if enabled
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
    
    def _write_modulators_to_xml(self, root, control_name_map):
        """Write modulator sections to XML"""
        # MIDI CC mapping for controls with midi_cc set
        midi_controls = [el for el in getattr(self.ui, "elements", []) if getattr(el, "midi_cc", None) is not None]
        if midi_controls:
            midi_elem = ET.SubElement(root, "midi")
            cc_map = {}
            for el in midi_controls:
                cc_num = str(getattr(el, "midi_cc"))
                if cc_num not in cc_map:
                    cc_elem = ET.SubElement(midi_elem, "cc", {"number": cc_num})
                    cc_map[cc_num] = cc_elem
                # Use position as index in ui.elements
                position = str(getattr(self.ui.elements, "index", lambda x: None)(el)) if hasattr(self.ui.elements, "index") else "0"
                # Fallback: use order in midi_controls
                if position == "None":
                    position = str(midi_controls.index(el))
                ET.SubElement(cc_map[cc_num], "binding", {
                    "level": "ui",
                    "type": "control",
                    "parameter": "VALUE",
                    "position": position,
                    "translation": "linear",
                    "translationOutputMin": "0",
                    "translationOutputMax": "1"
                })

        # --- GLOBAL PARAMETER BLOCKS ---
        # Determine which controls are present
        control_targets = {getattr(el, "target", None) for el in getattr(self.ui, "elements", [])}
        # AMPEG: if any envelope controls are present
        if any(t in ("ENV_ATTACK", "ENV_DECAY", "ENV_SUSTAIN", "ENV_RELEASE") for t in control_targets):
            ET.SubElement(root, "ampeg", {
                "attack": "0.01",
                "decay": "0.2",
                "sustain": "1.0",
                "release": "0.3"
            })
        # REVERB: if any REVERB_* control or have_reverb
        if any(t and t.startswith("REVERB_") for t in control_targets) or getattr(self, "have_reverb", False):
            ET.SubElement(root, "reverb", {
                "wetLevel": "0.5",
                "roomSize": "0.8"
            })
        # CHORUS: if any CHORUS_* control or have_chorus
        if any(t and t.startswith("CHORUS_") for t in control_targets) or getattr(self, "have_chorus", False):
            ET.SubElement(root, "chorus", {
                "delay": "20",
                "depth": "0.3",
                "rate": "0.25"
            })
        # FILTER: if any FILTER_* control or have_tone
        if any(t and t.startswith("FILTER_") for t in control_targets) or getattr(self, "have_tone", False):
            ET.SubElement(root, "filter", {
                "type": "lowpass",
                "cutoff": "20000",
                "resonance": "0.1"
            })
