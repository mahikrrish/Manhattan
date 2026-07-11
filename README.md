# Manhattan - Offline AI Assistant

## Overview

Manhattan is a personal offline AI assistant being developed in Python to gain practical experience in building an end-to-end Artificial Intelligence system from scratch. Rather than relying on cloud-based AI services, the project focuses on understanding how independent AI components work together to create an intelligent conversational assistant.

The project integrates Speech Recognition, Natural Language Processing (NLP), Conversation Memory, Large Language Models (LLMs), and persistent database storage into a modular architecture. Each component has been designed as an independent Python module to encourage separation of responsibilities, easier debugging, future scalability, and maintainability.

The primary objective of Manhattan is educational and professional development. It serves as a hands-on engineering project for understanding the complete lifecycle of an AI assistant—from capturing user input to generating context-aware responses using a locally hosted Large Language Model.

This project is not intended to compete with commercial AI assistants. Instead, it focuses on exploring the engineering challenges involved in designing and implementing such systems while following clean software engineering principles.

---

## Key Highlights

- Offline AI Assistant developed entirely in Python.
- Modular architecture with independently testable components.
- OpenAI Whisper for Speech Recognition.
- spaCy-powered Natural Language Processing.
- Custom Conversation Memory implementation.
- Llama 3.2:3B for offline inference.
- MySQL-backed conversation history and performance monitoring.
- Comprehensive exception handling and runtime performance logging.

---

# Project Goals

- Build an offline voice-enabled AI assistant.
- Understand modern Speech-to-Text (STT) systems.
- Explore Natural Language Processing techniques using spaCy.
- Integrate a locally hosted Large Language Model into a real-world application.
- Design and implement conversation memory using MySQL.
- Learn modular software architecture and component interaction.
- Gain practical experience in debugging, testing, documentation, and performance monitoring.
- Develop a portfolio project demonstrating AI Engineering skills.

---

# System Architecture

## Current Workflow

<p align="center">
  <img src="docs/Manhattan%20Workflow.jpg" alt="Manhattan Workflow" width="850">
</p>

---

# Project Structure

```
Manhattan/
│
├── speech_recognition.py         # OpenAI Whisper speech-to-text pipeline
├── natural_language_processing.py# spaCy-based NLP preprocessing
├── conversation_memory.py        # Conversation retrieval and context construction
├── llama.py                      # Llama 3.2 integration and response generation
├── database.py                   # MySQL connection and database operations
├── performance_monitor.py        # Component performance logging
├── gui.py                        # Desktop graphical user interface
│
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── LICENSE                       # Project license
```

Each module has a single responsibility, allowing Manhattan to remain modular, maintainable, and scalable. Components communicate through well-defined interfaces, making it easier to debug, test, and extend individual modules without affecting the rest of the system.

---

# Architecture Principles

Manhattan follows a modular software architecture where each major AI capability is implemented as an independent Python component.

The design emphasizes:

- Single Responsibility Principle
- Modular component design
- Separation of concerns
- Reusability
- Maintainability
- Independent testing
- Performance monitoring
- Scalability

This architecture allows individual components to evolve independently while minimizing the impact of future enhancements on the overall system.

---

# Technologies Used

## Programming Language

- Python 3.14

Purpose

- Primary programming language used for application development.

---

## Speech Recognition

- OpenAI Whisper (Base Model)

Purpose

- Offline Speech-to-Text conversion.
- Direct microphone transcription.
- NumPy ndarray based audio processing.
- Eliminates intermediate audio file generation.

---

## Natural Language Processing

- spaCy

Purpose

- Sentence Detection
- Named Entity Recognition (NER)
- Token Analysis
- Entity Summary Generation
- Structured NLP preprocessing for downstream LLM processing.

Future Scope

- Intent Classification
- Command Routing
- Relationship Extraction
- Semantic Analysis

---

## Large Language Model

- Llama 3.2 : 3B (Local)

Purpose

