import pytest
import os
from ffmpeg_utils.ffmpeg_handler import FFmpeg
import pathlib

# Test video paths (relative to this test file)
TESTS_DIR = pathlib.Path(__file__).parent
ASSETS_DIR = TESTS_DIR / "assets"
TEST_VIDEO1 = str(ASSETS_DIR / "test_1_16_9.mp4")
TEST_VIDEO2 = str(ASSETS_DIR / "test_2_16_9.mp4")

def test_trim_action():
    ffmpeg = FFmpeg()
    workflow = {'action': 'trim', 'input': TEST_VIDEO1, 'start': 0, 'duration': 1}
    output = ffmpeg.render_workflow(workflow)
    assert os.path.exists(output)

def test_concat_action():
    ffmpeg = FFmpeg()
    workflow = {
        'action': 'concat',
        'input': [
            {'action': 'trim', 'input': TEST_VIDEO1, 'start': 0, 'duration': 3},
            {'action': 'trim', 'input': TEST_VIDEO2, 'start': 0, 'duration': 3}
        ]
    }
    output = ffmpeg.render_workflow(workflow)
    assert os.path.exists(output)
