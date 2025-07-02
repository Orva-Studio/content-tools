# Content Tools

A collection of tools for content creation and processing, including audio processing automation and YouTube title generation.

## Tools

### Audio Processing (`scripts/clean_audio.py`)

Automated audio processing tool that integrates with Auphonic API to clean and enhance audio files.

**Features:**
- Upload audio files to Auphonic for professional audio processing
- Configurable presets for different audio enhancement needs
- Automatic download of processed files
- Real-time processing status monitoring
- Comprehensive error handling and logging

**Usage:**
```bash
python scripts/clean_audio.py <audio_file_path> [options]
```

**Options:**
- `--preset, -p`: Preset name to use (default: "Usual-2")
- `--output-dir, -o`: Output directory for processed files (default: "~/Downloads/auphonic_results")

**Requirements:**
- Python 3.x
- `requests` library
- Auphonic API key set as `AUPHONIC_API_KEY` environment variable

**Example:**
```bash
export AUPHONIC_API_KEY="your_api_key_here"
python scripts/clean_audio.py ~/audio/recording.wav --preset "Usual-2" --output-dir ~/processed_audio
```

### YouTube Title Generation (`titles/`)

Tools and templates for generating engaging YouTube video titles based on content analysis.

**Components:**
- `PROMPT.md`: Detailed guidelines for creating attention-grabbing YouTube titles
- `SOURCES.md`: List of source URLs for content analysis
- `PRIMED_SOURCES.md`: Processed content from sources ready for title generation

**Title Generation Guidelines:**
- Use attention-grabbing words ("No," "End," "Why," "How," "What," "Perfect")
- Include bold claims or exaggerations
- Focus on specific topics with broad appeal
- Incorporate numbers for structure and value
- Add emotional triggers
- Keep titles short and punchy (under 10 words)
- Tap into trending or controversial themes

## Setup

1. Clone the repository
2. Set up environment variables:
   ```bash
   export AUPHONIC_API_KEY="your_auphonic_api_key"
   ```
3. Install Python dependencies:
   ```bash
   pip install requests
   ```

## Project Structure

```
content-tools/
├── scripts/
│   └── clean_audio.py          # Audio processing automation
└── titles/
    ├── PROMPT.md               # Title generation guidelines
    ├── SOURCES.md              # Source URLs for content
    └── PRIMED_SOURCES.md       # Processed source content
```

## Contributing

Feel free to contribute by:
- Adding new content processing tools
- Improving existing scripts
- Adding new title generation templates
- Enhancing documentation

## License

This project is for personal/educational use.