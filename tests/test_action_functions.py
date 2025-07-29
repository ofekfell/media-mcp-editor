import pytest
import os
import pathlib
from ffmpeg_utils.ffmpeg_handler import FFmpeg, ACTION_REGISTRY, handle_trim, handle_cut, handle_change_volume, handle_concat, handle_scale, handle_fade
import ffmpeg

# Test video paths (relative to this test file)
TESTS_DIR = pathlib.Path(__file__).parent
ASSETS_DIR = TESTS_DIR / "assets"
TEST_VIDEO1 = str(ASSETS_DIR / "test_1_16_9.mp4")
TEST_VIDEO2 = str(ASSETS_DIR / "test_2_16_9.mp4")

class TestActionRegistry:
    """Test the action registry system."""
    
    def test_registry_contains_all_actions(self):
        """Test that all expected actions are registered."""
        expected_actions = ['trim', 'cut', 'change_volume', 'concat', 'scale', 'fade', 'rotate', 'speed', 'blur', 'crossfade', 'audio_mix']
        for action in expected_actions:
            assert action in ACTION_REGISTRY, f"Action '{action}' not found in registry"
    
    def test_registry_functions_are_callable(self):
        """Test that all registered functions are callable."""
        for action, func in ACTION_REGISTRY.items():
            assert callable(func), f"Action '{action}' is not callable"

class TestTrimAction:
    """Test the trim action function."""
    
    def test_trim_video_only(self):
        """Test trimming a video-only stream."""
        video_stream = ffmpeg.input(TEST_VIDEO1).video
        
        params = {'start': 1, 'duration': 2}
        result = handle_trim(video_stream, params)
        
        # Should return a single stream (not tuple)
        assert not isinstance(result, tuple)
    
    def test_trim_video_audio_tuple(self):
        """Test trimming video and audio streams."""
        inp = ffmpeg.input(TEST_VIDEO1)
        streams = (inp.video, inp.audio)
        
        params = {'start': 1, 'duration': 2}
        result = handle_trim(streams, params)
        
        # Should return tuple of (video, audio)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_trim_with_none_audio(self):
        """Test trimming with None audio stream."""
        inp = ffmpeg.input(TEST_VIDEO1)
        streams = (inp.video, None)
        
        params = {'start': 1, 'duration': 2}
        result = handle_trim(streams, params)
        
        # Should return tuple with None audio
        assert isinstance(result, tuple)
        assert result[1] is None

class TestCutAction:
    """Test the cut (crop) action function."""
    
    def test_cut_video_only(self):
        """Test cutting/cropping a video-only stream."""
        video_stream = ffmpeg.input(TEST_VIDEO1).video
        
        params = {'x': 0, 'y': 0, 'width': 320, 'height': 240}
        result = handle_cut(video_stream, params)
        
        # Should return a single stream (not tuple)
        assert not isinstance(result, tuple)
    
    def test_cut_video_audio_tuple(self):
        """Test cutting video while preserving audio."""
        inp = ffmpeg.input(TEST_VIDEO1)
        streams = (inp.video, inp.audio)
        
        params = {'x': 0, 'y': 0, 'width': 320, 'height': 240}
        result = handle_cut(streams, params)
        
        # Should return tuple with cropped video and unchanged audio
        assert isinstance(result, tuple)
        assert len(result) == 2

class TestChangeVolumeAction:
    """Test the change_volume action function."""
    
    def test_change_volume_video_audio_tuple(self):
        """Test changing volume on video/audio tuple."""
        inp = ffmpeg.input(TEST_VIDEO1)
        streams = (inp.video, inp.audio)
        
        params = {'volume': 0.5}
        result = handle_change_volume(streams, params)
        
        # Should return tuple with unchanged video and modified audio
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_change_volume_with_none_audio(self):
        """Test changing volume with None audio stream."""
        inp = ffmpeg.input(TEST_VIDEO1)
        streams = (inp.video, None)
        
        params = {'volume': 0.5}
        result = handle_change_volume(streams, params)
        
        # Should return tuple with None audio unchanged
        assert isinstance(result, tuple)
        assert result[1] is None
    
    def test_change_volume_audio_only(self):
        """Test changing volume on audio-only stream."""
        audio_stream = ffmpeg.input(TEST_VIDEO1)
        
        params = {'volume': 0.5}
        result = handle_change_volume(audio_stream, params)
        
        # Should return modified stream
        assert result is not None

