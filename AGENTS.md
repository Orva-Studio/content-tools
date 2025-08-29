# Agent Guidelines

## Build/Lint/Test Commands
- **Run single test**: `python scripts/clean_audio.py --help` or `python scripts/virtual_mic_delay.py --help`
- **Check syntax**: `python -m py_compile scripts/*.py`
- **Install deps**: `pip install requests pyaudio numpy`

## Code Style
- **Python 3.x**, standard library first, then third-party imports
- **Naming**: snake_case for functions/variables, UPPER_CASE for constants
- **Error handling**: Use descriptive error messages with `exit_with_error()` pattern
- **CLI args**: Use `argparse` with descriptive help text
- **Formatting**: 4-space indentation, max 100 chars per line
- **Types**: Use type hints in function signatures when helpful
- **Comments**: Docstrings for functions, inline comments for complex logic
- **Environment**: Use `os.environ.get()` for API keys, never hardcode secrets