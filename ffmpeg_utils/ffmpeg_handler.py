import ffmpeg
import logging
import uuid
import os
import shutil
from urllib.parse import urlparse

from typing import Any, Dict, Callable

logger = logging.getLogger(__name__)

# Action registry for robust, extensible action handling
ACTION_REGISTRY: Dict[str, Callable] = {}

def action_handler(name):
    def decorator(func):
        ACTION_REGISTRY[name] = func
        return func
    return decorator

@action_handler('trim')
def handle_trim(streams, params):
    # streams: (video, audio) or just video
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.trim(start=params['start'], duration=params['duration']).setpts('PTS-STARTPTS')
        a_out = a.filter('atrim', start=params['start'], duration=params['duration']).filter('asetpts', 'PTS-STARTPTS') if a is not None else None
        return v_out, a_out
    else:
        return streams.trim(start=params['start'], duration=params['duration']).setpts('PTS-STARTPTS')

@action_handler('cut')
def handle_cut(streams, params):
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.crop(params['x'], params['y'], params['width'], params['height'])
        return v_out, a
    else:
        return streams.crop(params['x'], params['y'], params['width'], params['height'])

@action_handler('change_volume')
def handle_change_volume(streams, params):
    if isinstance(streams, tuple):
        v, a = streams
        a_out = a.filter('volume', params['volume']) if a is not None else None
        return v, a_out
    else:
        return streams.audio.filter('volume', params['volume'])

@action_handler('concat')
def handle_concat(streams_list, params):
    """
    Alternative using filter() method for more explicit control
    """
    if all(isinstance(s, tuple) for s in streams_list):
        # Validate all tuples have exactly 2 elements (video, audio)
        for s in streams_list:
            if len(s) != 2:
                raise ValueError("All streams must have both video and audio for concat action")
        
        videos = [s[0] for s in streams_list]
        audios = [s[1] for s in streams_list]
        
        # Concatenate videos using filter method
        video_out = ffmpeg.filter(videos, 'concat', n=len(videos), v=1, a=0)
        audio_out = ffmpeg.filter(audios, 'concat', n=len(audios), v=0, a=1)
        return video_out, audio_out

@action_handler('scale')
def handle_scale(streams, params):
    """Scale video to specified dimensions"""
    if isinstance(streams, tuple):
        v, a = streams
        width = params.get('width', -1)
        height = params.get('height', -1)
        v_out = v.filter('scale', w=width, h=height)
        return v_out, a
    else:
        width = params.get('width', -1)
        height = params.get('height', -1)
        return streams.filter('scale', w=width, h=height)

@action_handler('overlay')
def handle_overlay(streams_list, params):
    """Overlay one video on top of another"""
    if not isinstance(streams_list, list) or len(streams_list) != 2:
        raise ValueError("Overlay action requires exactly 2 video streams")
    
    base_stream, overlay_stream = streams_list
    x = params.get('x', 0)
    y = params.get('y', 0)
    
    if isinstance(base_stream, tuple) and isinstance(overlay_stream, tuple):
        base_v, base_a = base_stream
        overlay_v, _ = overlay_stream  # Don't need overlay audio
        v_out = base_v.overlay(overlay_v, x=x, y=y)
        return v_out, base_a
    else:
        return base_stream.overlay(overlay_stream, x=x, y=y)

@action_handler('fade')
def handle_fade(streams, params):
    """Add fade in/out effect"""
    fade_type = params.get('type', 'in')  # 'in' or 'out'
    start_time = params.get('start_time', 0)
    duration = params.get('duration', 1)
    
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.filter('fade', type=fade_type, start_time=start_time, duration=duration)
        if a is not None:
            a_out = a.filter('afade', type=fade_type, start_time=start_time, duration=duration)
        else:
            a_out = None
        return v_out, a_out
    else:
        return streams.filter('fade', type=fade_type, start_time=start_time, duration=duration)

@action_handler('rotate')
def handle_rotate(streams, params):
    """Rotate video by specified angle"""
    angle = params.get('angle', 0)  # in degrees
    angle_rad = f"{angle}*PI/180"  # convert to radians
    
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.filter('rotate', angle=angle_rad)
        return v_out, a
    else:
        return streams.filter('rotate', angle=angle_rad)

