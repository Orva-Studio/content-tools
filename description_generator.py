#!/usr/bin/env python3
"""
YouTube Description Generator for Cloudflare Sandbox SDK
Generates keyword-optimized descriptions based on selected title
"""

import re
import sys
from typing import List, Tuple


def parse_srt(transcript_path: str) -> str:
    """Parse SRT file and extract clean transcript text"""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {transcript_path} not found")
        sys.exit(1)
    
    lines = content.split('\n')
    clean_lines = []
    
    for line in lines:
        if not line.strip():
            continue
        if line.strip().isdigit():
            continue
        if re.match(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', line.strip()):
            continue
            
        clean_line = line.strip()
        if clean_line:
            clean_lines.append(clean_line)
    
    return ' '.join(clean_lines)


def extract_timestamps(transcript_path: str) -> List[Tuple[str, str]]:
    """Extract timestamps and content for chapter markers"""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return []
    
    lines = content.split('\n')
    timestamps = []
    current_content = ""
    current_time = ""
    
    for i, line in enumerate(lines):
        if re.match(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', line.strip()):
            # Extract start time
            start_time = line.strip().split(' --> ')[0]
            # Convert to MM:SS format
            time_parts = start_time.split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = int(time_parts[2].split(',')[0])
            
            if hours > 0:
                formatted_time = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                formatted_time = f"{minutes}:{seconds:02d}"
            
            # Save previous timestamp if exists
            if current_time and current_content:
                # Shorten content for chapter title
                words = current_content.split()[:8]  # First 8 words
                chapter_title = ' '.join(words).replace('.', '').replace(',', '')
                timestamps.append((current_time, chapter_title))
            
            current_time = formatted_time
            current_content = ""
            
        elif line.strip() and not line.strip().isdigit() and not re.match(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', line.strip()):
            current_content += line.strip() + " "
    
    # Add last timestamp
    if current_time and current_content:
        words = current_content.split()[:8]
        chapter_title = ' '.join(words).replace('.', '').replace(',', '')
        timestamps.append((current_time, chapter_title))
    
    return timestamps


def generate_description(title_number: int, transcript_path: str) -> str:
    """Generate keyword-optimized YouTube description"""
    
    # Parse transcript
    transcript = parse_srt(transcript_path)
    timestamps = extract_timestamps(transcript_path)
    
    # Title mapping to descriptions
    title_descriptions = {
        1: "Cloudflare's Sandbox SDK changes everything for AI code execution. This new tool lets developers run untested AI-generated code safely in isolated environments. Learn how it works with Workers, Durable Objects, and containers to execute Python, Node.js, and Bun code at the edge. Perfect for building AI agents that need to run code securely without risking your main systems.",
        
        2: "Developers are choosing Cloudflare over Daytona for sandboxed code execution. Cloudflare's Sandbox SDK integrates seamlessly with Workers and Durable Objects, offering longer run times and better edge performance. See how to execute AI-generated code, manage processes, and clone Git repos in isolated containers. Compare features, pricing, and performance to understand why Cloudflare wins for production workloads.",
        
        3: "The new Cloudflare Sandbox is perfect for AI agents that need to execute code safely. Learn how to build AI-powered applications that can run Python, JavaScript, and other code in secure containers. This tutorial shows the complete setup process, from installing the SDK to deploying AI agents that can write and execute code at the edge. Includes real examples with Anthropic's Haiku model.",
        
        4: "Try Cloudflare's Sandbox SDK today for safer AI code execution. This comprehensive guide shows you how to set up sandboxes, execute code in multiple languages, and integrate with existing Worker applications. Learn about the architecture, pricing, and deployment process. See real examples of running AI-generated code with proper error handling and output capture.",
        
        5: "Cloudflare Workers just got a huge upgrade with the Sandbox SDK. Now you can execute code, manage files, and run processes in isolated containers directly from your Workers. This changes everything for serverless applications that need more than just HTTP handling. Learn how to combine Workers with Durable Objects and containers for powerful edge computing solutions.",
        
        6: "Run AI-generated code safely with Cloudflare's new Sandbox SDK. This tool creates isolated environments where you can execute untrusted code without risking your systems. Perfect for AI applications, code playgrounds, and dynamic content generation. Learn the setup process, security features, and best practices for production deployment.",
        
        7: "Execute Python in Cloudflare's new Sandbox with this complete tutorial. The Sandbox SDK supports Python 3.11, Node.js, and Bun in Ubuntu containers. Learn how to set up the development environment, write code execution functions, and deploy to Workers. Includes error handling, output capture, and integration with AI models for dynamic code generation.",
        
        8: "Build AI agents with Cloudflare Sandbox SDK that can write and execute code. This advanced tutorial shows how to combine Anthropic's AI with Cloudflare's sandboxing capabilities. Create agents that can solve programming problems, test code, and provide real-time feedback. Learn about session management, file operations, and process control in isolated environments.",
        
        9: "Cloudflare's Sandbox beats Vercel and Daytona in several key areas. Compare features, pricing, run times, and integration capabilities. See real performance tests and use case scenarios. Understand why Cloudflare's edge network and Worker integration make it superior for production applications. Includes detailed feature comparison and deployment examples.",
        
        10: "Deploy code execution at the edge with Cloudflare's Sandbox SDK. This deep dive explores the architecture, performance characteristics, and use cases for edge-based code execution. Learn how to leverage Cloudflare's global network for low-latency code processing. See real examples of AI applications, code playgrounds, and dynamic content generation.",
        
        11: "The hidden truth about Cloudflare's Sandbox SDK reveals why it's different from other solutions. Learn about the unique architecture that combines Workers, Durable Objects, and containers. Discover the security features, performance optimizations, and integration capabilities that make it special. This insider look shows what Cloudflare isn't telling you about their sandboxing technology.",
        
        12: "Cloudflare's secret weapon for AI code execution is the Sandbox SDK. This tool enables safe execution of AI-generated code in isolated environments. Learn how it works, why it matters for AI applications, and how to implement it in your projects. See real examples of AI agents that can write, test, and execute code securely.",
        
        13: "What Cloudflare doesn't tell you about their Sandbox SDK could impact your development decisions. Learn about the limitations, requirements, and hidden costs. Understand the trade-offs compared to Daytona, Vercel, and other solutions. This honest review covers everything you need to know before choosing Cloudflare for your sandboxing needs.",
        
        14: "The real reason Cloudflare released the Sandbox SDK now reveals their strategy for the AI development market. Understand the timing, competitive landscape, and future roadmap. Learn how this fits into Cloudflare's broader vision for edge computing and serverless applications. This analysis shows the business and technical motivations behind the release.",
        
        15: "Inside Cloudflare's Sandbox architecture shows how Workers, Durable Objects, and containers work together. This technical deep dive explores the RPC communication, lifecycle management, and security isolation. Learn about the design decisions, performance optimizations, and scalability features. Perfect for developers who want to understand how it really works.",
        
        16: "Cloudflare's Sandbox might be too late to compete with established solutions like Daytona and Vercel. This critical analysis examines the timing, feature gaps, and market challenges. Learn why being late to market could hurt adoption, despite Cloudflare's strong ecosystem. Compare features, pricing, and developer experience to understand the competitive landscape.",
        
        17: "Cloudflare's Sandbox might fail against Daytona due to feature gaps and pricing differences. This honest comparison examines where Daytona excels and where Cloudflare falls short. Learn about Python SDK support, advanced features, and cost considerations. Understand the trade-offs before choosing your sandboxing solution.",
        
        18: "The problem with Cloudflare's new Sandbox SDK includes limitations, complexity, and integration challenges. This critical review covers the setup process, documentation gaps, and potential issues. Learn about the requirements, debugging challenges, and production considerations. Understand what works well and what needs improvement.",
        
        19: "Cloudflare Sandbox vs the competition: Who wins in the sandboxing wars? This comprehensive comparison tests features, performance, and developer experience. See side-by-side comparisons with Daytona, Vercel, and other solutions. Learn which use cases favor each platform and how to choose the right tool for your needs.",
        
        20: "Is Cloudflare's Sandbox worth the hype? This honest review examines the promises vs reality. Learn about the actual capabilities, limitations, and use cases. See real examples, performance tests, and cost analysis. Understand when to choose Cloudflare and when to look elsewhere for your sandboxing needs.",
        
        21: "Cloudflare just changed the game for AI development with the Sandbox SDK. This breakthrough enables safe code execution at the edge, perfect for AI applications. Learn how this transforms what's possible with serverless AI agents, code generation tools, and dynamic content creation. See real examples of next-generation AI applications.",
        
        22: "The future of code execution is here with Cloudflare's Sandbox SDK. This revolutionary tool enables secure, isolated code execution at the edge. Learn how it transforms serverless applications, AI development, and dynamic content generation. See the architecture, use cases, and future roadmap that's shaping the next generation of web applications.",
        
        23: "2024's most important developer tool is Cloudflare's Sandbox SDK. This game-changing technology enables safe code execution in serverless environments. Learn why it matters for AI development, testing, and dynamic applications. See real examples, performance benchmarks, and integration possibilities that make it essential for modern development.",
        
        24: "Why everyone's talking about Cloudflare's new Sandbox SDK and its impact on AI development. This comprehensive overview covers the features, benefits, and use cases that have developers excited. Learn about the architecture, integration possibilities, and competitive advantages. See real examples of what makes this tool revolutionary.",
        
        25: "The Sandbox war: Cloudflare vs everyone else in the battle for code execution dominance. This analysis covers the competitive landscape, feature comparisons, and market dynamics. Learn how Cloudflare's approach differs from Daytona, Vercel, and other solutions. Understand the strategic implications for developers and the future of serverless computing.",
        
        26: "7 reasons to choose Cloudflare's Sandbox SDK over competing solutions. This detailed analysis covers integration with Workers, edge performance, run time limits, security features, pricing, developer experience, and future roadmap. Learn why these factors make Cloudflare the superior choice for many use cases.",
        
        27: "5 things Cloudflare's Sandbox does better than other sandboxing solutions. This comparison highlights the unique advantages of Cloudflare's approach, including edge performance, Worker integration, security model, scalability, and ecosystem benefits. See real examples that demonstrate these advantages in action.",
        
        28: "3 ways Cloudflare beats Daytona at sandboxing despite being newer to the market. This focused analysis examines the key advantages: edge network performance, Worker ecosystem integration, and longer run times. Learn why these factors matter for production applications and how they translate to better user experiences.",
        
        29: "10 minutes to master Cloudflare's Sandbox SDK with this quick tutorial. Learn the basics of setup, code execution, and deployment. See real examples of running Python, JavaScript, and other code in isolated containers. Perfect for developers who want to get started quickly with this powerful new tool.",
        
        30: "The 1 feature that makes Cloudflare Sandbox special is its seamless integration with Workers and Durable Objects. This unique combination enables powerful serverless applications that can execute code safely. Learn how this integration works, why it matters, and how to leverage it for your projects. See real examples of what's possible only with Cloudflare."
    }
    
    # Get the description for the selected title
    description = title_descriptions.get(title_number, "Learn about Cloudflare's Sandbox SDK and how it enables safe code execution for AI applications. This comprehensive guide covers setup, implementation, and best practices for running code in isolated environments at the edge.")
    
    # Add timestamps
    if timestamps:
        description += "\n\n📌 Chapters:"
        for time, title in timestamps[:15]:  # Limit to first 15 chapters
            description += f"\n{time} {title}"
    
    return description


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 description_generator.py <title_number> <transcript_path>")
        sys.exit(1)
    
    try:
        title_number = int(sys.argv[1])
    except ValueError:
        print("Error: Title number must be an integer")
        sys.exit(1)
    
    transcript_path = sys.argv[2]
    
    if title_number < 1 or title_number > 30:
        print("Error: Title number must be between 1 and 30")
        sys.exit(1)
    
    description = generate_description(title_number, transcript_path)
    print(description)


if __name__ == "__main__":
    main()