from ffmpeg_utils.ffmpeg_handler import FFmpeg
from files_util.file_handler import FileHandler
from urllib.parse import urlparse
from typing import Optional, Dict, List, Any, Union
import requests
import logging
import uuid
import os
import base64
import json
from .workflow_builder import WorkflowBuilder

logger = logging.getLogger(__name__)


def send_response(result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper function to send a response with proper error handling."""
    if not result:
        result = {}
    
    if result.get("error"):
        logger.error(f"Sending error response: {result['error']}")
        return {"error": result["error"]}
    
    logger.info(f"Sending response: {result}")
    return {"result": result}

def encode_to_base64(data: Dict[str, Any]) -> str:
    """Encode dictionary to base64 string."""
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()


def decode_from_base64(encoded_data: str) -> Dict[str, Any]:
    """Decode base64 string back to dictionary."""
    json_str = base64.b64decode(encoded_data.encode()).decode()
    return json.loads(json_str)


def process_input_stream(input_stream: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
    """Process input_stream - decode if base64 encoded, otherwise return as-is."""
    if isinstance(input_stream, str):
        # First check if it's a URL or file path
        parsed = urlparse(input_stream)
        if parsed.scheme in ("http", "https") or os.path.isfile(input_stream):
            # It's a raw URL or file path, return as-is
            logger.info(f"Processing raw URL/path: {input_stream}")
            return input_stream
        else:
            # It might be base64 encoded, try to decode
            try:
                # Try to decode as base64 - if successful, it's an encoded stream
                decoded = decode_from_base64(input_stream)
                logger.info(f"Successfully decoded base64 stream")
                return decoded
            except Exception as e:
                logger.error(f"Failed to decode as base64 and not a valid URL/path: {e}")
                # If decoding fails and it's not a valid URL/path, it's an error
                raise ValueError(f"Input stream is neither a valid URL/path nor base64 encoded: {input_stream}")
    else:
        # Already a dict, return as-is
        return input_stream


def send_action_response(result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Helper function to send a response with proper error handling and base64 encoding."""
    if not result:
        result = {}
    
    if result.get("error"):
        logger.error(f"Sending error response: {result['error']}")
        return {"error": result["error"]}
    
    logger.info(f"Sending response: {result}")
    encoded_result = encode_to_base64(result)
    return {"result_stream": encoded_result}


class MediaMCPHandler:
    """Handles media processing operations including downloading, validation, and rendering."""
    
    def __init__(self):
        """Initialize MediaMCPHandler with FFmpeg handler and file handler."""
        logger.info("Initializing MediaMCPHandler")
        
        self.ffmpeg_handler = FFmpeg()
        self.file_handler = FileHandler()
        self.local_files_cache: Dict[str, str] = {}
        self.workflow_builder = WorkflowBuilder()  
        
        logger.info("MediaMCPHandler initialized successfully")

    def _generate_output_filename(self, input_url: str, operation: str = "") -> str:
        """
        Generate a unique output filename with the same extension as the input.
        
        Args:
            input_url: The input URL or file path
            operation: Optional operation prefix for the filename
            
        Returns:
            Generated filename path in temp directory
        """
        _, ext = os.path.splitext(urlparse(input_url).path)
        if not ext:
            ext = ".mp4"  # Default extension if none found
        
        operation_prefix = f"{operation}_" if operation else ""
        filename = f"{operation_prefix}{uuid.uuid4()}{ext}"
        
        return os.path.realpath(os.path.join("/tmp", filename))

    def _validate_source(self, source: str) -> str:
        """
        Validate if the media source is accessible (URL or local file).
        
        Args:
            source: URL or file path to validate
            
        Returns:
            The validated URL/path
            
        Raises:
            ValueError: If URL/path is invalid or inaccessible
        """
        logger.info(f"Validating input: {source}")
        parsed = urlparse(source)
        
        if parsed.scheme in ("http", "https"):
            return self._validate_remote_url(source)
        elif os.path.isfile(source):
            logger.info(f"Local file validated: {source}")
            return source
        else:
            error_msg = "Input must be a valid HTTP/HTTPS URL or a local file path"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _validate_remote_url(self, url: str) -> str:
        """
        Validate remote URL accessibility.
        
        Args:
            url: Remote URL to validate
            
        Returns:
            The validated URL
            
        Raises:
            ValueError: If URL is not accessible
        """
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            if response.status_code >= 400:
                error_msg = f"URL is not reachable, status code: {response.status_code}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"URL validated successfully: {url}")
            return url
            
        except requests.RequestException as e:
            error_msg = f"URL validation failed: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _url_to_local(self, url: str) -> str:
        """
        Download a URL to a local file or return the path if already local.
        
        Args:
            url: URL or local path to process
            
        Returns:
            Local file path
            
        Raises:
            ValueError: If download fails or path is invalid
        """
        # Check cache first
        if url in self.local_files_cache:
            logger.info(f"Using cached local path for URL: {url}")
            return self.local_files_cache[url]
        
        parsed = urlparse(url)
        
        if parsed.scheme in ("http", "https"):
            return self._download_remote_url(url)
        elif os.path.isfile(url):
            logger.info(f"Input is already a local file: {url}")
            self.local_files_cache[url] = url
            return url
        else:
            error_msg = "Input must be a valid HTTP/HTTPS URL or a local file path"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _download_remote_url(self, url: str) -> str:
        """
        Download remote URL to local storage.
        
        Args:
            url: Remote URL to download
            
        Returns:
            Local file path
            
        Raises:
            ValueError: If download fails
        """
        logger.info(f"Downloading URL to local: {url}")
        self._validate_url(url)
        
        local_path = self.file_handler.download_url_to_local(url)
        if not local_path:
            error_msg = f"Failed to download URL: {url}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.local_files_cache[url] = local_path
        logger.info(f"Downloaded to local path: {local_path}")
        return local_path

    def get_media_info(self, input_source: str) -> Dict[str, Any]:
        """
        Get media information for the given input.
        
        Args:
            input_source: URL or local path to media file
            
        Returns:
            Media information dictionary
        """
        logger.info(f"Getting media info for: {input_source}")
        self._validate_source(input_source)
        
        # Convert to local path if needed
        parsed = urlparse(input_source)
        if parsed.scheme in ("http", "https"):
            local_path = self._url_to_local(input_source)
            return self.ffmpeg_handler.get_media_info(local_path)
        else:
            return self.ffmpeg_handler.get_media_info(input_source)

    def add_trim_action(self, start: int, duration: int, input_stream: Any) -> Dict[str, Any]:
        """
        Get trim action parameters.
        
        Args:
            start: Start time for trimming
            duration: Duration of the trim
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Trim action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_trim_action(start, duration, processed_stream)

    def add_cut_action(self, width: int, height: int, x: int, y: int, input_stream: Any) -> Dict[str, Any]:
        """
        Get cut/crop action parameters.
        
        Args:
            width: Width of the crop area
            height: Height of the crop area
            x: X offset for crop start (default: 0)
            y: Y offset for crop start (default: 0)
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Cut action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_cut_action(width, height, x, y, processed_stream)

    def add_change_volume_action(self, volume: float, input_stream: Any) -> Dict[str, Any]:
        """
        Get volume change action parameters.
        
        Args:
            volume: Volume multiplier (1.0 = no change, 0.5 = half volume, 2.0 = double volume)
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Volume change action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_change_volume_action(volume, processed_stream)

    def add_concat_action(self, input_stream: List[Any]) -> Dict[str, Any]:
        """
        Get concatenation action parameters.
        
        Args:
            input_stream: List of base64 encoded streams or input filenames
            
        Returns:
            Concatenation action dictionary
        """
        # Process each item in the list
        processed_streams = [process_input_stream(stream) for stream in input_stream]
        return self.workflow_builder.add_concat_action(processed_streams)

    def add_scale_action(self, width: int, height: int, input_stream: Any) -> Dict[str, Any]:
        """
        Get scale action parameters.
        
        Args:
            width: Target width in pixels
            height: Target height in pixels (-1 to maintain aspect ratio)
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Scale action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_scale_action(width, height, processed_stream)

    def add_fade_action(self, fade_type: str, start_time: float, duration: float, input_stream: Any) -> Dict[str, Any]:
        """
        Get fade action parameters.
        
        Args:
            fade_type: Type of fade ("in" or "out")
            start_time: When to start the fade (seconds)
            duration: Duration of the fade effect (seconds)
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Fade action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_fade_action(fade_type, start_time, duration, processed_stream)

    def add_rotate_action(self, angle: float, input_stream: Any) -> Dict[str, Any]:
        """
        Get rotate action parameters.
        
        Args:
            angle: Rotation angle in degrees (positive = clockwise)
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Rotate action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_rotate_action(angle, processed_stream)

    def add_speed_action(self, factor: float, input_stream: Any) -> Dict[str, Any]:
        """
        Get speed action parameters.
        
        Args:
            factor: Speed multiplier (2.0 = 2x faster, 0.5 = 2x slower)
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Speed action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_speed_action(factor, processed_stream)

    def add_blur_action(self, radius: int, input_stream: Any) -> Dict[str, Any]:
        """
        Get blur action parameters.
        
        Args:
            radius: Blur radius (higher = more blur)
            input_stream: Base64 encoded stream or input filename
            
        Returns:
            Blur action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_blur_action(radius, processed_stream)


    def add_crossfade_action(self, input_streams: List[Any], duration: float, stream1_duration: float, transition: str) -> Dict[str, Any]:
        """
        Get crossfade action parameters.
        
        Args:
            input_streams: List of exactly 2 base64 encoded streams or input filenames
            duration: Duration of the crossfade effect (seconds)
            stream1_duration: Duration of the first stream (required for calculating crossfade timing)
            transition: Transition type
            
        Returns:
            Crossfade action dictionary
        """
        processed_streams = [process_input_stream(stream) for stream in input_streams]
        return self.workflow_builder.add_crossfade_action(processed_streams, duration, stream1_duration, transition)

    def add_audio_mix_action(self, input_streams: List[Any], weights: str) -> Dict[str, Any]:
        """
        Get audio mix action parameters.
        
        Args:
            input_streams: List of base64 encoded streams or input filenames
            weights: Optional audio weights string
            
        Returns:
            Audio mix action dictionary
        """
        processed_streams = [process_input_stream(stream) for stream in input_streams]
        return self.workflow_builder.add_audio_mix_action(processed_streams, weights)

    def add_overlay_action(self, input_streams: List[Any], x: int = 0, y: int = 0) -> Dict[str, Any]:
        """
        Get overlay action parameters.
        
        Args:
            input_streams: List of exactly 2 base64 encoded streams or input filenames [base_video, overlay_video]
            x: Horizontal offset from left edge (default: 0)
            y: Vertical offset from top edge (default: 0)
            
        Returns:
            Overlay action dictionary
        """
        processed_streams = [process_input_stream(stream) for stream in input_streams]
        return self.workflow_builder.add_overlay_action(processed_streams, x, y)

    def add_set_fps_action(self, input_stream: Any, fps: float) -> Dict[str, Any]:
        """
        Get set FPS action parameters.
        
        Args:
            input_stream: Base64 encoded stream or input filename
            fps: Target frame rate
            
        Returns:
            Set FPS action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_set_fps_action(processed_stream, fps)

    def add_audio_resample_action(self, input_stream: Any, sample_rate: int) -> Dict[str, Any]:
        """
        Get audio resample action parameters.
        
        Args:
            input_stream: Base64 encoded stream or input filename
            sample_rate: Target sample rate (e.g., 44100, 48000)
            
        Returns:
            Audio resample action dictionary
        """
        processed_stream = process_input_stream(input_stream)
        return self.workflow_builder.add_audio_resample_action(processed_stream, sample_rate)

    def render_workflow(self, workflow: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Render a complex workflow with embedded URLs in leaf nodes.
        
        Args:
            workflow: Base64 encoded workflow or workflow dictionary with embedded URLs
            
        Returns:
            Workflow result dictionary with result_url if successful
        """
        logger.info(f"Rendering workflow")
        
        try:
            # Process workflow - decode if base64 encoded
            processed_workflow = process_input_stream(workflow)
            
            # Execute the workflow (FFmpeg handler will extract URLs from nodes)
            output_path = self.ffmpeg_handler.render_workflow(processed_workflow)
            
            logger.info(f"Workflow completed successfully, result path: {output_path}")
            return {"result_path": output_path}
            
        except Exception as e:
            logger.error(f"Error during workflow rendering: {str(e)}")
            return {"error": str(e)}