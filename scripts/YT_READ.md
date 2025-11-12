# YouTube Title Optimizer

A Python CLI tool that scores YouTube titles (0-100) similar to Vidiq's title scoring and suggests 3 improved titles for better
 SEO and engagement.

## Features

- **Rule-based Scoring**: Evaluates titles on length, power/emotional words, numbers/lists, questions, capitalization, uniquene
ss, and keyword placement.
- **Title Suggestions**: Generates 3 optimized title variations.
- **Optional AI Enhancement**: Uses OpenAI SDK for sentiment analysis to refine scoring and suggestions (requires API key).

## Installation

1. Ensure Python 3.x is installed.
2. (Optional) Install OpenAI SDK: `pip install openai`
3. Set environment variable for AI: `export OPENAI_API_KEY=your_key_here`

## Usage

Run the script from the command line:

```bash
python3 youtube_title_optimizer.py "Your YouTube Title"
```

For AI-enhanced analysis:

```bash
python3 youtube_title_optimizer.py --ai "Your YouTube Title"
```

### Output Example

```
Title: How to Bake a Cake
Score: 47/100

Suggestions:
1. Easy How to Bake a Cake (Score: 40)
2. Top 10 How to Bake a Cake (Score: 47)
```

## Scoring Factors

- **Length** (20%): Optimal 50-60 characters.
- **Power Words** (25%): Words like "amazing", "secret", "easy", etc.
- **Numbers/Lists** (15%): Digits or list formats.
- **Questions** (15%): Starts with "How", "What", etc.
- **Formatting** (10%): Title case preferred.
- **Uniqueness** (10%): Avoids clickbait phrases.
- **Keywords** (5%): Assumes front-loaded keywords.
- **AI Sentiment** (optional): Adjusts score based on emotional appeal.


## Notes

- AI mode requires OpenAI API key and internet connection.
- Suggestions are generated heuristically; AI mode improves them.
- For best results, provide titles with potential keywords.