@action_handler('speed')
def handle_speed(streams, params):
    """Change playback speed"""
    factor = params.get('factor', 1.0)
    
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.filter('setpts', f'PTS/{factor}')
        if a is not None:
            a_out = a.filter('atempo', tempo=factor)
        else:
            a_out = None
        return v_out, a_out
    else:
        return streams.filter('setpts', f'PTS/{factor}')

@action_handler('blur')
def handle_blur(streams, params):
    """Apply blur effect"""
    radius = params.get('radius', 5)
    
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.filter('gblur', sigma=radius)
        return v_out, a
    else:
        return streams.filter('gblur', sigma=radius)


@action_handler('crossfade')
def handle_crossfade(streams_list, params):
    """Crossfade between two streams"""
    if len(streams_list) != 2:
        raise ValueError("Crossfade requires exactly 2 streams")
    
    duration = params.get('duration', 1.0)
    transition = params.get('transition', 'fade')
    stream1_duration = params.get('stream1_duration')
    
    if not stream1_duration:
        raise ValueError("stream1_duration parameter is required for crossfade")
    
    # Calculate offset automatically: crossfade starts (duration) seconds before first stream ends
    offset = stream1_duration - duration
    
    stream1, stream2 = streams_list
    
    if isinstance(stream1, tuple) and isinstance(stream2, tuple):
        v1, a1 = stream1
        v2, a2 = stream2
        
        # Normalize FPS to ensure consistent frame rates for crossfade
        v1_normalized = v1.filter('fps', fps=30)
        v2_normalized = v2.filter('fps', fps=30)
        
        v_out = ffmpeg.filter([v1_normalized, v2_normalized], 'xfade', transition=transition, offset=offset, duration=duration)
        if a1 is not None and a2 is not None:
            a_out = ffmpeg.filter([a1, a2], 'acrossfade', d=duration, c1=0, c2=1)
        else:
            a_out = a1 or a2
        return v_out, a_out
    else:
        # Normalize FPS for single streams too
        stream1_normalized = stream1.filter('fps', fps=30)
        stream2_normalized = stream2.filter('fps', fps=30)
        return ffmpeg.filter([stream1_normalized, stream2_normalized], 'xfade', transition=transition, offset=offset, duration=duration)

@action_handler('audio_mix')
def handle_audio_mix(streams_list, params):
    """Mix multiple audio streams"""
    weights = params.get('weights', None)  # e.g., "0.5 0.5"
    
    if not all(isinstance(s, tuple) for s in streams_list):
        raise ValueError("Audio mix requires video/audio tuple streams")
    
    videos = [s[0] for s in streams_list]
    audios = [s[1] for s in streams_list if s[1] is not None]
    
    if len(audios) < 2:
        raise ValueError("Audio mix requires at least 2 audio streams")
    
    # Use first video, mix audios
    v_out = videos[0]
    mix_params = {'inputs': len(audios)}
    if weights:
        mix_params['weights'] = weights
    
    a_out = ffmpeg.filter(audios, 'amix', **mix_params)
    return v_out, a_out

@action_handler('set_fps')
def handle_set_fps(streams, params):
    """Set video frame rate"""
    fps = params.get('fps', 30)
    
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.filter('fps', fps=fps)
        return v_out, a
    else:
        return streams.filter('fps', fps=fps)

@action_handler('set_format')
def handle_set_format(streams, params):
    """Set video pixel format"""
    format_type = params.get('format', 'yuv420p')
    
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.filter('format', format_type)
        return v_out, a
    else:
        return streams.filter('format', format_type)

@action_handler('reset_video_pts')
def handle_reset_video_pts(streams, params):
    """Reset video presentation timestamp"""
    if isinstance(streams, tuple):
        v, a = streams
        v_out = v.filter('setpts', 'PTS-STARTPTS')
        return v_out, a
    else:
        return streams.filter('setpts', 'PTS-STARTPTS')

@action_handler('audio_resample')
def handle_audio_resample(streams, params):
    """Resample audio to specified sample rate"""
    sample_rate = params.get('sample_rate', 44100)
    
    if isinstance(streams, tuple):
        v, a = streams
        if a is not None:
            a_out = a.filter('aresample', sample_rate)
        else:
            a_out = None
        return v, a_out
    else:
        return streams.audio.filter('aresample', sample_rate)

