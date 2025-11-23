# Web Browser Engineering

A step-by-step implementation of a web browser from scratch, following the book [Web Browser Engineering](https://browser.engineering/).

## Project Structure

```
web-browser-engineering/
├── browser.py          # Main browser implementation (evolves with each chapter)
├── chapter01/          # Chapter 1 exercises
├── chapter02/          # Chapter 2 exercises
└── ...
```

## Overview

This project builds a working web browser incrementally, starting from basic HTTP requests and gradually adding features like HTML parsing, layout, rendering, and JavaScript execution.

### Main File: `browser.py`

The `browser.py` file is the core implementation that grows as you progress through the book. It demonstrates:

- HTTP protocol implementation using raw sockets
- HTML parsing and DOM construction
- Layout engine
- Rendering pipeline
- (More features added chapter by chapter)

### Chapter Folders

Each `chapterXX/` directory contains solutions to exercises from that chapter, allowing you to:

- Practice specific concepts in isolation
- Experiment with variations
- Compare different implementation approaches

## Getting Started

### Prerequisites

- Python 3.x

### Running the Browser

```bash
python browser.py
```

### Working on Exercises

Navigate to the relevant chapter folder:

```bash
cd chapter01
python exercise01.py
```

## Learning Approach

This codebase prioritizes **educational clarity** over production-ready features:

- Uses 2-space indentation for consistency with the book
- Implements protocols from first principles (raw sockets vs. HTTP libraries)
- Adds complexity incrementally across chapters
- Focuses on core browser concepts

## License

Educational project following the Web Browser Engineering book.