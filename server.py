from typing import List
from fastmcp import FastMCP
from media_mcp_handler.media_mcp import MediaMCPHandler
from media_mcp_handler.media_mcp import send_response, send_action_response

mcp = FastMCP("media-mcp")
media_handler = MediaMCPHandler()


@mcp.tool()
def get_media_info(input_address: str):
    """Get comprehensive media file information including duration, resolution, codecs, and format details.
    
    This is typically the first step before building a workflow to understand the input media properties.
    
    Args:
        input_address: URL (http/https) or local file path to the media file
        
    Returns:
        Media information including:
        - duration: Length of media in seconds
        - width/height: Video dimensions
        - video_codec/audio_codec: Encoding information
        - format: Container format details
        
    Example:
        info = get_media_info("https://example.com/video.mp4")
        # Use info to plan your workflow actions
    """
    results = media_handler.get_media_info(input_address)
    return send_response(result=results)


@mcp.tool()
def add_trim_action(input_stream: str, start: int, duration: int):
    """Create a trim action that cuts a portion from the timeline of a media stream.
    
    This builds an action that can be chained with other actions before final rendering.
    
    Args:
        input_stream: Previous action result or initial input (use input filename or url string for first action)
        start: Start time in integer seconds
        duration: Duration to keep in integer seconds
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
        
    Workflow Usage Example:
        1. Chain actions: result_stream = add_trim_action(input_stream, "30", "60")
        2. Continue chaining or render
    """
    result = media_handler.add_trim_action(input_stream=input_stream, start=start, duration=duration)
    return send_action_response(result)


@mcp.tool()
def add_cut_action(input_stream: str, width: int, height: int, x: int = 0, y: int = 0):
    """Create a crop action that extracts a rectangular region from video frames.
    
    This builds an action that can be chained with other actions before final rendering.
    
    Args:
        input_stream: Previous action result or initial input (use input filename string or url for first action)
        width: Width of the crop area in pixels
        height: Height of the crop area in pixels  
        x: Horizontal offset from left edge (default: 0)
        y: Vertical offset from top edge (default: 0)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
        
    Workflow Usage:
        1. Get video info first to know dimensions
        2. Chain crop: result_stream = add_cut_action(input_stream, 1280, 720, 100, 50)
        3. Continue chaining or render
    """
    result = media_handler.add_cut_action(input_stream=input_stream, width=width, height=height, x=x, y=y)
    return send_action_response(result)


@mcp.tool()
def add_change_volume_action(input_stream: str, volume: float):
    """Create a volume adjustment action that modifies audio levels.
    
    This builds an action that can be chained with other actions before final rendering.
    
    Args:
        input_stream: Previous action result or initial input (use input filename or url string for first action)
        volume: Volume multiplier (1.0 = no change, 0.5 = half volume, 2.0 = double volume, 0.0 = mute)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
        
    Workflow Usage:
        1. Adjust volume: result_stream = add_change_volume_action(input_stream, 1.5)
        2. Continue chaining or render
    """
    result = media_handler.add_change_volume_action(input_stream=input_stream, volume=volume)
    return send_action_response(result)


@mcp.tool()
def add_concat_action(input_streams: List[str]):
    """Create a concatenation action that joins multiple media streams sequentially.
    
    This builds an action that can be chained with other actions before final rendering.
    
    Args:
        input_streams: List of result_stream dicts or input filenames to concatenate in order
                      Example: [fresh_input_address_2, fresh_input_address_1] or [result_stream1, result_stream2]
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
        
    Workflow Usage:
        1. Prepare multiple inputs or result_streams
        2. Concatenate: result_stream = add_concat_action([rolling_stream_result, another_stream_result])
        3. Continue chaining or render
        
    Note: All inputs should have compatible formats (same resolution, codecs) for best results.
    """
    result = media_handler.add_concat_action(input_stream=input_streams)
    return send_action_response(result)


@mcp.tool()
def add_scale_action(input_stream: str, width: int, height: int = -1):
    """Create a scale action that resizes video dimensions.
    
    Args:
        input_stream: Previous action result or initial input
        width: Target width in pixels
        height: Target height in pixels (-1 to maintain aspect ratio)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
    """
    result = media_handler.add_scale_action(input_stream=input_stream, width=width, height=height)
    return send_action_response(result)


@mcp.tool()
def add_fade_action(input_stream: str, fade_type: str = "in", start_time: float = 0, duration: float = 1):
    """Create a fade action that adds fade in/out effects.

    Pay Attention: when you apply a fade-out followed by a fade-in, and the fade-in follows the fade-out on the timeline, the video becomes completely black. so never do that. its ok that the fade-in will come before the fade-out in timing.

    Args:
        input_stream: Previous action result or initial input
        fade_type: Type of fade ("in" or "out")
        start_time: When to start the fade (seconds)
        duration: Duration of the fade effect (seconds)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
    """
    result = media_handler.add_fade_action(input_stream=input_stream, fade_type=fade_type, start_time=start_time, duration=duration)
    return send_action_response(result)


