<div align="center">

# 🎬 Media MCP Editor

### *Powerful FFmpeg-powered media processing server with MCP integration*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Latest-green.svg)](https://ffmpeg.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
[![Tests](https://img.shields.io/badge/Tests-38%20Passing-brightgreen.svg)](#testing)

---

*Transform, edit, and process media files with ease using a comprehensive set of video and audio manipulation tools through a Model Context Protocol interface.*

</div>

## ✨ Features

### 📊 **Media Information & Analysis**
- 📋 **Media Info** - Comprehensive file analysis (duration, resolution, codecs, format, bitrate)

<table>
<tr>
<td width="50%">

### 🎥 **Video Operations**
- 🎬 **Trim** - Extract portions with precision timing
- ✂️ **Cut/Crop** - Resize and position video frames  
- 📏 **Scale** - Resize to any resolution
- 🔄 **Rotate** - Rotate by any angle
- 🌫️ **Blur** - Apply blur effects
- 🎭 **Fade** - Smooth fade in/out transitions
- ⚡ **Speed Control** - Change playback speed
- 🎞️ **FPS Control** - Frame rate adjustment

</td>
<td width="50%">

### 🎵 **Audio Operations**
- 🔊 **Volume Control** - Precise audio level adjustment
- 🎚️ **Audio Mixing** - Combine multiple audio streams
- 📡 **Resampling** - Change sample rates
- 🎼 **Audio Effects** - Professional audio processing

</td>
</tr>
</table>

---

## 🛠️ Quick Start

### 💻 Local Installation

```bash
# 📥 Clone the repository
git clone <repository-url>
cd media-mcp

# 📦 Install dependencies
pip install -e .

# 🛠️ Install FFmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows - Download from https://ffmpeg.org/download.html
```

---

## 🚀 Usage


### 🔗 **Connect to LLM Clients**

This MCP server can be integrated with various LLM clients that support the Model Context Protocol:

#### **Claude Desktop**
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "media-mcp": {
      "command": "/Users/yourusername/.local/bin/uv",
      "args": [
        "--directory",
        "/path/to/media-mcp-editor",
        "run",
        "server.py"
      ]
    }
  }
}
```

#### **Other MCP-Compatible Clients**
- **Connection**: Use stdio transport with the server command
- **Protocol**: Model Context Protocol (MCP)
- **Tools Available**: All media processing operations listed below

---

## 🎯 API Operations

### 📊 **Media Information**

| Operation | Description | Example |
|-----------|-------------|---------|
| `get_media_info` 📋 | Get comprehensive media details | `duration, resolution, codecs, format` |

### 🎬 **Basic Video Operations**

| Operation | Description | Example |
|-----------|-------------|---------|
| `trim` ✂️ | Extract media portion | `start: 0, duration: 30` |
| `cut` 📐 | Crop video dimensions | `width: 1280, height: 720, x: 0, y: 0` |
| `scale` 📏 | Resize video | `width: 1920, height: 1080` |
| `rotate` 🔄 | Rotate video | `angle: 90` (degrees) |
| `speed` ⚡ | Change playback speed | `factor: 2.0` (2x faster) |
| `blur` 🌫️ | Apply blur effect | `radius: 5` |
| `fade` 🎭 | Fade in/out | `type: "in", start: 0, duration: 2` |

### 🎵 **Audio Operations**

| Operation | Description | Example |
|-----------|-------------|---------|
| `change_volume` 🔊 | Adjust volume | `volume: 1.5` (50% louder) |
| `audio_mix` 🎚️ | Mix audio streams | `weights: "0.7,0.3"` |
| `audio_resample` 📡 | Change sample rate | `sample_rate: 48000` |

### 🔗 **Advanced Operations**

| Operation | Description | Use Case |
|-----------|-------------|----------|
| `concat` 🔗 | Join multiple videos | Create compilations |
| `crossfade` 🌅 | Smooth transitions between videos | Professional editing |
| `overlay` 🎭 | Layer videos with positioning | Picture-in-picture, watermarks |
| `set_fps` 🎞️ | Change frame rate | Optimize playback, standardize |

---

## 💡 Using Examples

*Showcasing MCP's natural language interface that generates JSON workflows*

### 📋 **Media Analysis**

**🗣️ User:** *"What are the technical details of my video file?"*

**🤖 Generated Workflow for Rendering:**
```json
{
  "tool": "get_media_info",
  "input_address": "video.mp4"
}
```

---

### 🎬 **Simple Video Editing**

**🗣️ User:** *"I need to trim the first 30 seconds from my video"*

**🤖 Generated Workflow for Rendering:**
```json
{
  "action": "trim",
  "params": {"start": 0, "duration": 30},
  "input": {"url": "input_video.mp4"}
}
```

---

### 🎞️ **Multi-Video Projects**

**🗣️ User:** *"Combine my intro, main content, and outro videos into one file"*

**🤖 Generated Workflow for Rendering:**
```json
{
  "action": "concat",
  "input": [
    {"url": "intro.mp4"},
    {"url": "main_content.mp4"},
    {"url": "outro.mp4"}
  ]
}
```

---

### 🔧 **Complex Workflow**

**🗣️ User:** *"Scale my video to 1080p, add a 2-second fade-in at the beginning, then trim it to 15 seconds starting from the 5-second mark"*

**🤖 Generated Workflow for Rendering:**
```json
{
  "action": "trim",
  "params": {"start": 5, "duration": 15},
  "input": {
    "action": "fade",
    "params": {"fade_type": "in", "start_time": 0, "duration": 2},
    "input": {
      "action": "scale",
      "params": {"width": 1920, "height": 1080},
      "input": {"url": "https://example.com/video.mp4"}
    }
  }
}
```

---

### 🎭 **Picture-in-Picture**

**🗣️ User:** *"Add a small overlay video in the top-right corner of my main video"*

**🤖 Generated Workflow for Rendering:**
```json
{
  "action": "overlay",
  "params": {"x": 50, "y": 50},
  "input": [
    {"url": "main_video.mp4"},
    {"url": "overlay_video.mp4"}
  ]
}
```

---

### 🌅 **Professional Transitions**

**🗣️ User:** *"Create a smooth 2-second crossfade transition between two 10-second video clips"*

**🤖 Generated Workflow for Rendering:**
```json
{
  "action": "crossfade",
  "params": {
    "duration": 2.0,
    "stream1_duration": 10.0,
    "transition": "fade"
  },
  "input": [
    {"url": "video1.mp4"},
    {"url": "video2.mp4"}
  ]
}
```

---

### 🎵 **Audio Processing**

**🗣️ User:** *"Make the audio 50% louder and change the sample rate to 48kHz"*

**🤖 Generated Workflow for Rendering:**
```json
{
  "action": "audio_resample",
  "params": {"sample_rate": 48000},
  "input": {
    "action": "change_volume",
    "params": {"volume": 1.5},
    "input": {"url": "audio_file.mp3"}
  }
}
```

---

## 🧪 Testing

*Comprehensive test suite with 38 passing tests!*

```bash
# 🧪 Run all tests
python -m pytest tests/ -v

# 🎯 Run specific test file
python -m pytest tests/test_media_mcp_handler.py -v

# 📊 Run with coverage
python -m pytest tests/ --cov=media_mcp_handler --cov=ffmpeg_utils
```

### 📈 **Test Coverage**
- ✅ **38 Tests Passing**
- 🎬 **Media Operations** - All video/audio functions
- 🔧 **Workflow Processing** - Complex pipeline testing
- 🌐 **URL Handling** - Remote file processing
- 📁 **File Management** - Local file operations
- ⚠️ **Error Handling** - Comprehensive error scenarios

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- 🐛 **Found a bug?** [Open an issue](https://github.com/your-username/media-mcp/issues)
- 💡 **Have a feature request?** [Start a discussion](https://github.com/your-username/media-mcp/discussions)
- 📧 **Need help?** Check our [documentation](https://github.com/your-username/media-mcp/wiki)

---

<div align="center">

### 🌟 **Star this project if you find it useful!** 🌟

*Built with ❤️ *

**[⬆️ Back to Top](#-media-mcp-handler)**

</div>
