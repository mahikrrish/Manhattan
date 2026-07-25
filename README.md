# Manhattan — Offline AI Assistant

## Overview

Manhattan is a personal offline AI assistant developed entirely in Python to gain practical, hands-on experience in designing and building an end-to-end Artificial Intelligence system from scratch.

Rather than relying on cloud-based AI services, the project focuses on understanding how independent AI components work together to create an intelligent conversational assistant. Each component has been designed as an independent Python module, emphasizing separation of responsibilities, modular architecture, easier debugging, and maintainability.

The project integrates Speech Recognition, Natural Language Processing (NLP), Conversation Memory, a locally hosted Large Language Model, persistent database storage, and a desktop GUI into a single cohesive system.

> **This project is not intended to compete with commercial AI assistants.**
> It is a personal engineering and portfolio project built to explore the complete lifecycle of an AI assistant — from capturing user input to generating context-aware responses using a locally hosted Large Language Model.

---

## Key Highlights

- Fully offline — no internet connection required after setup
- Modular architecture with independently testable components
- OpenAI Whisper (Base) for Speech-to-Text
- spaCy for Natural Language Processing
- Llama 3.2:3B for offline LLM inference via Ollama
- Custom-built Conversation Memory backed by MySQL
- Comprehensive performance monitoring per component
- Desktop GUI built with CustomTkinter
- Python 3.14.3

---

## System Architecture

<p align="center">
  <img src="docs/Manhattan Workflow.jpg" alt="Manhattan Workflow Diagram" width="850">
</p>

---

## Project Structure

```
Manhattan/
│
├── config.py                       # One-time database setup — run first
├── user_interface.py               # Main application entry point
│
├── speech_recognition.py           # OpenAI Whisper speech-to-text pipeline
├── natural_language_processing.py  # spaCy NLP preprocessing
├── conversation_memory.py          # Conversation retrieval and context construction
├── manhattan.py                    # Llama 3.2:3B integration and response generation
├── database.py                     # MySQL operations and performance monitoring
│
├── database_schema.sql             # Database and table definitions
├── requirements.txt                # Python dependencies
│
├── assets/
│   ├── Manhattan Icon.ico          # Application window icon (title bar)
│   ├── Manhattan Icon.png          # Splash screen image
│   ├── microphone.png              # Microphone button icon
│   ├── send-button.png             # Submit button icon
│   └── data-retrieval.png          # Conversation retrieval button icon
│
├── docs/
│   └── Manhattan Workflow.jpg      # Architecture workflow diagram
│
├── __init__.py                     # Package initializer
├── README.md                       # Project documentation
└── LICENSE                         # Project license
```

---

## Technologies Used

| Category | Technology |
|---|---|
| Language | Python 3.14.3 |
| Speech Recognition | OpenAI Whisper (Base) |
| NLP | spaCy — en_core_web_sm |
| LLM | Llama 3.2:3B via Ollama |
| Audio | SoundDevice, NumPy |
| Database | MySQL |
| GUI | CustomTkinter |

---

## Prerequisites

Before installing Python dependencies, the following must be installed on your system.

### 1. FFmpeg

FFmpeg is required by OpenAI Whisper for audio processing.

Download FFmpeg from https://ffmpeg.org/download.html

Extract the archive and add the `bin` folder to your system PATH.

Verify installation:
```
ffmpeg -version
```

> **Note:** Manhattan has been developed and tested on Windows only. Installation on macOS or Linux has not been tested.

---

### 2. Ollama

Ollama is required to run Llama 3.2:3B locally.

Download and install Ollama from https://ollama.com

After installation, pull the Llama 3.2:3B model:
```
ollama pull llama3.2:3b
```

Verify Ollama is running:
```
ollama list
```

Ollama must be running in the background before launching Manhattan.

---

### 3. MySQL

Manhattan requires a running MySQL server.

Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/

During installation, note your:
- Host (usually `localhost`)
- Port (usually `3306`)
- Username (usually `root`)
- Password (set during installation)

