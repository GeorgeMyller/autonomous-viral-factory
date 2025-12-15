# Autonomous Viral Factory

🎬 **An AI-powered system that automatically creates viral video clips from YouTube trends.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agent%20Framework-orange.svg)](https://crewai.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)

## 🌟 Features

- **🔍 Trend Scout Agent**: Searches YouTube for trending videos in your niche
- **📝 Content Strategist Agent**: Analyzes transcripts to find the best 30-second clips
- **✂️ Video Editor Agent**: Downloads, clips, and adds subtitles automatically
- **🖥️ Streamlit UI**: User-friendly interface with Ollama model auto-detection
- **🤖 Multi-LLM Support**: Works with OpenAI, Google Gemini, and Ollama (local models)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Ollama](https://ollama.ai/) (for local LLMs - optional)
- FFmpeg (for video processing)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/autonomous-viral-factory.git
cd autonomous-viral-factory

# Install dependencies with uv
uv sync

# Copy environment template
cp .env.example .env
```

### Configure API Keys

Edit `.env` with your API keys:

```bash
# For OpenAI
OPENAI_API_KEY=your_openai_key

# For Google Gemini
GOOGLE_API_KEY=your_google_key

# For Ollama (local - no API key required)
OPENAI_API_BASE=http://localhost:11434/v1
```

### Run the App

**Option 1: Streamlit UI**
```bash
uv run streamlit run src/app.py
```

**Option 2: Command Line**
```bash
uv run src/autonomous_crew.py --provider ollama --model qwen3:14b --topic "Your Topic"
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  Viral Trend    │ ──▶ │    Content       │ ──▶ │   Autonomous      │
│    Scout        │     │   Strategist     │     │   Video Editor    │
└─────────────────┘     └──────────────────┘     └───────────────────┘
        │                       │                         │
        ▼                       ▼                         ▼
  YouTube Search         Transcript             Download + Clip
     (yt-dlp)             Analysis               + Subtitles
```

### Agents & Tools

| Agent | Tool | Description |
|-------|------|-------------|
| Viral Trend Scout | YouTube Trend Search | Uses yt-dlp to find trending videos |
| Content Strategist | YouTube Transcript Fetcher | Extracts and analyzes video transcripts |
| Video Editor | Video Downloader | Downloads videos from YouTube |
| Video Editor | Smart Video Clipper | Clips video segments with MoviePy |
| Video Editor | Auto Subtitler | Adds subtitles using Whisper |

## 📁 Project Structure

```
autonomous-viral-factory/
├── src/
│   ├── app.py                 # Streamlit web interface
│   ├── autonomous_crew.py     # CrewAI agents and tasks
│   └── tools/
│       ├── youtube_search.py  # YouTube trend search tool
│       ├── transcript_tool.py # Transcript fetcher tool
│       └── video_editor_tools.py # Video processing tools
├── downloads/                 # Downloaded videos
├── output/                    # Final processed clips
├── logs/                      # Execution logs
├── .env.example              # Environment template
└── pyproject.toml            # Python dependencies
```

## 🎯 Supported LLM Providers

| Provider | Models | Notes |
|----------|--------|-------|
| **OpenAI** | gpt-4o, gpt-4-turbo, gpt-3.5-turbo | Best tool-calling support |
| **Google Gemini** | gemini-2.0-flash | Good performance |
| **Ollama** | qwen3:14b, llama3, mistral | Local, private, free |

> **Tip**: For best results with Ollama, use `qwen3:14b` - it has better structured output.

## 🛠️ Troubleshooting

### YouTube IP Blocking
If downloads fail, the system automatically generates a fallback video. For real downloads, consider using a VPN or cookies.

### LLM Not Calling Tools
The system uses a hybrid approach where YouTube search is pre-fetched to ensure real data is used.

### Transcript Not Available
The Content Strategist will automatically try all video candidates and fall back to the highest-view video.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [CrewAI](https://crewai.com/) - AI Agent orchestration framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing in Python
- [Whisper](https://github.com/openai/whisper) - Speech recognition for subtitles
