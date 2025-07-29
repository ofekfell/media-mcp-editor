import pathlib
import pytest
import os
from media_mcp_handler.media_mcp import MediaMCPHandler

# Test video paths (relative to this test file)
TESTS_DIR = pathlib.Path(__file__).parent
ASSETS_DIR = TESTS_DIR / "assets"
TEST_VIDEO1 = str(ASSETS_DIR / "test_1_16_9.mp4")
TEST_VIDEO2 = str(ASSETS_DIR / "test_2_16_9.mp4")

def test_render_workflow():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'concat',
        'input': [
            {'action': 'trim', 'input': TEST_VIDEO1, 'start': 0, 'duration': 1},
            {'action': 'trim', 'input': TEST_VIDEO2, 'start': 0, 'duration': 1}
        ]
    }
    result = handler.render_workflow(workflow)
    assert 'result_path' in result
