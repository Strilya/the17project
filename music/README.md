# Background Music for Instagram Reels

This directory contains royalty-free spiritual/ambient background music for Instagram Reels.

## Overview

The video generator will automatically add background music at 25% volume to enhance the spiritual vibe of your content. Music is mixed with voiceovers using intelligent audio processing.

## How It Works

1. **Automatic Selection**: The system randomly selects a music file from this directory
2. **Style Matching**: Music files with style keywords in the filename (meditation, 432hz, ambient, spiritual) are prioritized
3. **Intelligent Looping**: Music is automatically looped/trimmed to match video duration (17 seconds)
4. **Volume Mixing**: Background music plays at 25% volume (configurable in `config/video_config.json`)

## Where to Get Free Spiritual Music

### Recommended FREE Sources (No Attribution Required)

1. **Pixabay** - https://pixabay.com/music/
   - Search: "meditation", "432hz", "ambient", "spiritual healing"
   - License: Pixabay License (Free for commercial use, no attribution)
   - Format: Download as MP3

2. **FreePD** - https://freepd.com
   - Search: "ambient", "meditation", "peaceful"
   - License: Public Domain
   - Format: Download as MP3

3. **Free Music Archive** - https://freemusicarchive.org
   - Filter by: "Ambient", "Meditation", "New Age"
   - License: Look for CC0 (Public Domain) or CC BY (requires attribution)
   - Format: Download as MP3

4. **YouTube Audio Library** - https://www.youtube.com/audiolibrary
   - Filter: "Ambient", "Focus", "Meditation"
   - License: Many tracks are free to use (check individual licenses)
   - Format: Download as MP3

### Recommended Search Terms

- "432hz meditation"
- "ambient spiritual"
- "healing frequency"
- "peaceful meditation"
- "cosmic ambient"
- "chakra meditation"
- "tibetan singing bowls"
- "purple frequency"

## File Naming Convention

For best results, include style keywords in filenames:

- `meditation_peaceful_waves.mp3`
- `432hz_healing_frequency.mp3`
- `ambient_space_cosmos.mp3`
- `spiritual_healing_light.mp3`

The system will match these keywords to video categories for better thematic alignment.

## How to Add Music

1. Download MP3 files from sources above
2. Place MP3 files in this `music/` directory
3. Optionally rename files to include style keywords
4. The system will automatically detect and use them

## Example Music Selection

Here are some specific tracks that work well (search on Pixabay or FreePD):

- "Celestial Meditation" - Cosmic, ethereal sounds
- "Deep Focus" - Minimal, peaceful ambient
- "Healing Frequencies 432Hz" - Spiritual healing vibes
- "Purple Nebula" - Space ambient sounds
- "Chakra Balancing" - Meditation tones

## Configuration

Edit `config/video_config.json` to adjust music settings:

```json
"background_music": {
  "enabled": true,          // Enable/disable music
  "volume": 0.25,           // Music volume (0.0 to 1.0)
  "music_dir": "music",     // This directory
  "styles": [               // Preferred styles (matched to filenames)
    "meditation",
    "432hz",
    "ambient_space",
    "spiritual_healing"
  ]
}
```

## Setup Instructions

### Option 1: Manual Download (Recommended)

1. **Download Music**: Get 3-5 ambient meditation tracks from free sources:
   - [Pixabay Music](https://pixabay.com/music/search/meditation/) - CC0, no attribution required
   - [Free Music Archive](https://freemusicarchive.org/search?quicksearch=meditation) - Various CC licenses
   - Search terms: "meditation", "432hz", "ambient", "spiritual healing"

2. **Add to Repository**:
   - Place MP3 files in this `music/` directory
   - For small files (<5MB each): Commit directly to git
   - For large files: Use [Git LFS](https://git-lfs.github.com/) or host externally

3. **Naming** (optional): Include keywords in filenames for better matching:
   - `432hz_healing_frequency.mp3`
   - `meditation_peaceful_flow.mp3`
   - `spiritual_ambient_space.mp3`

### Option 2: No Music (Voiceover Only)

The system works perfectly without background music! If no MP3 files are found, videos will be generated with:
- ✅ Voiceover narration only
- ✅ All visual elements (backgrounds, text, animations)
- ✅ Proper 17-second duration
- ✅ Complete video output

This is ideal for:
- Testing and development
- When you want pure voiceover content
- Avoiding music licensing concerns

## How the System Handles Music

- **Music Found**: Automatically mixes at 25% volume with voiceover
- **No Music Found**: Falls back gracefully to voiceover-only mode
- **No Errors**: Videos generate successfully either way

## Legal Notice

**IMPORTANT**: Ensure all music files you add comply with copyright laws and licensing requirements. Only use:
- Public domain music
- Creative Commons CC0 licensed music
- Music you have commercial rights to use

Never use copyrighted music without proper licensing, as this may result in Instagram takedowns or copyright strikes.

---

**Quick Start**: Download 3-5 ambient meditation tracks from Pixabay, drop them in this folder, and you're ready to go!
