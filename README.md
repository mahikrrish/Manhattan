# Manhattan - Offline AI Assistant

## Overview

Manhattan is a personal offline AI assistant being developed in Python to explore the practical implementation of modern Artificial Intelligence, Natural Language Processing (NLP), Speech Recognition, Conversational Memory, and Large Language Models (LLMs).

The primary objective of this project is educational and professional development. Manhattan serves as a hands-on platform for understanding how various AI components interact to form an intelligent conversational assistant capable of processing voice input, maintaining conversation history, and generating context-aware responses.

This project is not intended to compete with commercial AI assistants. Instead, it focuses on understanding the engineering challenges involved in building such systems from scratch.

---

## Project Goals

* Build an offline voice-enabled AI assistant.
* Understand Speech-to-Text (STT) systems.
* Explore Natural Language Processing techniques.
* Integrate Large Language Models into real-world applications.
* Implement conversational memory using databases.
* Learn software architecture, debugging, testing, and documentation practices.
* Develop a portfolio project demonstrating AI engineering skills.

---

## System Architecture

### Current Workflow

User Input (Voice/Text)

↓

OpenAI Whisper

(Speech-to-Text)

↓

spaCy NLP Processing

(Named Entity Recognition)

↓

Llama 3.2:3B

(Reasoning and Response Generation)

↕

LangChain

(Context Management)

↕

MySQL

(Conversation Memory)

↓

Assistant Response

---

## Technologies Used

### Programming Language

* Python 3.14

### Speech Recognition

* OpenAI Whisper (Base Model)

Purpose:

* Offline speech-to-text conversion.
* Converts microphone input into text.
* Supports direct NumPy waveform transcription.

### Natural Language Processing

* spaCy

Purpose:

* Named Entity Recognition (NER)
* Structured extraction of:

  * People
  * Locations
  * Organizations
  * Dates
  * Monetary Values

Future Scope:

* Intent Classification
* Command Routing
* Structured Information Extraction

### Large Language Model

* Llama 3.2:3B

Purpose:

* Conversational reasoning
* Context-aware response generation
* Query understanding

### Memory Management

* LangChain

Purpose:

* Conversation orchestration
* Retrieval of historical conversations
* Context construction for LLM prompts

### Database

* MySQL

Purpose:

* Persistent storage of:

  * User Queries
  * Assistant Responses
  * Timestamps
  * Performance Metrics
  * Conversation History

### Audio Processing

* SoundDevice
* NumPy

Purpose:

* Real-time microphone recording
* Audio buffering
* Waveform manipulation
* Silence detection

---

## Current Features

### Speech Recognition

Implemented using OpenAI Whisper Base.

Features:

* Real-time microphone recording
* Silence-based recording termination
* Direct NumPy-to-Whisper transcription
* No intermediate audio file required
* Basic microphone error handling

### Conversation Memory

Planned integration using:

* LangChain
* MySQL

Capabilities:

* Retrieve previous conversations
* Store assistant responses
* Maintain conversational context

### NLP Pipeline

Current:

* Named Entity Recognition (NER)

Future:

* Intent Classification
* Entity-driven automation
* Command execution

---

## Engineering Decisions

### Direct ndarray Transcription

Initial Design:

Microphone → WAV File → Whisper

Current Design:

Microphone → NumPy ndarray → Whisper

Reason:

* Reduced disk I/O
* Faster processing
* Simplified pipeline

### Whisper Sample Rate

Configured at:

16,000 Hz

Reason:

* Native Whisper sample rate
* Eliminates additional resampling

### Model Loading Strategy

Current:

Load Whisper model once during initialization.

Reason:

* Reduced transcription latency
* Improved runtime performance

---

## Error Handling Implemented

Current error scenarios handled include:

* Invalid microphone channel configuration
* Audio device unavailable
* Recording initialization failures

Additional error handling and recovery strategies are documented separately in the project documentation.

---

## Performance Monitoring (Planned)

The project architecture includes support for storing:

* Recording Start Time
* Recording End Time
* Transcription Start Time
* Transcription End Time
* Attempt Count
* Processing Duration
* Total Response Time

These metrics will be stored in MySQL for performance analysis.

---

## Future Enhancements

### Voice Output

* Text-to-Speech (TTS)

### Automation

* Windows System Commands
* Application Launching
* File Operations

### AI Improvements

* Better Context Retrieval
* Intent Classification
* Multi-turn Conversation Optimization

### Monitoring

* Detailed Performance Dashboard
* Error Analytics
* Usage Metrics

---

## Lessons Learned

Throughout development, one of the most significant observations has been that building AI systems involves considerably more engineering work than model integration.

Areas such as:

* Audio capture
* Data preprocessing
* Error handling
* Memory management
* Performance optimization

often require more effort than invoking the AI model itself.

This project serves as a practical exploration of those engineering challenges.

---

## Author

Sai Krishna Mahidhar Devulpalli

Amazon India

Risk Control Analyst

Project: Manhattan - Offline AI Assistant

Year: 2026


