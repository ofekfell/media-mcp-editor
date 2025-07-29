import pathlib
import pytest
import os
from fastmcp import FastMCP
from media_mcp_handler.media_mcp import MediaMCPHandler, send_response
from tests.test_proper_split import TEST_VIDEO

# Test video paths (relative to this test file)
TESTS_DIR = pathlib.Path(__file__).parent
ASSETS_DIR = TESTS_DIR / "assets"
TEST_VIDEO1 = str(ASSETS_DIR / "test_1_16_9.mp4")
TEST_VIDEO2 = str(ASSETS_DIR / "test_2_16_9.mp4")

def test_server_render_workflow():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'concat',
        'input': [
            {'action': 'trim', 'input': TEST_VIDEO1, 'start': 0, 'duration': 1},
            {'action': 'trim', 'input': TEST_VIDEO2, 'start': 0, 'duration': 1}
        ]
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_cut_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'cut',
        'input': TEST_VIDEO1,
        'x': 0, 'y': 0, 'width': 640, 'height': 360
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_change_volume_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'change_volume',
        'input': TEST_VIDEO1,
        'volume': 0.5
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_scale_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'scale',
        'input': TEST_VIDEO1,
        'width': 1280, 'height': 720
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_fade_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'fade',
        'input': TEST_VIDEO1,
        'type': 'in', 'start_time': 0, 'duration': 1
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_rotate_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'rotate',
        'input': TEST_VIDEO1,
        'angle': 90
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_speed_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'speed',
        'input': TEST_VIDEO1,
        'factor': 2.0
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_blur_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'blur',
        'input': TEST_VIDEO1,
        'radius': 5
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_crossfade_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'crossfade',
        'input': [
            TEST_VIDEO1,
            TEST_VIDEO2
        ],
        'duration': 2.0,
        'transition': 'fade',
        'stream1_duration': 10.0
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_audio_mix_action():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'audio_mix',
        'input': [
            TEST_VIDEO1,
            TEST_VIDEO2
        ],
        'weights': '0.5 0.5'
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_overlay_action():
    handler = MediaMCPHandler()
    # Create two separate videos first, then overlay
    base_video = {
        'action': 'trim',
        'input': TEST_VIDEO1,
        'start': 0, 'duration': 3
    }
    overlay_video = {
        'action': 'scale',
        'input': {
            'action': 'trim',
            'input': TEST_VIDEO2,
            'start': 0, 'duration': 3
        },
        'width': 320, 'height': 180
    }
    workflow = {
        'action': 'overlay',
        'input': [base_video, overlay_video],
        'x': 10, 'y': 10
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_normalization_actions():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'set_fps',
        'input': {
            'action': 'set_format',
            'input': {
                'action': 'reset_video_pts',
                'input': TEST_VIDEO1
            },
            'format': 'yuv420p'
        },
        'fps': 24
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_audio_normalization_actions():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'audio_dynaudnorm',
        'input': {
            'action': 'reset_audio_pts',
            'input': {
                'action': 'audio_resample',
                'input': TEST_VIDEO1,
                'sample_rate': 48000
            }
        }
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_complex_workflow():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'crossfade',
        'input': [
            {
                'action': 'fade',
                'input': {
                    'action': 'scale',
                    'input': {
                        'action': 'trim',
                        'input': TEST_VIDEO1,
                        'start': 0, 'duration': 5
                    },
                    'width': 640, 'height': 360
                },
                'type': 'in', 'duration': 1
            },
            {
                'action': 'change_volume',
                'input': {
                    'action': 'scale',
                    'input': {
                        'action': 'trim',
                        'input': TEST_VIDEO2,
                        'start': 0, 'duration': 5
                    },
                    'width': 640, 'height': 360
                },
                'volume': 0.8
            }
        ],
        'duration': 2.0,
        'stream1_duration': 5.0
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response

def test_multi_action_concat():
    handler = MediaMCPHandler()
    workflow = {
        'action': 'concat',
        'input': [
            {
                'action': 'blur',
                'input': {
                    'action': 'rotate',
                    'input': TEST_VIDEO1,
                    'angle': 45
                },
                'radius': 3
            },
            {
                'action': 'speed',
                'input': {
                    'action': 'scale',
                    'input': TEST_VIDEO2,
                    'width': 640, 'height': 360
                },
                'factor': 1.5
            }
        ]
    }
    result = handler.render_workflow(workflow)
    response = send_response(result=result)
    assert 'result' in response