@mcp.tool()
def add_rotate_action(input_stream: str, angle: float):
    """Create a rotate action that rotates video by specified degrees.
    
    Args:
        input_stream: Previous action result or initial input
        angle: Rotation angle in degrees (positive = clockwise)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
    """
    result = media_handler.add_rotate_action(input_stream=input_stream, angle=angle)
    return send_action_response(result)


@mcp.tool()
def add_speed_action(input_stream: str, factor: float):
    """Create a speed action that changes playback speed.
    
    Args:
        input_stream: Previous action result or initial input
        factor: Speed multiplier (2.0 = 2x faster, 0.5 = 2x slower)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
    """
    result = media_handler.add_speed_action(input_stream=input_stream, factor=factor)
    return send_action_response(result)


@mcp.tool()
def add_blur_action(input_stream: str, radius: int = 5):
    """Create a blur action that applies gaussian blur effect.
    
    Args:
        input_stream: Previous action result or initial input
        radius: Blur radius (higher = more blur)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
    """
    result = media_handler.add_blur_action(input_stream=input_stream, radius=radius)
    return send_action_response(result)




@mcp.tool()
def add_crossfade_action(input_streams: List[str], duration: float = 1.0, stream1_duration: float = None, transition: str = "fade"):
    """Create a crossfade action that smoothly transitions between two streams.
    
    Note- crossfade actions return fps 30 by default, so if you want to change the fps of the crossfade, you need to add a set fps action after this action.
    Args:
        input_streams: List of exactly 2 result_stream dicts or input filenames to crossfade
        duration: Duration of the crossfade effect (seconds)
        stream1_duration: Duration of the first stream (required for calculating crossfade timing)
        transition: Transition type (fade, wipeleft, wiperight, etc.)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
    """
    result = media_handler.add_crossfade_action(input_streams=input_streams, duration=duration, stream1_duration=stream1_duration, transition=transition)
    return send_action_response(result)


@mcp.tool()
def add_audio_mix_action(input_streams: List[str], weights: str = None):
    """Create an audio mix action that combines multiple audio streams.
    
    Args:
        input_streams: List of result_stream dicts or input filenames to mix
        weights: Optional audio weights (e.g., "0.5 0.3 0.2" for 3 streams)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
    """
    result = media_handler.add_audio_mix_action(input_streams=input_streams, weights=weights)
    return send_action_response(result)


@mcp.tool()
def add_overlay_action(input_streams: List[str], x: int = 0, y: int = 0):
    """Create an overlay action that places one video on top of another.
    
    Args:
        input_streams: List of exactly 2 result_stream dicts or input filenames [base_video, overlay_video]
        x: Horizontal offset from left edge (default: 0)
        y: Vertical offset from top edge (default: 0)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
        
    Workflow Usage:
        1. Prepare base video and overlay video (often scaled smaller)
        2. Overlay: result_stream = add_overlay_action([base_stream, overlay_stream], 10, 10)
        3. Continue chaining or render
    """
    result = media_handler.add_overlay_action(input_streams=input_streams, x=x, y=y)
    return send_action_response(result)


@mcp.tool()
def add_set_fps_action(input_stream: str, fps: float):
    """Create a set FPS action that normalizes video frame rate.
    
    Args:
        input_stream: Previous action result or initial input
        fps: Target frame rate (e.g., 24, 30, 60)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
        
    Usage:
        Useful for ensuring consistent frame rates before crossfade or other operations
    """
    result = media_handler.add_set_fps_action(input_stream=input_stream, fps=fps)
    return send_action_response(result)


@mcp.tool()
def add_audio_resample_action(input_stream: str, sample_rate: int):
    """Create an audio resample action that changes audio sample rate.
    
    Args:
        input_stream: Previous action result or initial input
        sample_rate: Target sample rate (44100, 48000, etc.)
        
    Returns:
        result_stream dict to pass to next action or to render_workflow
        
    Usage:
        Useful for normalizing audio before mixing or concatenation
    """
    result = media_handler.add_audio_resample_action(input_stream=input_stream, sample_rate=sample_rate)
    return send_action_response(result)


@mcp.tool()
def render_workflow(workflow: str):
    """Execute the final rendering of a complete workflow
    
    This is the final step that processes all chained actions and produces the output file.
    
    Args:
        workflow: Base64 encoded result_stream
        
    Returns:
        Result dict with 'result_path' containing the path to the rendered output file,
        or 'error' if rendering failed
        
    Complete Workflow Example:
        # 1. Get media info (optional but recommended)
        info = get_media_info("https://example.com/video.mp4")
        
        # 2. Build action chain
        stream1 = add_trim_action(rolling_stream_or_fresh_adress, 30, 10)  # Trim 30s-40s
        stream2 = add_cut_action(stream1, 1280, 720, 0, 0)          # Crop to 720p
        stream3 = add_change_volume_action(stream2, 1.5)            # Increase volume
        
        # 3. Render final result  
        result = render_workflow(stream3)
        # Output file available at result['result_path']
    """
    results = media_handler.render_workflow(workflow)
    return send_response(result=results)


if __name__ == "__main__":
    mcp.run(transport="stdio")