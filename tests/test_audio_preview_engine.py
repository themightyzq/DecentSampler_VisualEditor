"""The audio preview must survive a machine with no audio device.

pygame imports fine on a CI runner or a server, but pygame.mixer.init() then fails.
The preview widget polls the engine from a QTimer every 100 ms; if the poll raised,
PyQt5 would abort the whole process (a Python exception in a slot is fatal), so the
editor died a moment after it opened.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

pygame = pytest.importorskip("pygame", reason="pygame is an optional dependency")

from widgets import audio_preview


@pytest.fixture
def engine_without_audio_device(monkeypatch):
    def no_device(*args, **kwargs):
        raise pygame.error("No audio device")

    monkeypatch.setattr(audio_preview.pygame.mixer, "init", no_device)
    monkeypatch.setattr(audio_preview.pygame.mixer, "get_init", lambda: None)
    pygame.mixer.quit()  # a mixer left initialised by another test would hide the bug
    return audio_preview.AudioPreviewEngine()


def test_engine_reports_not_ready_without_a_device(engine_without_audio_device):
    assert engine_without_audio_device.mixer_ready is False


def test_polling_stop_and_pause_do_not_raise_without_a_device(engine_without_audio_device):
    engine = engine_without_audio_device
    assert engine.get_is_playing() is False  # what the 100 ms timer calls
    engine.stop()
    engine.pause()
    assert engine.is_playing is False