- Conversational reasoning.
- Context-aware response generation.
- Multi-turn conversation understanding.
- Offline inference.

---

## Conversation Memory

- Custom Python Implementation
- MySQL

Purpose

- Retrieve previous conversations.
- Construct conversational context.
- Build LLM message history.
- Maintain configurable conversation windows.
- Supply contextual memory to the LLM.

---

## Database

- MySQL

Purpose

Stores persistent project data including:

- User Inputs
- NLP Processed Output
- Assistant Responses
- Conversation History
- Performance Monitoring Logs
- Execution Timestamps

---

## Audio Processing

- SoundDevice
- NumPy

Purpose

- Real-time microphone recording.
- Audio buffering.
- Waveform manipulation.
- Silence detection.

---

# Current Features

## Speech Recognition

Implemented using OpenAI Whisper (Base Model).

Current Features

- Real-time microphone recording.
- Direct NumPy ndarray transcription.
- No intermediate audio file generation.
- Silence-based recording termination.
- Offline Speech-to-Text conversion.
- Basic microphone error handling.
- Performance monitoring integration.

---

## Natural Language Processing

Implemented using spaCy.

Current Features

- Sentence Detection
- Named Entity Recognition (NER)
- Token Analysis
- Entity Summary Generation
- Structured NLP preprocessing
- Exception handling
- Performance monitoring integration

Current NLP Output

Each user input is transformed into a structured dictionary containing:

- Original Text
- Sentence Detection
- Named Entities
- Entity Summary
- Token Analysis

The structured output serves as the input for the Conversation Memory module before being supplied to the Large Language Model.

---

## Conversation Memory

Implemented as an independent Python module.

Current Features

- Retrieve previous conversations from MySQL.
- Configurable conversation retrieval window.
- Dynamic conversation context construction.
- LLM message history generation.
- Automatic chronological ordering.
- Independent exception handling.
- Performance monitoring integration.

Conversation Memory dynamically retrieves previous conversations, combines them with the current NLP processed input, constructs the complete message history, and supplies it to the Large Language Model.

---

## Large Language Model

Implemented using Llama 3.2 : 3B.

Current Features

- Offline inference.
- Multi-turn conversation support.
- Context-aware response generation.
- Conversation Memory integration.
- Structured NLP input processing.

The model receives conversational context generated by the Conversation Memory module together with the latest processed user input to produce an intelligent response.

---

## Database

Implemented using MySQL.

Current Tables

### Conversation History

Stores:

- Conversation ID
- User Input
- NLP Processed Output
- Assistant Response
- Conversation Timestamp

### Performance Monitor

Stores:

- Component Name
- Start Time
- End Time
- Processing Duration
- Status
- Error Message
- Conversation ID

The Performance Monitor enables runtime analysis of every major component in the system.

---

# Engineering Decisions

## Modular Architecture

Instead of developing Manhattan as a single monolithic application, each major responsibility has been implemented as an independent Python module.

Current modules include:

- Speech Recognition
- Natural Language Processing
- Conversation Memory
- Large Language Model
- Database
- Performance Monitoring

This architecture improves:

- Maintainability
- Debugging
- Component isolation
- Future scalability
- Independent testing

---

## Direct ndarray Transcription

### Initial Design

Microphone

↓

WAV File

↓

Whisper

### Current Design

Microphone

↓

NumPy ndarray

↓

Whisper

Benefits

- Eliminates disk I/O.
- Reduces latency.
- Simplifies processing pipeline.
- Faster transcription.

---

## Whisper Sample Rate

Configured at

16,000 Hz

Reason

- Native Whisper sample rate.
- Eliminates runtime resampling.
- Improved transcription efficiency.

---

## Conversation Memory Strategy

Instead of storing complete conversational context inside every database row, Manhattan dynamically reconstructs the message history whenever a new user request is processed.

Advantages

- Eliminates duplicated data.
- Reduces database storage.
- Simplifies maintenance.
- Configurable conversation window.
- Easier future enhancements.

