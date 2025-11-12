#!/usr/bin/env python3
"""
YouTube Title Optimizer CLI Tool
Scores a given YouTube title (0-100) like Vidiq and suggests 3 better titles.
Optional AI sentiment analysis using OpenAI SDK.
"""

import argparse
import os
import re
import random
import sys

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Power words list
POWER_WORDS = [
    "amazing", "secret", "instant", "unbelievable", "proven", "exclusive",
    "urgent", "shocking", "easy", "free", "guaranteed", "limited", "now",
    "today", "immediately", "best", "worst", "how", "what", "why"
]

def score_title(title, use_ai=False):
    """
    Score the title from 0-100 based on various factors.
    """
    score = 0

    # Length (20%)
    length = len(title)
    if 50 <= length <= 60:
        score += 20
    elif 40 <= length < 50 or 60 < length <= 70:
        score += 15
    elif length < 40:
        score += 10
    # else 0

    # Power/Emotional Words (25%)
    words = title.lower().split()
    power_count = sum(1 for word in words if word in POWER_WORDS)
    score += min(power_count * 2.5, 25)  # up to 25 points

    # Numbers/Lists (15%)
    if re.search(r'\d+', title) or re.search(r'top \d+|best \d+|\d+ ways?|\d+ tips?', title.lower()):
        score += 15

    # Questions/Curiosity (15%)
    if title.startswith(('How', 'What', 'Why', 'When', 'Where')) or '?' in title:
        score += 15

    # Capitalization/Formatting (10%)
    if title.istitle() or (title.isupper() == False and not title.islower()):

   # Uniqueness/Harmony (10%)
    if not re.search(r'this will|you won\'t believe|shocking|amazing|unbelievable', title.lower(), re.IGNORECASE):
        score += 10

    # Keyword Placement (5%) - basic: assume first word is keyword
    if words and len(words[0]) > 3:
        score += 5

    # AI Sentiment (optional)
    if use_ai and OPENAI_AVAILABLE:
        try:
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO expert. Analyze the sentiment and emotional appeal of
the given title for clickability and engagement on a scale of 0-100. Respond only with a number."},
                    {"role": "user", "content": f"Title: {title}"}
                ],
                max_tokens=10
            )
            ai_score = int(response.choices[0].message.content.strip())
            score = (score + ai_score) / 2  # average with rule-based
        except Exception as e:
            print(f"AI scoring failed: {e}", file=sys.stderr)

    return min(int(score), 100)

def generate_suggestions(title, use_ai=False):
    """
    Generate 3 improved title suggestions.
    """
    suggestions = []
    base = title.lower()

    # Suggestion 1: Add power word if missing
    if not any(word in base for word in POWER_WORDS[:10]):  # first 10
        power = random.choice(POWER_WORDS[:10])
        new_title = f"{power.capitalize()} {title}"
        suggestions.append(new_title)

    # Suggestion 2: Make it a question
    if not title.startswith(('How', 'What', 'Why')):
        question_starters = ["How", "What", "Why"]
        starter = random.choice(question_starters)
        new_title = f"{starter} {title.lower()}"
        suggestions.append(new_title)

    # Suggestion 3: Add number
    if not re.search(r'\d+', title):
        num = random.randint(5, 10)
 45         new_title = f"Top {num} {title}"
 44         suggestions.append(new_title)
 43
 42     # If AI, refine suggestions
 41     if use_ai and OPENAI_AVAILABLE:
 40         try:
 39             client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
 38             prompt = f"Suggest 3 better YouTube titles based on this one: '{title}'. Make them optimized for SEO and engage
    ment. List them as 1. Title 2. Title 3. Title"
 37             response = client.chat.completions.create(
 36                 model="gpt-3.5-turbo",
 35                 messages=[{"role": "user", "content": prompt}],
 34                 max_tokens=150
 33             )
 32             ai_suggestions = response.choices[0].message.content.strip().split('\n')
 31             suggestions = [re.sub(r'^\d+\.\s*', '', s).strip() for s in ai_suggestions if s.strip()]
 30         except Exception as e:
 29             print(f"AI suggestions failed: {e}", file=sys.stderr)
 28
 27     return suggestions[:3]
 26
 25 def main():
 24     parser = argparse.ArgumentParser(description="Score and optimize YouTube titles.")
 23     parser.add_argument("title", help="The YouTube title to analyze")
 22     parser.add_argument("--ai", action="store_true", help="Enable AI sentiment analysis (requires OpenAI API key)")
 21     args = parser.parse_args()
 20
 19     if args.ai and not OPENAI_AVAILABLE:
 18         print("Error: OpenAI library not installed. Install with: pip install openai", file=sys.stderr)
 17         sys.exit(1)
 16
 15     if args.ai and not os.environ.get('OPENAI_API_KEY'):
 14         print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
 13         sys.exit(1)
 12
 11     score = score_title(args.title, args.ai)
 10     print(f"Title: {args.title}")
  9     print(f"Score: {score}/100")
  8
  7     suggestions = generate_suggestions(args.title, args.ai)
  6     print("\nSuggestions:")
  5     for i, sug in enumerate(suggestions, 1):
  4         sug_score = score_title(sug, args.ai)
  3         print(f"{i}. {sug} (Score: {sug_score})")
  2
  1 if __name__ == "__main__":
155     main()