These values will be needed during configuration.

---

## Installation

### Step 1 — Clone the repository

```
git clone https://github.com/mahikrrish/Manhattan.git
cd Manhattan
```

### Step 2 — Install Python dependencies

```
pip install -r requirements.txt
```

### Step 3 — Download the spaCy language model

```
python -m spacy download en_core_web_sm
```

### Step 4 — Download the OpenAI Whisper Base model

The Whisper Base model downloads automatically the first time Manhattan's Speech Recognition component runs. No manual download is required.

To pre-download it manually:
```python
import whisper
whisper.load_model("base")
```

---

## Configuration — Run Once

Before launching Manhattan for the first time, the database must be configured.

### Step 1 — Edit config.py

Open `config.py` and update the following values with your local MySQL credentials:

```python
DB_HOST = "localhost"       # Your MySQL host
DB_PORT = 3306              # Your MySQL port (integer, no quotes)
DB_USER = "root"            # Your MySQL username
DB_PASSWORD = "yourpassword" # Your MySQL password
```

> **Note:** Remove the quotes around `DB_PORT` — it must be an integer.

### Step 2 — Run config.py

```
python config.py
```

This script will:
- Connect to your MySQL server
- Create the `offlineai` database
- Create the `conversation_history` and `performance_monitor` tables from `database_schema.sql`
- Generate a `database_configuration.py` file used by the application

A confirmation dialog will appear on success.

> **Important:** Run `config.py` only once. If you run it again, it will detect the existing `database_configuration.py` and prompt you to run `user_interface.py` instead.

---

## Running Manhattan

After configuration is complete, launch the application:

```
python user_interface.py
```

A splash screen will appear for 3 seconds, followed by the main chat window.

---

## Features

### Speech Recognition

