"""Saving must never damage an existing preset.

The writer builds the whole file in memory, writes it to a temporary file in the
same folder, fsyncs it, then moves it over the target with os.replace. If anything
fails first, the original file is untouched and the user sees the error.
"""
import os
import stat
import sys
import wave

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import serialization.dspreset_writer as writer_module
from models.data_classes import SampleZone
from models.instrument_preset import InstrumentPreset
from serialization.dspreset_writer import write_dspreset

ORIGINAL = b"<?xml version='1.0'?>\n<DecentSampler presetName='original, do not lose'/>\n"


def _wav(path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"\x00\x00" * 32)


@pytest.fixture
def setup(tmp_path):
    wav = tmp_path / "kick.wav"
    _wav(wav)
    preset = InstrumentPreset("New Name")
    preset.sample_manager.zones = [SampleZone(str(wav), 60, 60, 60)]
    target = tmp_path / "out" / "preset.dspreset"
    target.parent.mkdir()
    target.write_bytes(ORIGINAL)
    return preset, target


def _leftovers(folder):
    return [p.name for p in folder.iterdir() if p.name.endswith(".tmp")]


def test_failed_write_leaves_original_byte_identical(setup, monkeypatch):
    """A write that fails part-way (disk full, I/O error) must not touch the target."""
    preset, target = setup
    real_open = open

    class FailingFile:
        def __init__(self, handle):
            self._handle = handle

        def write(self, data):
            self._handle.write(data[: len(data) // 2])  # a partial write, then the failure
            self._handle.flush()
            raise OSError(28, "No space left on device")

        def __getattr__(self, name):
            return getattr(self._handle, name)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self._handle.close()
            return False

    def fake_open(path, mode="r", *args, **kwargs):
        handle = real_open(path, mode, *args, **kwargs)
        return FailingFile(handle) if "w" in mode else handle

    monkeypatch.setattr(writer_module, "open", fake_open, raising=False)

    with pytest.raises(OSError):
        write_dspreset(preset, str(target))

    assert target.read_bytes() == ORIGINAL
    assert _leftovers(target.parent) == []


def test_failure_while_building_xml_leaves_original(setup, monkeypatch):
    """Regression guard: an exception during serialisation leaves the target alone."""
    preset, target = setup

    def boom(*args, **kwargs):
        raise RuntimeError("serialisation failed")

    monkeypatch.setattr(writer_module.ET, "tostring", boom)
    with pytest.raises(RuntimeError):
        write_dspreset(preset, str(target))
    assert target.read_bytes() == ORIGINAL
    assert _leftovers(target.parent) == []


def test_failure_at_final_replace_leaves_original_and_no_temp(setup, monkeypatch):
    preset, target = setup

    def fail_replace(src, dst):
        raise OSError("replace refused")

    monkeypatch.setattr(writer_module.os, "replace", fail_replace)
    with pytest.raises(OSError):
        write_dspreset(preset, str(target))
    assert target.read_bytes() == ORIGINAL
    assert _leftovers(target.parent) == []


@pytest.mark.skipif(sys.platform == "win32" or (hasattr(os, "geteuid") and os.geteuid() == 0),
                    reason="needs POSIX directory permissions and a non-root user")
def test_unwritable_folder_leaves_original(setup):
    """Cannot create the temp file next to the target: the original survives, error raised.

    The old in-place writer happily overwrote a writable file inside a read-only
    folder; the new one refuses, because it cannot do so atomically.
    """
    preset, target = setup
    folder = target.parent
    (folder / "samples").mkdir()  # so the failure is at the temp file, not at making samples/
    folder.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        with pytest.raises(OSError):
            write_dspreset(preset, str(target))
    finally:
        folder.chmod(stat.S_IRWXU)
    assert target.read_bytes() == ORIGINAL


def test_successful_write_replaces_file_and_leaves_no_temp(setup):
    preset, target = setup
    write_dspreset(preset, str(target))
    data = target.read_bytes()
    assert data != ORIGINAL
    assert b'presetName="New Name"' in data
    assert _leftovers(target.parent) == []


def test_successful_write_keeps_existing_file_permissions(setup):
    if sys.platform == "win32":
        pytest.skip("POSIX permissions")
    preset, target = setup
    target.chmod(0o640)
    write_dspreset(preset, str(target))
    assert stat.S_IMODE(target.stat().st_mode) == 0o640


def test_sample_copy_never_overwrites_a_different_file(tmp_path):
    """A same-named but different file in samples/ is kept; the new sample gets a new name."""
    src = tmp_path / "src"
    src.mkdir()
    wav = src / "kick.wav"
    _wav(wav)
    out = tmp_path / "out"
    (out / "samples").mkdir(parents=True)
    other = out / "samples" / "kick.wav"
    other.write_bytes(b"someone else's recording")

    preset = InstrumentPreset("P")
    preset.sample_manager.zones = [SampleZone(str(wav), 60, 60, 60)]
    write_dspreset(preset, str(out / "p.dspreset"))

    assert other.read_bytes() == b"someone else's recording"
    assert (out / "samples" / "kick_1.wav").read_bytes() == wav.read_bytes()


def test_same_size_different_content_is_not_overwritten(tmp_path):
    """Equal length is not enough to count as the same file: the bytes are compared."""
    src = tmp_path / "src"
    src.mkdir()
    wav = src / "kick.wav"
    _wav(wav)
    out = tmp_path / "out"
    (out / "samples").mkdir(parents=True)
    other = out / "samples" / "kick.wav"
    other.write_bytes(b"x" * wav.stat().st_size)  # same size, different bytes
    # Same modification time too. Windows stamps files from a clock that ticks about
    # every 15 ms, so two files written back to back get one time; set it outright so
    # the test checks this on every platform and does not depend on timing.
    stamp = wav.stat().st_mtime_ns
    os.utime(other, ns=(stamp, stamp))
    assert other.stat().st_size == wav.stat().st_size
    assert other.stat().st_mtime_ns == wav.stat().st_mtime_ns

    preset = InstrumentPreset("P")
    preset.sample_manager.zones = [SampleZone(str(wav), 60, 60, 60)]
    write_dspreset(preset, str(out / "p.dspreset"))

    assert other.read_bytes() == b"x" * wav.stat().st_size
    assert (out / "samples" / "kick_1.wav").read_bytes() == wav.read_bytes()


def test_repeat_save_does_not_copy_samples_again(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    wav = src / "kick.wav"
    _wav(wav)
    out = tmp_path / "out"
    out.mkdir()
    preset = InstrumentPreset("P")
    preset.sample_manager.zones = [SampleZone(str(wav), 60, 60, 60)]

    copies = []
    real_copy2 = writer_module.shutil.copy2
    monkeypatch.setattr(writer_module.shutil, "copy2",
                        lambda a, b, *args, **kw: copies.append(b) or real_copy2(a, b, *args, **kw))

    write_dspreset(preset, str(out / "p.dspreset"))
    assert len(copies) == 1
    write_dspreset(preset, str(out / "p.dspreset"))
    assert len(copies) == 1  # unchanged: nothing copied the second time
