# Clean Audio Script (Python)

This script uploads audio files to Auphonic for automatic audio processing and enhancement.

## Usage

Use `uv` to run the script with the required dependencies:

```bash
uv run --with requests ~/content-tools/scripts/clean_audio.py ~/Downloads/file.m4a --preset "Usual-2"
```

### Command Structure

```bash
uv run --with requests <script_path> <audio_file> [options]
```

### Arguments

- `<audio_file>` - Path to the audio file to process (required)

### Options

- `--preset <name>` or `-p <name>` - Preset name to use (default: "Usual-2")
- `--output-dir <path>` or `-o <path>` - Output directory for processed files (default: "~/Downloads/auphonic_results")

### Examples

```bash
# Basic usage with default preset
uv run --with requests ~/content-tools/scripts/clean_audio.py ~/Downloads/podcast.m4a

# Using a custom preset
uv run --with requests ~/content-tools/scripts/clean_audio.py ~/Downloads/interview.mp3 --preset "Podcast Enhancement"

# Custom output directory
uv run --with requests ~/content-tools/scripts/clean_audio.py ~/Downloads/audio.wav --output-dir ~/processed_audio

# All options together
uv run --with requests ~/content-tools/scripts/clean_audio.py ~/Downloads/recording.m4a --preset "Voice Only" --output-dir ~/clean_audio
```

## Dependencies

### Python Packages

The script requires the following Python packages (automatically installed by `uv` when using `--with`):

- **requests** - For HTTP API calls to Auphonic
- **argparse** - For command-line argument parsing (built-in)
- **os** - For file system operations (built-in)
- **time** - For delays and timeouts (built-in)

### Environment Variables

- **AUPHONIC_API_KEY** - Your Auphonic API key (required)

Set your API key in your shell profile:

```bash
export AUPHONIC_API_KEY="your-api-key-here"
```

## Prerequisites

1. **uv** - Python package manager (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)
2. **Auphonic account** - Sign up at [auphonic.com](https://auphonic.com)
3. **API key** - Generate from your Auphonic account settings

## What the Script Does

1. **Validates** the input audio file exists and is readable
2. **Looks up** the specified preset by name from your Auphonic account
3. **Uploads** the audio file and creates a new production
4. **Starts** the audio processing job
5. **Monitors** progress with status updates every 15 seconds
6. **Downloads** the processed files when complete
7. **Saves** results to the specified output directory

## Supported Audio Formats

Auphonic supports most common audio formats including:
- MP3
- M4A
- WAV
- FLAC
- OGG
- And many others

## Processing Time

Processing time varies based on:
- Audio file length
- Selected preset complexity
- Current Auphonic server load

The script will wait up to 5 minutes for processing to complete.

## Troubleshooting

### Common Issues

1. **"AUPHONIC_API_KEY environment variable is required"**
   - Set your API key: `export AUPHONIC_API_KEY="your-key"`

2. **"Preset not found"**
   - The script will list available presets
   - Check spelling and case sensitivity

3. **"Audio file does not exist"**
   - Verify the file path is correct
   - Use absolute paths or check current directory

4. **Processing timeout**
   - Large files may take longer than 5 minutes
   - Check status manually at the provided Auphonic URL

### Getting Help

```bash
uv run --with requests ~/content-tools/scripts/clean_audio.py --help
```

## Alternative: TypeScript Version

A TypeScript version using Bun is also available: `clean_audio.ts`

```bash
# Using the TypeScript version
./clean_audio.ts ~/Downloads/file.m4a --preset "Usual-2"
```
