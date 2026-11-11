# Autonomous Viral Factory

🎬 **An AI-powered system that automatically creates viral video clips from YouTube trends.**

🎬 **Um sistema alimentado por IA que cria automaticamente clipes virais de vídeos do YouTube.**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agent%20Framework-orange.svg)](https://crewai.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)

---

<details>
<summary>🇧🇷 <b>Documentação em Português</b></summary>

## 🌟 Funcionalidades

- **🔍 Agente Scout de Tendências**: Busca vídeos em alta no YouTube no seu nicho
- **🧠 Analista de Momentos Virais**: Usa Whisper + IA para identificar os TOP 3 momentos mais virais
- **✂️ Agente Editor de Vídeo**: Baixa, corta e adiciona legendas automaticamente
- **📊 Geração Multi-Clips**: Cria clipes separados para TODOS os momentos virais identificados
- **🖥️ Interface Streamlit**: Interface amigável com auto-detecção de modelos Ollama
- **🤖 Suporte Multi-LLM**: Funciona com OpenAI, Google Gemini e Ollama (modelos locais)

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes Python)
- [Ollama](https://ollama.ai/) (para LLMs locais - opcional)
- FFmpeg (para processamento de vídeo)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/GeorgeMyller/autonomous-viral-factory.git
cd autonomous-viral-factory

# Instale as dependências com uv
uv sync

# Copie o template de ambiente
cp .env.example .env
```

### Configure as Chaves de API

Edite o arquivo `.env` com suas chaves:

```bash
# Para OpenAI
OPENAI_API_KEY=sua_chave_openai

# Para Google Gemini
GOOGLE_API_KEY=sua_chave_google

# Para Ollama (local - não precisa de chave)
OPENAI_API_BASE=http://localhost:11434/v1
```

### Execute o App

**Opção 1: Interface Streamlit**
```bash
uv run streamlit run src/app.py
```

**Opção 2: Linha de Comando**
```bash
uv run src/autonomous_crew.py --provider ollama --model qwen3:14b --topic "Seu Tópico"
```

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  Scout de       │ ──▶ │   Download do    │ ──▶ │  Analista de     │ ──▶ │   Editor de Vídeo │
│  Tendências     │     │   Vídeo          │     │  Momentos Virais │     │   (Corte+Legenda) │
└─────────────────┘     └──────────────────┘     └──────────────────┘     └───────────────────┘
         │                       │                         │                         │
         ▼                       ▼                         ▼                         ▼
   Busca YouTube            yt-dlp               Whisper + LLM               MoviePy + FFmpeg
                                                (TOP 3 momentos)             (Múltiplos Clipes!)
```

### Agentes & Ferramentas

| Agente | Ferramenta | Descrição |
|--------|------------|-----------|
| Scout de Tendências | YouTube Trend Search | Usa yt-dlp para encontrar vídeos em alta |
| Editor de Vídeo | Video Downloader | Baixa vídeos do YouTube |
| **Analista de Momentos Virais** | **Viral Moment Analyzer** | **Transcrição com Whisper + análise IA para encontrar TOP 3 momentos virais** |
| Editor de Vídeo | Smart Video Clipper | Corta segmentos de vídeo com MoviePy |
| Editor de Vídeo | Auto Subtitler | Adiciona legendas usando Whisper + FFmpeg |

## 🔄 Pipeline de Processamento

1. **Scout**: Busca vídeos em alta no YouTube sobre seu tópico
2. **Download**: Baixa o melhor vídeo candidato
3. **Análise**: 
   - Transcreve o vídeo com OpenAI Whisper (local)
   - IA analisa a transcrição para identificar **TOP 3 momentos virais**
   - Retorna timestamps precisos para cada momento
4. **Criação de Clipes**: Para **CADA** momento viral:
   - Corta o vídeo nos timestamps identificados
   - Adiciona legendas no clipe
   - Salva na pasta `output/`
5. **Exibição**: Interface mostra todos os clipes gerados com botões de download individuais

## 📁 Estrutura do Projeto

```
autonomous-viral-factory/
├── src/
│   ├── app.py                 # Interface web Streamlit
│   ├── autonomous_crew.py     # Agentes e tarefas CrewAI (pipeline de 4 tarefas)
│   └── tools/
│       ├── youtube_search.py      # Ferramenta de busca de tendências YouTube
│       ├── transcript_tool.py     # Ferramenta de busca de transcrições
│       ├── video_editor_tools.py  # Ferramentas de processamento de vídeo
│       └── viral_moment_tool.py   # Analisador de momentos virais Whisper + IA
├── downloads/                 # Vídeos baixados + arquivos SRT
├── output/                    # Clipes processados (múltiplos por execução!)
├── logs/                      # Logs de execução
├── .env.example               # Template de ambiente
└── pyproject.toml             # Dependências Python
```

## 🎯 Provedores LLM Suportados

| Provedor | Modelos | Notas |
|----------|---------|-------|
| **OpenAI** | gpt-4o, gpt-4-turbo | Melhor suporte para tool-calling |
| **Google Gemini** | gemini-2.0-flash | Bom desempenho |
| **Ollama** | qwen3:14b, llama3, mistral | Local, privado, grátis! |

> **Dica**: Para melhores resultados com Ollama, use `qwen3:14b` ou modelos maiores - eles produzem melhores análises de momentos virais.

## 🛠️ Solução de Problemas

### Bloqueio de IP do YouTube
Se os downloads falharem, o sistema gera automaticamente um vídeo de fallback. Para downloads reais, considere usar VPN ou cookies.

### Transcrição Whisper Lenta
A primeira execução baixa o modelo Whisper `base` (~150MB). Execuções subsequentes são mais rápidas. Para velocidade, certifique-se de ter uma GPU disponível.

### Nenhum Clipe Gerado
Verifique a pasta `logs/` para detalhes da execução. Problemas comuns:
- Análise de transcrição retornando timestamps inválidos
- Vídeo muito curto para múltiplos clipes

### LLM Não Retornando JSON Válido
Para usuários do Ollama, certifique-se de usar um modelo capaz como `qwen3:14b`. Modelos menores podem ter dificuldade com saída JSON.

</details>

---

<details open>
<summary>🇺🇸 <b>English Documentation</b></summary>

## 🌟 Features

- **🔍 Trend Scout Agent**: Searches YouTube for trending videos in your niche
- **🧠 Viral Moment Analyst**: Uses Whisper + AI to identify the TOP 3 most viral moments
- **✂️ Video Editor Agent**: Downloads, clips, and burns subtitles automatically
- **📊 Multi-Clip Generation**: Creates separate clips for ALL identified viral moments
- **🖥️ Streamlit UI**: User-friendly interface with Ollama model auto-detection
- **🤖 Multi-LLM Support**: Works with OpenAI, Google Gemini, and Ollama (local models)

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Ollama](https://ollama.ai/) (for local LLMs - optional)
- FFmpeg (for video processing)

### Installation

```bash
# Clone the repository
git clone https://github.com/GeorgeMyller/autonomous-viral-factory.git
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
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  Viral Trend    │ ──▶ │   Video          │ ──▶ │  Viral Moment    │ ──▶ │   Video Editor    │
│    Scout        │     │   Download       │     │   Analyst        │     │   (Clip+Caption)  │
└─────────────────┘     └──────────────────┘     └──────────────────┘     └───────────────────┘
         │                       │                         │                         │
         ▼                       ▼                         ▼                         ▼
   YouTube Search          yt-dlp               Whisper + LLM               MoviePy + FFmpeg
                                                (TOP 3 moments)             (Multiple Clips!)
```

### Agents & Tools

| Agent | Tool | Description |
|-------|------|-------------|
| Viral Trend Scout | YouTube Trend Search | Uses yt-dlp to find trending videos |
| Video Editor | Video Downloader | Downloads videos from YouTube |
| **Viral Moment Analyst** | **Viral Moment Analyzer** | **Whisper transcription + AI analysis to find TOP 3 viral moments** |
| Video Editor | Smart Video Clipper | Clips video segments with MoviePy |
| Video Editor | Auto Subtitler | Burns subtitles using Whisper + FFmpeg |

## 🔄 Processing Pipeline

1. **Scout**: Searches YouTube for trending videos on your topic
2. **Download**: Downloads the best candidate video
3. **Analyze**: 
   - Transcribes video with OpenAI Whisper (local)
   - AI analyzes transcript to identify **TOP 3 viral moments**
   - Returns precise timestamps for each moment
4. **Create Clips**: For **EACH** viral moment:
   - Clips the video at the identified timestamps
   - Burns subtitles into the clip
   - Saves to `output/` folder
5. **Display**: UI shows all generated clips with individual download buttons

## 📁 Project Structure

```
autonomous-viral-factory/
├── src/
│   ├── app.py                 # Streamlit web interface
│   ├── autonomous_crew.py     # CrewAI agents and tasks (4-task pipeline)
│   └── tools/
│       ├── youtube_search.py      # YouTube trend search tool
│       ├── transcript_tool.py     # Transcript fetcher tool
│       ├── video_editor_tools.py  # Video processing tools
│       └── viral_moment_tool.py   # Whisper + AI viral moment analyzer
├── downloads/                 # Downloaded videos + SRT files
├── output/                    # Final processed clips (multiple per run!)
├── logs/                      # Execution logs
├── .env.example               # Environment template
└── pyproject.toml             # Python dependencies
```

## 🎯 Supported LLM Providers

| Provider | Models | Notes |
|----------|--------|-------|
| **OpenAI** | gpt-4o, gpt-4-turbo | Best tool-calling support |
| **Google Gemini** | gemini-2.0-flash | Good performance |
| **Ollama** | qwen3:14b, llama3, mistral | Local, private, free! |

> **Tip**: For best results with Ollama, use `qwen3:14b` or larger models - they produce better viral moment analysis.

## 🛠️ Troubleshooting

### YouTube IP Blocking
If downloads fail, the system automatically generates a fallback video. For real downloads, consider using a VPN or cookies.

### Whisper Transcription Slow
The first run downloads the Whisper `base` model (~150MB). Subsequent runs are faster. For speed, ensure you have a GPU available.

### No Clips Generated
Check the `logs/` folder for execution details. Common issues:
- Transcript analysis returning invalid timestamps
- Video too short for multiple clips

### LLM Not Returning Valid JSON
For Ollama users, ensure you're using a capable model like `qwen3:14b`. Smaller models may struggle with JSON output.

</details>

---

## 📄 License / Licença

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments / Agradecimentos

- [CrewAI](https://crewai.com/) - AI Agent orchestration framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing in Python
- [Whisper](https://github.com/openai/whisper) - Speech recognition for transcription
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API for multi-provider support
- [viral-clips-crew](https://github.com/alexfazio/viral-clips-crew) - Inspiration for viral moment analysis