class TestConcatAction:
    """Test the concat action function."""
    
    def test_concat_multiple_streams(self):
        """Test concatenating multiple video/audio stream pairs."""
        # Create multiple stream pairs
        inp1 = ffmpeg.input(TEST_VIDEO1)
        inp2 = ffmpeg.input(TEST_VIDEO2)
        streams_list = [
            (inp1.video, inp1.audio),
            (inp2.video, inp2.audio)
        ]
        
        params = {}
        result = handle_concat(streams_list, params)
        
        # Should return tuple of concatenated (video, audio)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_concat_mismatched_streams_raises_error(self):
        """Test that mismatched video/audio streams raise an error."""
        # Create mismatched streams (different lengths)
        inp1 = ffmpeg.input(TEST_VIDEO1)
        streams_list = [
            (inp1.video, inp1.audio),
            (inp1.video,)  # Missing audio
        ]
        
        params = {}
        with pytest.raises(ValueError, match="All streams must have both video and audio"):
            handle_concat(streams_list, params)

class TestWorkflowIntegration:
    """Test complete workflow building and execution."""
    
    def test_simple_trim_workflow(self):
        """Test a simple trim workflow."""
        ffmpeg_handler = FFmpeg()
        workflow = {
            'action': 'trim',
            'input': TEST_VIDEO1,
            'start': 0,
            'duration': 2
        }
        
        output = ffmpeg_handler.render_workflow(workflow)
        assert os.path.exists(output)
        
        # Clean up
        if os.path.exists(output):
            os.remove(output)
    
    def test_complex_nested_workflow(self):
        """Test a complex workflow with nested actions."""
        ffmpeg_handler = FFmpeg()
        workflow = {
            'action': 'concat',
            'input': [
                {
                    'action': 'trim',
                    'input': TEST_VIDEO1,
                    'start': 0,
                    'duration': 1
                },
                {
                    'action': 'change_volume',
                    'input': {
                        'action': 'trim',
                        'input': TEST_VIDEO2,
                        'start': 0,
                        'duration': 1
                    },
                    'volume': 0.5
                }
            ]
        }
        
        output = ffmpeg_handler.render_workflow(workflow)
        assert os.path.exists(output)
        
        # Clean up
        if os.path.exists(output):
            os.remove(output)
    
    def test_invalid_action_raises_error(self):
        """Test that invalid actions raise appropriate errors."""
        ffmpeg_handler = FFmpeg()
        workflow = {
            'action': 'invalid_action',
            'input': {'url': TEST_VIDEO1}
        }
        
        with pytest.raises(ValueError, match="Unknown action"):
            ffmpeg_handler.render_workflow(workflow)
    
    def test_invalid_node_format_raises_error(self):
        """Test that invalid node formats raise appropriate errors."""
        ffmpeg_handler = FFmpeg()
        
        # Test with invalid input (not dict or string)
        with pytest.raises(ValueError, match="Invalid node format"):
            ffmpeg_handler.render_workflow(123)  # Invalid type

class TestNewActions:
    """Test the new action functions."""
    
    def test_scale_action(self):
        """Test scale action function."""
        inp = ffmpeg.input(TEST_VIDEO1)
        streams = (inp.video, inp.audio)
        
        params = {'width': 1280, 'height': 720}
        result = handle_scale(streams, params)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_fade_action(self):
        """Test fade action function."""
        inp = ffmpeg.input(TEST_VIDEO1)
        streams = (inp.video, inp.audio)
        
        params = {'type': 'in', 'start_time': 0, 'duration': 1}
        result = handle_fade(streams, params)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    

if __name__ == "__main__":
    pytest.main([__file__])