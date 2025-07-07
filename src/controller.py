from model import InstrumentPreset

def load_preset(path):
    """Load a DecentSampler preset from file and return an InstrumentPreset instance."""
    return InstrumentPreset.from_dspreset(path)

def save_preset(path, preset):
    """Save the given InstrumentPreset to a DecentSampler .dspreset file."""
    preset.to_dspreset(path)
