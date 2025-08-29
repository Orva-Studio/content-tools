# Virtual Microphone Audio Delay Tool

A Python tool that creates a virtual microphone with delayed audio, perfect for recording software like Camtasia when you need audio-video synchronization.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Usage Examples](#usage-examples)
- [Camtasia Integration](#camtasia-integration)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

## Overview

This tool creates a virtual microphone that:
- Takes audio input from your physical microphone
- Applies a configurable delay (default 200ms)
- Outputs the delayed audio to a virtual audio device
- Allows recording software to capture synchronized audio

**Perfect for**: Screen recording, live streaming, or any scenario where you need to synchronize audio with video that has inherent delay.

## Prerequisites

### System Requirements
- **macOS** (tested on macOS 12+)
- **Homebrew** package manager
- **Python 3.8+** (comes with macOS or via Homebrew)
- **UV** (optional but recommended for dependency management)

### Required Permissions
- **Microphone access** for input devices
- **Audio output access** for virtual devices

## Installation

### Step 1: Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Audio Dependencies

Install PortAudio (required for PyAudio):

```bash
brew install portaudio
```

### Step 3: Install Virtual Audio Device

Install BlackHole (free virtual audio driver):

```bash
brew install blackhole-2ch
```

**Alternative options:**
```bash
# For 16-channel version
brew install blackhole-16ch

# Or install VB-Cable manually from https://vb-audio.com/Cable/
```

### Step 4: Configure Audio Routing

1. Open **Audio MIDI Setup** (Applications → Utilities)
2. You should see "BlackHole 2ch" in the device list
3. Configure as needed for your recording setup

### Step 5: Verify Installation

Check that all dependencies are installed:

```bash
brew list | grep -E "(portaudio|blackhole)"
```

Expected output:
```
blackhole-2ch
portaudio
```

## Quick Start

### Option 1: Using UV (Recommended)

List available audio devices:
```bash
uv run --with "numpy,pyaudio" virtual_mic_delay.py --list-devices
```

Auto-detect and run:
```bash
uv run --with "numpy,pyaudio" virtual_mic_delay.py --auto-detect
```

### Option 2: Traditional pip installation

```bash
pip3 install numpy pyaudio
python3 virtual_mic_delay.py --list-devices
```

## Command Reference

### Core Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-d, --delay` | int | 200 | Delay in milliseconds |
| `-r, --rate` | int | 44100 | Audio sample rate in Hz |
| `-b, --buffer` | int | 1024 | Audio buffer size |
| `-i, --input-device` | int | Default | Input device ID (physical microphone) |
| `-o, --output-device` | int | Required | Output device ID (virtual audio device) |

### Utility Options

| Option | Description |
|--------|-------------|
| `--list-devices` | Show all available audio devices |
| `--auto-detect` | Automatically find and use virtual audio devices |
| `--help` | Show help message |

### Understanding Device List Output

When you run `--list-devices`, you'll see output like:
```
📋 Available audio devices:
============================================================
    0: DELL U2720Q (IN:0, OUT:2)
    1: WH-XB900N (IN:1, OUT:0)
🔊  8: BlackHole 2ch (IN:2, OUT:2) [VIRTUAL]
    9: MacBook Pro Microphone (IN:1, OUT:0)
============================================================
✅ Found virtual devices: [8]
💡 Use these device IDs for --output-device
```

**Key:**
- `IN:X` = Number of input channels (0 = no input capability)
- `OUT:Y` = Number of output channels (0 = no output capability)
- `[VIRTUAL]` = Detected virtual audio device

## Usage Examples

### Example 1: Basic Setup with Auto-Detection

```bash
uv run --with "numpy,pyaudio" virtual_mic_delay.py --auto-detect
```

This will:
- Automatically find virtual audio devices
- Use default microphone as input
- Apply 200ms delay
- Output to detected virtual device

### Example 2: Custom Delay for Video Sync

```bash
uv run --with "numpy,pyaudio" virtual_mic_delay.py \
  --input-device 4 \
  --output-device 8 \
  --delay 300
```

**Common delay values:**
- `200ms` - Standard for most screen recording
- `300ms` - Heavy processing or network streaming
- `100ms` - Light processing, minimal delay needed

### Example 3: High-Quality Audio Settings

```bash
uv run --with "numpy,pyaudio" virtual_mic_delay.py \
  --input-device 4 \
  --output-device 8 \
  --rate 48000 \
  --buffer 512 \
  --delay 200
```

**Audio quality settings:**
- Sample rate: `44100` (CD quality) or `48000` (professional)
- Buffer size: `512` (low latency) to `2048` (stable)

## Camtasia Integration

### Step 1: Start Virtual Microphone

```bash
uv run --with "numpy,pyaudio" virtual_mic_delay.py --auto-detect --delay 250
```

Keep this terminal window open during recording.

### Step 2: Configure Camtasia

1. Open **Camtasia**
2. Go to **Camtasia → Preferences → Audio**
3. Set **Microphone** to your virtual device (e.g., "BlackHole 2ch")
4. Test audio levels

### Step 3: Record

1. Start your virtual microphone script
2. Begin Camtasia recording
3. Audio will be automatically synchronized with the specified delay

### Step 4: Stop Recording

1. Stop Camtasia recording first
2. Press `Ctrl+C` in terminal to stop virtual microphone

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: pyaudio` | Install with `brew install portaudio` then reinstall pyaudio |
| `Device not found` | Run `--list-devices` to verify device IDs |
| `Permission denied` | Grant microphone access in System Settings → Security |
| `Audio stuttering` | Increase buffer size with `--buffer 2048` |
| `No virtual devices` | Install BlackHole: `brew install blackhole-2ch` |

### Error Messages

**"portaudio.h not found"**
```bash
brew install portaudio
# Then reinstall pyaudio
```

**"No suitable virtual audio device found"**
```bash
brew install blackhole-2ch
# Restart Audio MIDI Setup
```

**"Device busy or unavailable"**
- Close other audio applications
- Check Audio MIDI Setup for conflicts
- Try different device IDs

### Debugging Mode

Set environment variables for verbose output:

```bash
export AUDIO_DEBUG=1
uv run --with "numpy,pyaudio" virtual_mic_delay.py --auto-detect
```

## Technical Details

### How It Works

1. **Input**: Captures audio from physical microphone
2. **Buffer**: Stores audio samples in circular buffer
3. **Delay**: Applies time-based delay using buffer
4. **Output**: Streams delayed audio to virtual device
5. **Recording**: Software captures from virtual device

### Performance Characteristics

- **CPU Usage**: ~5-15% on modern Mac
- **Memory**: ~50-100MB for audio buffers
- **Latency**: Configurable (100-2000ms typical)

### Audio Quality

The tool preserves audio quality with:
- **Bit depth**: 32-bit float internal processing
- **Sample rates**: 44.1kHz, 48kHz, 96kHz supported
- **Channels**: Mono processing (stereo input averaged)

### Constants Definition

Following best practices, define commonly used values:

```python
# Common delay values (milliseconds)
STANDARD_DELAY = 200
NETWORK_DELAY = 300
MINIMAL_DELAY = 100

# Audio quality presets
CD_QUALITY_RATE = 44100
PROFESSIONAL_RATE = 48000
LOW_LATENCY_BUFFER = 512
STABLE_BUFFER = 1024
```

## Advanced Usage

### Creating Audio Routing Scripts

Create reusable configuration scripts:

```bash
#!/bin/bash
# screen-recording-setup.sh

# Define constants to avoid magic numbers
readonly YETI_MIC_DEVICE=4
readonly BLACKHOLE_DEVICE=8
readonly SYNC_DELAY=250
readonly SAMPLE_RATE=48000

echo "🎤 Starting virtual microphone for screen recording..."
uv run --with "numpy,pyaudio" virtual_mic_delay.py \
  --input-device $YETI_MIC_DEVICE \
  --output-device $BLACKHOLE_DEVICE \
  --delay $SYNC_DELAY \
  --rate $SAMPLE_RATE
```

### Environment Variables

Control behavior with environment variables:

```bash
export AUDIO_DEBUG=1              # Enable debug logging
export DEFAULT_DELAY=250          # Override default delay
export PREFERRED_SAMPLE_RATE=48000 # Set default sample rate
```

---

**💡 Pro Tip**: Always test your setup before important recordings. Run the virtual microphone, record a short test in Camtasia, and verify audio-video synchronization.

**🚨 Remember**: Keep the virtual microphone terminal window open during your entire recording session. Closing it will stop the audio feed to your recording software.
