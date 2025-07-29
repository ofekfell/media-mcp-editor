from typing import Any, Dict, List

class WorkflowBuilder:
    """
    Builds workflow steps by chaining actions. Each method corresponds to an available action.
    """        
    def add_trim_action(self, start: str, duration: str, input_stream: List[Any]) -> Dict[str, Any]:
        #TODO: VERIFY START+ DURATION <= INPUT DURATION
        if start< 0 or duration <= 0:
            raise ValueError("Start time must be >= 0 and duration must be > 0")
        
        return self._build_item(action="trim", input_stream=input_stream, start=start, duration=duration)

    def add_cut_action(self, width: int, height: int, x: int, y: int, input_stream: List[Any]) -> Dict[str, Any]:
        #TODO: VERIFY x+WIDTH,y+HEIGHT <= INPUT WIDTH, HEIGHT
        if x <= 0 or y <= 0 or width <= 0 or height <= 0:
            raise ValueError("x ,y ,width and height must be greater than 0")
        return self._build_item(action="cut", input_stream=input_stream, width=width, height=height, x=x, y=y)

    def add_change_volume_action(self, volume: float, input_stream: List[Any]) -> Dict[str, Any]:
        # always above 0.0, so no need to check
        if volume < 0.0:
            raise ValueError("Volume must be greater than or equal to 0.0")
        
        return self._build_item(action="change_volume", input_stream=input_stream, volume=volume)

    def add_concat_action(self, input_stream: List[Any]) -> Dict[str, Any]:
        if len(input_stream) < 2:
            raise ValueError("Concat action requires at least two inputs")
        
        return self._build_item(action="concat", input_stream=input_stream)

    def add_scale_action(self, width: int, height: int, input_stream: List[Any]) -> Dict[str, Any]:
        if width <= 0:
            raise ValueError("Width must be greater than 0")
        
        return self._build_item(action="scale", input_stream=input_stream, width=width, height=height)

    def add_fade_action(self, fade_type: str, start_time: float, duration: float, input_stream: List[Any]) -> Dict[str, Any]:
        if fade_type not in ["in", "out"]:
            raise ValueError("Fade type must be 'in' or 'out'")
        if duration <= 0:
            raise ValueError("Duration must be greater than 0")
        
        return self._build_item(action="fade", input_stream=input_stream, type=fade_type, start_time=start_time, duration=duration)

    def add_rotate_action(self, angle: float, input_stream: List[Any]) -> Dict[str, Any]:
        return self._build_item(action="rotate", input_stream=input_stream, angle=angle)

    def add_speed_action(self, factor: float, input_stream: List[Any]) -> Dict[str, Any]:
        if factor <= 0:
            raise ValueError("Speed factor must be greater than 0")
        
        return self._build_item(action="speed", input_stream=input_stream, factor=factor)

    def add_blur_action(self, radius: int, input_stream: List[Any]) -> Dict[str, Any]:
        if radius <= 0:
            raise ValueError("Blur radius must be greater than 0")
        
        return self._build_item(action="blur", input_stream=input_stream, radius=radius)


    def add_crossfade_action(self, input_streams: List[Any], duration: float, stream1_duration: float, transition: str) -> Dict[str, Any]:
        if len(input_streams) != 2:
            raise ValueError("Crossfade action requires exactly 2 inputs")
        if duration <= 0:
            raise ValueError("Duration must be greater than 0")
        if stream1_duration is None or stream1_duration <= 0:
            raise ValueError("stream1_duration must be provided and greater than 0")
        
        return self._build_item(action="crossfade", input_stream=input_streams, duration=duration, stream1_duration=stream1_duration, transition=transition)

    def add_audio_mix_action(self, input_streams: List[Any], weights: str) -> Dict[str, Any]:
        if len(input_streams) < 2:
            raise ValueError("Audio mix action requires at least 2 inputs")
        
        return self._build_item(action="audio_mix", input_stream=input_streams, weights=weights)

    def add_overlay_action(self, input_streams: List[Any], x: int, y: int) -> Dict[str, Any]:
        if len(input_streams) != 2:
            raise ValueError("Overlay action requires exactly 2 inputs")
        
        return self._build_item(action="overlay", input_stream=input_streams, x=x, y=y)

    def add_set_fps_action(self, input_stream: Any, fps: float) -> Dict[str, Any]:
        return self._build_item(action="set_fps", input_stream=input_stream, fps=fps)

    def add_audio_resample_action(self, input_stream: Any, sample_rate: int) -> Dict[str, Any]:
        return self._build_item(action="audio_resample", input_stream=input_stream, sample_rate=sample_rate)

    def _build_item(self, action: str, input_stream: Any, **kwargs) -> Dict[str, Any]:
        # Handle different input types
        if isinstance(input_stream, str):
            # Direct URL/path - wrap in leaf node structure
            input_node = {"url": input_stream}
        elif isinstance(input_stream, dict) and "url" in input_stream:
            # Already a leaf node with URL
            input_node = input_stream
        elif isinstance(input_stream, dict):
            # Workflow node - use as-is
            input_node = input_stream
        elif isinstance(input_stream, list):
            # List of inputs (for concat) - process each
            input_node = []
            for inp in input_stream:
                if isinstance(inp, str):
                    input_node.append({"url": inp})
                else:
                    input_node.append(inp)
        else:
            input_node = input_stream
            
        item = {
            'action': action,
            'input': input_node  # Note: changed from 'inputs' to 'input' for consistency
        }
        item.update(kwargs)
        return item
