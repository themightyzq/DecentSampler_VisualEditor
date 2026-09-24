from typing import List, Optional


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
        self.seqMode = seqMode
        self.seqPosition = seqPosition
        self.volume = volume
        self.pan = pan
        self.tune = tune

        # Sample playback range
        self.start = start
        self.end = end

        # Loop settings
        self.loopEnabled = loopEnabled
        self.loopStart = loopStart
        self.loopEnd = loopEnd
        self.loopCrossfade = loopCrossfade
        self.loopMode = loopMode

        # Sample tags for blending and organization
        self.tags = tags or []

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
        self.waveform = waveform
        self.amplitude = amplitude
        self.offset = offset
        self.phase = phase
        self.sync = sync
        self.sync_length = sync_length
        self.retrigger = retrigger


class ModulatorTarget:
    def __init__(self, target_type: str, parameter: str, level: str = "instrument",
                 position: int = 0, group_index: int = None, effect_index: int = None):
        self.target_type = target_type
        self.parameter = parameter
        self.level = level
        self.position = position
        self.group_index = group_index
        self.effect_index = effect_index


class ModulationRoute:
    def __init__(self, modulator_name: str, target: ModulatorTarget,
                 amount: float = 1.0, invert: bool = False):
        self.modulator_name = modulator_name
        self.target = target
        self.amount = amount
        self.invert = invert


class UIElement:
    def __init__(self, x, y, width, height, label, skin=None, tag=None, widget_type=None,
                 target=None, min_val=None, max_val=None, bindings=None, options=None,
                 midi_cc=None, orientation=None, color_ranges=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.skin = skin
        self.tag = tag
        self.widget_type = widget_type
        self.target = target
        self.min_val = min_val
        self.max_val = max_val
        self.bindings = bindings if bindings is not None else []
        self.options = options if options is not None else []
        self.midi_cc = midi_cc
        self.orientation = orientation
        self.color_ranges = color_ranges if color_ranges is not None else []