- Real-time microphone recording via SoundDevice
- Silence-based automatic recording termination (10 seconds)
- Direct NumPy ndarray transcription — no intermediate audio file
- OpenAI Whisper Base offline transcription
- Audio recorded at 16,000 Hz (Whisper's native sample rate)
- Basic microphone error handling with retry logic

### Natural Language Processing

- Sentence detection
- Named Entity Recognition (NER)
- Entity summary grouped by label (PERSON, ORG, GPE, DATE, etc.)
- Token-level analysis (text, lemma, POS tag)
- Graceful fallback — if NLP fails, raw text is forwarded to the LLM

### Conversation Memory

- Retrieves last 10 conversations from MySQL
- Dynamically reconstructs chronological message history
- Builds LLM-compatible message array for Ollama's chat API
- Configurable retrieval window (row_limit parameter)
- Fully independent of the LLM component

### Large Language Model

- Offline inference using Llama 3.2:3B via Ollama
- Multi-turn conversation with full context awareness
- System prompt defining Manhattan's personality and behavior
- Temperature: 0.3 (focused, consistent responses)
- Context window: 16,384 tokens
- Model keep-alive: 10 minutes (avoids repeated model loading)

### Database

Two tables managed by MySQL:

**conversation_history** — stores per-conversation data:
- Conversation ID, input mode, timestamp
- Raw user input, NLP output, conversation memory input
- AI response, execution timings, status, error message

**performance_monitor** — stores per-component execution data:
- Component name, start time, end time, duration
- Execution status, error message
- Linked to conversation_history via conversation_id

### User Interface

- Desktop GUI built with CustomTkinter
- Splash screen on startup
- Chat window with user (purple) and AI (green) message bubbles
- Text input with Enter key shortcut
- Microphone button for voice input
- Conversation history retrieval
- Controls disabled during processing to prevent concurrent requests
- All backend operations run in worker threads — UI stays responsive

---

## Database Schema

```sql
CREATE DATABASE IF NOT EXISTS offlineai;
USE offlineai;

CREATE TABLE conversation_history (
    conversation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    input_mode      VARCHAR(20),
    created_at      DATETIME,
    raw_text        LONGTEXT,
    processed_text  JSON,
    conversationmemory_input LONGTEXT,
    ai_response     LONGTEXT,
    run_start_time  DOUBLE,
    run_end_time    DOUBLE,
    run_duration    DOUBLE,
    status          VARCHAR(50),
    error_message   TEXT
) AUTO_INCREMENT = 1001;

CREATE TABLE performance_monitor (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    created_at      DATETIME     NOT NULL,
    component       VARCHAR(200) NOT NULL,
    start_time      DOUBLE       NOT NULL,
    end_time        DOUBLE       NOT NULL,
    duration        DOUBLE       NOT NULL,
    status          VARCHAR(100) NOT NULL,
    error_message   TEXT,
    conversation_id BIGINT,
    CONSTRAINT fk_performance_monitor_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversation_history (conversation_id)
);
```

---

## Engineering Decisions

### Modular Architecture

Each component — Speech Recognition, NLP, Conversation Memory, LLM, Database, GUI — is implemented as an independent Python module. This means any component can be updated, replaced, or debugged without affecting the rest of the system.

### Direct ndarray Transcription

Audio captured from the microphone is passed directly to Whisper as a NumPy ndarray — no intermediate WAV file is written to disk. This eliminates disk I/O, reduces latency, and simplifies the pipeline.

### Custom Conversation Memory

LangChain was evaluated for conversation memory management but was dropped. At the time of development, LangChain was actively migrating to LangGraph, creating version incompatibilities with Python 3.14 and a lack of stable documentation. A custom ConversationMemory component was built instead — it is reliable, fully understood, and does exactly what the project requires.

### Two-Phase Conversation Lifecycle

A conversation row is created in the database **before** processing begins (Phase 1), and updated with all results **after** processing completes (Phase 2). This ensures that component-level performance records are always linked to their parent conversation row, even if processing fails midway.

### Threading

All long-running operations (speech recognition, NLP, LLM inference) run in background threads. All GUI updates from worker threads are scheduled on the main event loop using CustomTkinter's `.after()` method, ensuring thread-safe UI updates.

---

## Future Enhancements

### Speech Recognition
- Voice Activity Detection (VAD)
- Multi-language support
- Speaker identification
- Noise profile learning

### Natural Language Processing
- Intent classification
- Command routing
- Semantic analysis
- Relationship extraction

### Conversation Memory
- Semantic retrieval using vector embeddings
- Topic-based conversation search
- Memory summarization
- Dynamic context window selection

### LLM
- Response streaming (token-by-token display)
- Multi-model support
- GPU optimization
- Prompt engineering improvements

### GUI
- Performance dashboard
- Voice recording indicators
- Settings management panel
- Conversation history viewer

---

## Lessons Learned

Building Manhattan demonstrated that an AI assistant is far more than just integrating a language model. The majority of development effort went into designing and building the surrounding ecosystem — audio capture, NLP preprocessing, conversation memory, database design, performance monitoring, threading, and GUI coordination.

The largest lesson: **the LLM is only one component of an AI system.** The engineering around it — how data flows in, how context is managed, how failures are handled — determines whether the system actually works in practice.

---

## Project Status

**Complete**

| Component | Status |
|---|---|
| Speech Recognition | Complete |
| Natural Language Processing | Complete |
| Conversation Memory | Complete |
| Llama 3.2:3B Integration | Complete |
| MySQL Integration | Complete |
| Performance Monitoring | Complete |
| Desktop GUI | Complete |

---

## Author

**Sai Krishna Mahidhar Devulapalli**

Sr. Risk Control Analyst — Amazon India

- GitHub: [github.com/mahikrrish](https://github.com/mahikrrish)
- LinkedIn: [linkedin.com/in/sai-krishnamahidhar-devulapalli-811158210](https://www.linkedin.com/in/sai-krishnamahidhar-devulapalli-811158210/)

---

## License

This repository is intended for educational, research, and portfolio purposes.

© 2026 Sai Krishna Mahidhar Devulapalli. All rights reserved.