@action_handler('reset_audio_pts')
def handle_reset_audio_pts(streams, params):
    """Reset audio presentation timestamp"""
    if isinstance(streams, tuple):
        v, a = streams
        if a is not None:
            a_out = a.filter('asetpts', 'PTS-STARTPTS')
        else:
            a_out = None
        return v, a_out
    else:
        return streams.audio.filter('asetpts', 'PTS-STARTPTS')

@action_handler('audio_dynaudnorm')
def handle_audio_dynaudnorm(streams, params):
    """Apply dynamic audio normalization"""
    if isinstance(streams, tuple):
        v, a = streams
        if a is not None:
            a_out = a.filter('dynaudnorm')
        else:
            a_out = None
        return v, a_out
    else:
        return streams.audio.filter('dynaudnorm')


def _find_ffmpeg_cmd():
    """Find the best available ffmpeg command."""
    # Try common locations in order of preference
    candidates = [
        '/opt/homebrew/bin/ffmpeg',  # Homebrew on Apple Silicon
        '/usr/local/bin/ffmpeg',     # Homebrew on Intel
        'ffmpeg'                     # System PATH
    ]
    
    for cmd in candidates:
        if cmd == 'ffmpeg':
            # Check if it's in PATH
            if shutil.which('ffmpeg'):
                return cmd
        else:
            # Check if the specific path exists
            if os.path.isfile(cmd):
                return cmd
    
    # Fallback to system PATH
    return 'ffmpeg'

