# Content Tools

A comprehensive collection of tools for content creation and processing, including audio processing automation, virtual microphone delay, and YouTube title generation.

## Table of Contents

- [Quick Start](#quick-start)
- [Scripts](#scripts)
  - [Audio Processing (clean_audio.py)](#audio-processing-clean_audiopy)
  - [Virtual Microphone Delay (virtual_mic_delay.py)](#virtual-microphone-delay-virtual_mic_delaypy)
- [Prompts](#prompts)
  - [YouTube Title Generation](#youtube-title-generation)
- [Setup & Installation](#setup--installation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd content-tools
   ```

2. **Set environment variables** (using UPPERCASE as per convention)
   ```bash
   export AUPHONIC_API_KEY="your_auphonic_api_key"
   ```

3. **Install uv** (recommended Python package manager)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Start using tools immediately**
   ```bash
   # Audio processing
   uv run --with requests scripts/clean_audio.py ~/Downloads/audio.m4a
   
   # Virtual microphone with delay
   uv run --with "numpy,pyaudio" scripts/virtual_mic_delay.py --auto-detect
   ```

## Scripts

### Audio Processing (clean_audio.py)

**Purpose:** Automated audio processing tool that integrates with Auphonic API to clean and enhance audio files with professional-grade processing.

**Key Features:**
- Upload audio files to Auphonic for professional audio processing
- Configurable presets for different audio enhancement needs
- Automatic download of processed files
- Real-time processing status monitoring
- Comprehensive error handling and logging

**Usage:**
```bash
uv run --with requests scripts/clean_audio.py <audio_file> [options]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--preset, -p` | string | "Usual-2" | Preset name to use for processing |
| `--output-dir, -o` | path | "~/Downloads/auphonic_results" | Output directory for processed files |

**Requirements:**
- Auphonic API key (set as `AUPHONIC_API_KEY` environment variable)
- Python packages: `requests`

**Examples:**
```bash
# Basic usage with default preset
uv run --with requests scripts/clean_audio.py ~/Downloads/podcast.m4a

# Custom preset and output directory
uv run --with requests scripts/clean_audio.py ~/audio/interview.mp3 \
  --preset "Podcast Enhancement" \
  --output-dir ~/processed_audio

# Using environment variable for API key
export AUPHONIC_API_KEY="your_api_key_here"
uv run --with requests scripts/clean_audio.py ~/recordings/meeting.wav
```

**TypeScript Alternative:** A TypeScript version (`clean_audio.ts`) is also available for Bun runtime.

---

### Virtual Microphone Delay (virtual_mic_delay.py)

**Purpose:** Creates a virtual microphone with configurable audio delay, perfect for screen recording software like Camtasia when you need audio-video synchronization.

**Key Features:**
- Creates virtual microphone with delayed audio output
- Auto-detection of virtual audio devices
- Configurable delay timing (50-2000ms)
- High-quality audio processing with minimal CPU usage
- Real-time audio streaming with buffer management

**Usage:**
```bash
uv run --with "numpy,pyaudio" scripts/virtual_mic_delay.py [options]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-d, --delay` | int | 200 | Delay in milliseconds |
| `-r, --rate` | int | 44100 | Audio sample rate in Hz |
| `-b, --buffer` | int | 1024 | Audio buffer size |
| `-i, --input-device` | int | Default | Input device ID (physical microphone) |
| `-o, --output-device` | int | Required | Output device ID (virtual audio device) |
| `--list-devices` | flag | - | Show all available audio devices |
| `--auto-detect` | flag | - | Automatically find and use virtual audio devices |

**Constants (avoiding magic numbers):**
```python
STANDARD_DELAY = 200      # Standard screen recording delay
NETWORK_DELAY = 300       # For network streaming
MINIMAL_DELAY = 100       # Light processing delay
CD_QUALITY_RATE = 44100   # CD quality sample rate
PROFESSIONAL_RATE = 48000 # Professional audio rate
```

**Requirements:**
- macOS with audio permissions
- Virtual audio driver (BlackHole recommended)
- Python packages: `numpy`, `pyaudio`
- System: `portaudio` (install via `brew install portaudio`)

**Examples:**
```bash
# Quick start with auto-detection
uv run --with "numpy,pyaudio" scripts/virtual_mic_delay.py --auto-detect

# List available audio devices first
uv run --with "numpy,pyaudio" scripts/virtual_mic_delay.py --list-devices

# Custom setup for Camtasia recording
uv run --with "numpy,pyaudio" scripts/virtual_mic_delay.py \
  --input-device 4 \
  --output-device 8 \
  --delay 250

# High-quality audio settings
uv run --with "numpy,pyaudio" scripts/virtual_mic_delay.py \
  --rate 48000 \
  --buffer 512 \
  --delay 200 \
  --auto-detect
```

**Setup Prerequisites:**
```bash
# Install audio dependencies
brew install portaudio blackhole-2ch

# Verify installation
brew list | grep -E "(portaudio|blackhole)"
```

## Prompts

### YouTube Title Generation

**Location:** `prompts/YT_TITLES.md`

**Purpose:** AI prompt template for generating compelling, high-click YouTube titles that balance clarity, credibility, and curiosity based on video transcripts.

**Key Features:**
- Generates 30 unique title variations (#1-#30)
- Two categories: Clickbait/Curiosity-First and Under 60 Characters
- Keyword-optimized YouTube descriptions
- Chapter timestamp generation
- Multiple angle strategies (Why/How-led, Authority, Timeliness, etc.)

**Input Requirements:**
- `transcript_path`: Path to .srt or .txt transcript file
- `working_title` (optional): Draft title to influence style/angle

**Usage with AI CLI:**
```bash
# Basic usage
ai run prompts/YT_TITLES.md /path/to/video.srt

# With working title influence
ai run prompts/YT_TITLES.md /path/to/transcript.txt "working_title=My Draft Angle"
```

**Output Format:**
1. **30 numbered titles** in two categories
2. **Best Pick recommendation** with rationale
3. **Interactive description generation** (user selects title number)
4. **Chapter timestamps** for YouTube descriptions

**Title Principles:**
- Start with strong words: "Why", "How", "What", "The", "No", "End", "Perfect"
- Use specific yet broad appeal
- Include numbers when natural (5, 7, 10, 20)
- Add ethical emotion: "Easy", "Fast", "Trouble", "Perfect"
- Keep under 10 words for short category
- Optional parenthetical curiosity tags: "(RIP Claude Code)", "(Secret sauce)"

**Supported Formats:**
- `.srt` files (with timestamp parsing)
- `.txt` files (plain text transcripts)
- Auto-detects language and topic from content

## Setup & Installation

### Prerequisites

1. **Python 3.8+** (built-in on macOS or via Homebrew)
2. **UV Package Manager** (recommended)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Homebrew** (for audio dependencies)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

### Environment Variables

Set required environment variables (using UPPERCASE convention):

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, ~/.config/fish/config.fish)
export AUPHONIC_API_KEY="your_auphonic_api_key_here"
```

### Audio Dependencies (for virtual_mic_delay.py)

```bash
# Install audio system dependencies
brew install portaudio blackhole-2ch

# Verify installation
brew list | grep -E "(portaudio|blackhole)"
```

### Python Dependencies

Dependencies are automatically managed by `uv` when using `--with` flag:

```bash
# No manual installation needed - uv handles dependencies
uv run --with requests scripts/clean_audio.py --help
uv run --with "numpy,pyaudio" scripts/virtual_mic_delay.py --help
```

**Alternative: Traditional pip installation**
```bash
pip install requests numpy pyaudio
```

## Project Structure

```
content-tools/
├── .gitignore                  # Ignore .srt files, .claude/, .crush/
├── README.md                   # This comprehensive documentation
├── scripts/
│   ├── clean_audio.py          # Python: Auphonic audio processing
│   ├── clean_audio.ts          # TypeScript: Alternative Auphonic client
│   ├── clean_audio.md          # Detailed documentation for clean_audio
│   ├── virtual_mic_delay.py    # Python: Virtual microphone with delay
│   └── virtual_mic_delay.md    # Detailed documentation for virtual_mic_delay
└── prompts/
    └── YT_TITLES.md            # AI prompt for YouTube title generation
```

## Contributing

Contributions are welcome! When adding new tools:

1. **Follow coding standards:**
   - Use function declarations instead of function expressions
   - Keep functions short and focused (< 20 lines)
   - Maintain single level of abstraction per function
   - Use TypeScript instead of JavaScript; prefer interfaces over types
   - Return errors instead of panicking unless truly exceptional
   - Use UPPERCASE for environment variables
   - Avoid magic numbers; define constants using `const`
   - Prefix boolean variables with verbs: `is`, `has`, `can`, etc.

2. **Documentation requirements:**
   - Add comprehensive `.md` documentation for new scripts
   - Include usage examples and troubleshooting sections
   - Update this README with new tool information

3. **Testing:**
   - Test with `uv run --with <dependencies>` pattern
   - Verify environment variable handling
   - Include error handling examples

4. **File organization:**
   - Scripts go in `scripts/` directory
   - AI prompts go in `prompts/` directory
   - Documentation accompanies each script

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note:** Please respect the API terms of service for external services used by these tools (Auphonic, etc.). The MIT license applies to the code in this repository, not to third-party services.