---

## Exception Handling

Each independent component implements its own exception handling strategy.

This enables:

- Component isolation.
- Consistent logging.
- Easier debugging.
- Accurate performance monitoring.

Unexpected failures inside one component can be identified quickly through the Performance Monitor.

---

# Performance Monitoring

Performance monitoring has been implemented as an independent component throughout the project.

Each major component records:

- Conversation ID
- Component Name
- Start Time
- End Time
- Processing Duration
- Execution Status
- Error Message

The collected metrics are stored in MySQL and provide detailed visibility into the execution pipeline for debugging, optimization, and future performance analysis.

---

# Future Enhancements

The current implementation focuses on establishing a robust and modular AI architecture. Future development will extend Manhattan with additional intelligent capabilities while maintaining the same modular design philosophy.

## Speech Recognition

Future improvements include:

- Voice Activity Detection (VAD)
- Speaker Identification
- Multi-language Speech Recognition
- Noise Profile Learning
- Automatic Microphone Calibration

---

## Natural Language Processing

Future improvements include:

- Intent Classification
- Relationship Extraction
- Semantic Analysis
- Command Detection
- Keyword Ranking
- Conversation Topic Detection
- Context Classification

---

## Conversation Memory

Future improvements include:

- Semantic Memory Retrieval
- Intelligent Conversation Ranking
- Topic-based Conversation Search
- Long-term Memory Optimization
- Memory Summarization
- Dynamic Context Window Selection

---

## Large Language Model

Future improvements include:

- Model Benchmarking
- Prompt Engineering
- Response Quality Evaluation
- Multi-model Support
- GPU Optimization

---

## GUI

Future improvements include:

- Modern Desktop Interface
- Live Conversation Window
- Voice Recording Indicators
- Conversation History Viewer
- Performance Dashboard
- Settings Management

---

## Performance Monitoring

Future improvements include:

- Interactive Performance Dashboard
- Processing Time Visualization
- Component Performance Comparison
- Error Analytics
- Runtime Statistics
- System Health Monitoring

---

# Lessons Learned

Developing Manhattan has demonstrated that building an AI assistant involves significantly more engineering than simply integrating a Large Language Model.

The majority of development effort has been spent designing and implementing the surrounding ecosystem required for an intelligent assistant.

Key engineering areas explored include:

- Speech Recognition
- Audio Processing
- Natural Language Processing
- Conversation Memory
- Database Design
- Performance Monitoring
- Exception Handling
- Software Architecture
- Modular Component Design
- System Integration

One of the biggest lessons learned throughout the project is that an AI assistant is fundamentally a collection of well-designed software components working together, with the Large Language Model serving as only one part of the overall system.

The project continues to evolve as additional AI engineering concepts are explored and implemented.

---

# Project Status

Current Status

**Actively Under Development**

Completed Components

- Speech Recognition
- Natural Language Processing
- Conversation Memory
- MySQL Integration
- Performance Monitoring
- Llama 3.2 Integration

Currently Under Development

- Desktop GUI
- Response Streaming
- Voice Output
- Advanced NLP Features
- Semantic Memory Retrieval

---

# Author

**Sai Krishna Mahidhar Devulapalli**

**Sr. Risk Control Analyst**  
Amazon India

### Project

**Manhattan — Offline AI Assistant**

### Developed Using

- Python
- OpenAI Whisper
- spaCy
- Llama 3.2
- MySQL

### Project Purpose

This project has been developed as a personal learning initiative to gain practical experience in Artificial Intelligence Engineering, Natural Language Processing, Speech Recognition, Large Language Model integration, software architecture, and backend system design.

It serves as a portfolio project demonstrating the implementation of modular AI systems using locally hosted technologies and custom-built components.

---

# License

This repository is intended for educational, research, and portfolio purposes.

© 2026 Sai Krishna Mahidhar Devulapalli. All rights reserved.