class FFmpeg:
    def __init__(self):
        self.ffmpeg_cmd = _find_ffmpeg_cmd()
        self._file_copies = {}  # Maps original_path -> [copy1_path, copy2_path, ...]
        self._copy_usage_index = {}  # Maps original_path -> next_index_to_use
        logger.info(f"Initializing FFmpeg handler with command: {self.ffmpeg_cmd}")

    def get_media_info(self, input_source: str) -> dict:
        logger.info(f"Probing media info for: {input_source}")
        try:
            probe = ffmpeg.probe(input_source)
            logger.info(f"Media info probe successful for: {input_source}")
            return {"stdout": probe, "stderr": "", "returncode": 0}
        except ffmpeg.Error as e:
            logger.error(f"Media info probe failed for {input_source}: {e}")
            return {"stdout": "", "stderr": str(e), "returncode": 1}

    def _download_source_if_needed(self, source: str) -> str:
        """Download URL to local file if it's a remote URL, otherwise return path as-is."""
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            # Import here to avoid circular imports
            from files_util.file_handler import FileHandler
            file_handler = FileHandler()
            local_path = file_handler.download_url_to_local(source)
            if not local_path:
                raise ValueError(f"Failed to download URL: {source}")
            logger.info(f"Downloaded {source} to {local_path}")
            return local_path
        elif os.path.isfile(source):
            return source
        else:
            raise ValueError(f"Invalid URL or file path: {source}")
        
    def normalize_input(self, local_path):
        """
        Normalize input video to consistent format for concatenation using modular actions
        
        Args:
            local_path (str): Path to the input video file
            
        Returns:
            tuple: (video_stream, audio_stream) - normalized ffmpeg streams
        """
        try:
            # Get input
            inp = ffmpeg.input(local_path)
            streams = (inp.video, inp.audio)
            
            # Apply video normalization actions
            streams = ACTION_REGISTRY['set_format'](streams, {'format': 'yuv420p'})
            streams = ACTION_REGISTRY['reset_video_pts'](streams, {})
            streams = ACTION_REGISTRY['set_fps'](streams, {'fps': 30})

            # Apply audio normalization actions
            streams = ACTION_REGISTRY['audio_resample'](streams, {'sample_rate': 44100})
            streams = ACTION_REGISTRY['reset_audio_pts'](streams, {})
            streams = ACTION_REGISTRY['audio_dynaudnorm'](streams, {})
            
            return streams
            
        except Exception as e:
            raise Exception(f"Error normalizing input {local_path}: {str(e)}")

    def _scan_workflow_for_file_usage(self, node):
        """Scan workflow to count how many times each file is used."""
        file_usage = {}
        
        def scan_node(n):
            if isinstance(n, dict):
                if "url" in n:
                    # Found a file reference - convert to local path
                    source = n["url"]
                    local_path = self._download_source_if_needed(source)
                    file_usage[local_path] = file_usage.get(local_path, 0) + 1
                elif "action" in n:
                    # Recursively scan action inputs
                    input_data = n.get('input')
                    if isinstance(input_data, list):
                        # Multi-input action
                        for inp in input_data:
                            scan_node(inp)
                    elif input_data is not None:
                        # Single input action
                        scan_node(input_data)
            elif isinstance(n, str):
                # Legacy string input
                local_path = self._download_source_if_needed(n)
                file_usage[local_path] = file_usage.get(local_path, 0) + 1
        
        scan_node(node)
        return file_usage

    def _create_file_copies(self, file_usage):
        """Create hard copies for files that are used multiple times."""
        self._file_copies.clear()
        self._copy_usage_index.clear()
        
        for file_path, usage_count in file_usage.items():
            if usage_count > 1:
                logger.info(f"Creating {usage_count-1} copies for {file_path} (used {usage_count} times)")
                
                # Create copies (usage_count - 1 copies, since original counts as one)
                copies = []
                for i in range(usage_count - 1):
                    copy_path = os.path.realpath(f"/tmp/copy_{i}_{uuid.uuid4()}_{os.path.basename(file_path)}")
                    shutil.copy2(file_path, copy_path)
                    copies.append(copy_path)
                    logger.info(f"Created copy: {copy_path}")
                
                self._file_copies[file_path] = copies
                self._copy_usage_index[file_path] = 0

    def _get_unique_file_path(self, original_path):
        """Get a unique file path for each usage - original for first use, copies for subsequent uses."""
        if original_path not in self._file_copies:
            # File is only used once, return original
            return original_path
        
        # File is used multiple times
        usage_index = self._copy_usage_index[original_path]
        
        if usage_index == 0:
            # First usage - use original file
            self._copy_usage_index[original_path] += 1
            return original_path
        else:
            # Subsequent usage - use a copy
            copy_index = usage_index - 1
            copies = self._file_copies[original_path]
            if copy_index < len(copies):
                self._copy_usage_index[original_path] += 1
                return copies[copy_index]
            else:
                raise RuntimeError(f"No more copies available for {original_path}")

    def render_workflow(self, node) -> str:
        # Step 1 & 2: Scan workflow and create copies for duplicated files
        file_usage = self._scan_workflow_for_file_usage(node)
        logger.info(f"File usage analysis: {file_usage}")
        self._create_file_copies(file_usage)
        def build_stream(n):
            # Handle leaf nodes with media sources (URLs or file paths)
            if isinstance(n, dict) and "url" in n:
                source = n["url"]
                original_path = self._download_source_if_needed(source)
                unique_path = self._get_unique_file_path(original_path)
                return self.normalize_input(unique_path)
            
            # Handle action nodes
            if isinstance(n, dict) and "action" in n:
                action = n['action']
                if action in ['concat', 'crossfade', 'audio_mix', 'overlay']:
                    # Handle actions with list of inputs
                    inputs = n.get('input', [])
                    streams_list = [build_stream(inp) for inp in inputs]
                    return ACTION_REGISTRY[action](streams_list, n)
                else:
                    handler = ACTION_REGISTRY.get(action)
                    if not handler:
                        raise ValueError(f"Unknown action: {action}")
                    input_stream = build_stream(n['input'])
                    return handler(input_stream, n)
            
            # Legacy support for string inputs (should not happen with new architecture)
            if isinstance(n, str):
                original_path = self._download_source_if_needed(n)
                unique_path = self._get_unique_file_path(original_path)
                return self.normalize_input(unique_path)
            
            raise ValueError(f"Invalid node format: {n}")
            
        streams = build_stream(node)
        output_path = os.path.realpath(f"/tmp/final_{uuid.uuid4()}.mp4")
        if isinstance(streams, tuple):
            v, a = streams
            if a is not None:
                out = ffmpeg.output(v, a, output_path)
            else:
                out = ffmpeg.output(v, output_path)
        else:
            out = ffmpeg.output(streams, output_path)
        try:
            ffmpeg.run(out, overwrite_output=True, cmd=self.ffmpeg_cmd)
            logger.info(f"Render successful: {output_path}")
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"Render failed: {e}")
            raise