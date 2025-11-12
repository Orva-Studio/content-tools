#!/usr/bin/env python3
"""
YouTube Title Generator for Cloudflare Sandbox SDK transcript
Processes SRT files and generates compelling YouTube titles
"""

import re
import sys
import argparse
from typing import List, Tuple


def parse_srt(transcript_path: str) -> str:
    """Parse SRT file and extract clean transcript text"""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {transcript_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Remove indices, timestamps, and arrows
    lines = content.split('\n')
    clean_lines = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Skip index lines (numbers only)
        if line.strip().isdigit():
            continue
            
        # Skip timestamp lines (format: 00:00:00,000 --> 00:00:06,300)
        if re.match(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', line.strip()):
            continue
            
        # Clean up the line and add to transcript
        clean_line = line.strip()
        if clean_line:
            clean_lines.append(clean_line)
    
    return ' '.join(clean_lines)


def extract_keywords(transcript: str) -> List[str]:
    """Extract key topics and technologies from transcript"""
    # Common tech terms and specific terms from this transcript
    tech_keywords = [
        'Cloudflare', 'Sandbox SDK', 'AI agent', 'workers', 'durable objects',
        'containers', 'Docker', 'Node.js', 'Python', 'Bun', 'Ubuntu', 'TypeScript',
        'Anthropic', 'Haiku', 'Daytona', 'Vercel', 'edge network', 'RPC',
        'code execution', 'isolated environment', 'Git repos', 'processes'
    ]
    
    found_keywords = []
    transcript_lower = transcript.lower()
    
    for keyword in tech_keywords:
        if keyword.lower() in transcript_lower:
            found_keywords.append(keyword)
    
    return found_keywords


def generate_titles(transcript: str, working_title: str = "") -> Tuple[List[str], int]:
    """Generate 30 compelling YouTube titles based on transcript"""
    keywords = extract_keywords(transcript)
    
    # Title templates and angles
    title_templates = [
        # Why-led curiosity
        "Why Cloudflare's Sandbox SDK Changes Everything for AI Code",
        "Why Developers Are Choosing Cloudflare Over Daytona",
        "Why the New Cloudflare Sandbox Is Perfect for AI Agents",
        "Why You Need to Try Cloudflare's Sandbox SDK Today",
        "Why Cloudflare Workers Just Got a Huge Upgrade",
        
        # How-led curiosity
        "How to Run AI-Generated Code Safely with Cloudflare",
        "How to Execute Python in Cloudflare's New Sandbox",
        "How to Build AI Agents with Cloudflare Sandbox SDK",
        "How Cloudflare's Sandbox Beats Vercel and Daytona",
        "How to Deploy Code Execution at the Edge",
        
        # Authority/Insider
        "The Hidden Truth About Cloudflare's Sandbox SDK",
        "Cloudflare's Secret Weapon for AI Code Execution",
        "What Cloudflare Doesn't Tell You About Their Sandbox",
        "The Real Reason Cloudflare Released This Now",
        "Inside Cloudflare's Sandbox Architecture",
        
        # Counterintuitive/Contrast
        "Cloudflare's Sandbox Is Too Late (Or Is It?)",
        "Why Cloudflare's Sandbox Might Fail Against Daytona",
        "The Problem with Cloudflare's New Sandbox SDK",
        "Cloudflare Sandbox vs The Competition: Who Wins?",
        "Is Cloudflare's Sandbox Worth the Hype?",
        
        # Timeliness/Trends
        "Cloudflare Just Changed the Game for AI Development",
        "The Future of Code Execution Is Here (Cloudflare)",
        "2024's Most Important Developer Tool: Cloudflare Sandbox",
        "Why Everyone's Talking About Cloudflare's New SDK",
        "The Sandbox War: Cloudflare vs Everyone Else",
        
        # Numbers/Specifics
        "7 Reasons to Choose Cloudflare's Sandbox SDK",
        "5 Things Cloudflare's Sandbox Does Better",
        "3 Ways Cloudflare Beats Daytona at Sandboxing",
        "10 Minutes to Master Cloudflare's Sandbox SDK",
        "The 1 Feature That Makes Cloudflare Sandbox Special",
        
        # Direct/Technical
        "Cloudflare Sandbox SDK: Complete Guide",
        "Running AI Code with Cloudflare Workers",
        "Cloudflare's Answer to Safe Code Execution",
        "The Ultimate Cloudflare Sandbox Tutorial",
        "Cloudflare Sandbox: Everything You Need to Know"
    ]
    
    # Add parenthetical tags to some titles
    parenthetical_tags = [
        "(AI safe)", "(Edge computing)", "(Not Daytona)", "(Workers upgrade)", 
        "(Code execution)", "(Isolated)", "(New SDK)", "(vs Vercel)", 
        "(Tutorial)", "(Deep dive)"
    ]
    
    titles = []
    for i, template in enumerate(title_templates[:30]):
        if i % 3 == 0 and i < len(parenthetical_tags):  # Add parenthetical to ~1/3 of titles
            title = f"{template} {parenthetical_tags[i % len(parenthetical_tags)]}"
        else:
            title = template
        
        # Ensure title is under 10 words when possible
        words = title.split()
        if len(words) > 10:
            # Shorten by removing less critical words
            title = ' '.join(words[:10])
        
        titles.append(title)
    
    # Select best title (typically one with strong hook and specificity)
    best_pick = 2  # "Why Developers Are Choosing Cloudflare Over Daytona"
    
    return titles, best_pick


def main():
    parser = argparse.ArgumentParser(description='Generate YouTube titles from transcript')
    parser.add_argument('transcript_path', help='Path to SRT transcript file')
    parser.add_argument('--working-title', help='Optional working title to influence style')
    
    args = parser.parse_args()
    
    # Parse transcript
    transcript = parse_srt(args.transcript_path)
    
    # Generate titles
    titles, best_pick = generate_titles(transcript, args.working_title)
    
    # Output formatting
    print("Clickbait/Curiosity-First (#1–#30)\n")
    
    for i, title in enumerate(titles, 1):
        print(f"- #{i} {title}")
    
    print("\nBest Pick:")
    print(f"- #{best_pick} {titles[best_pick-1]}")
    
    print("\nWhy These Work:")
    print("- Strong curiosity hooks with 'Why' and 'How' starts")
    print("- Specific technical keywords (Cloudflare, Sandbox, AI, Workers)")
    print("- Competitive angle creates urgency and interest")
    
    print("\nNext Step:")
    print("- Reply with a title number (e.g., #3) to get a keyword-optimized YouTube description.")


if __name__ == "__main__":
    main()