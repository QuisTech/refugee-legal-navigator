# Refugee Legal Navigator

An AI-powered voice assistant for refugee families to navigate asylum claims, legal resources, and case tracking.

## Project Structure

- `/src/models` - Core AI models for legal reasoning and document interpretation
- `/src/agents` - Specialized agents for case tracking, lawyer matching, and voice interaction
- `/src/utils` - Utility functions and Nova AI integrations
- `/data` - Example documents and user profiles for testing
- `/tests` - Unit tests
- `/scripts` - Demo scripts

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables
3. Run demo: `python run_voice_demo.py`

## Tech Stack

- Nova 2 Sonic: Voice-to-Text + Text-to-Voice
- Nova 2 Lite: Legal reasoning
- Nova Act: Automation for case tracking
- Embeddings: Document analysis
