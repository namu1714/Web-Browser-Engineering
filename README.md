# Web Browser Engineering

A step-by-step implementation of a web browser from scratch, following the book [Web Browser Engineering](https://browser.engineering/).

## Project Structure

```
web-browser-engineering/
├── src/                # Core browser implementation
│   ├── main.py         # Main entry point
│   ├── browser.py      # Browser class implementation
│   ├── url.py          # URL handling
│   ├── layout.py       # Layout engine
│   ├── globals.py      # Global configurations
│   └── server/         # Test web server
├── chapter01/          # Chapter 1 exercises
│   ├── browser01-ex1.py
│   ├── browser01-ex5.py
│   └── ...
├── chapter02/          # Chapter 2 exercises
│   ├── browser02-ex1.py
│   ├── browser02-ex2.py
│   └── ...
└── README.md
```

## Overview

This project builds a working web browser incrementally, starting from basic HTTP requests and gradually adding features like HTML parsing, layout, rendering, and JavaScript execution.

### Core Implementation (`src/`)

The `src/` directory contains the modular browser implementation:

- **`main.py`**: Entry point for running the browser
- **`browser.py`**: Core Browser class with rendering and event handling
- **`url.py`**: URL parsing and HTTP request handling
- **`layout.py`**: Layout engine for positioning elements
- **`globals.py`**: Global configuration and constants

This modular structure demonstrates:

- HTTP protocol implementation using raw sockets
- HTML parsing and DOM construction
- Layout engine
- Rendering pipeline
- (More features added chapter by chapter)

### Test Server (`src/server/`)

The `server/` directory contains a local web server for testing the browser implementation with various HTML pages and scenarios.

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
cd src
python3 main.py
```

Or from the root directory:

```bash
python3 src/main.py
```

### Running the Test Server

```bash
cd src/server
python3 server.py
```

Then navigate your browser to `http://localhost:8000` to test various pages.

### Working on Exercises

Navigate to the relevant chapter folder:

```bash
cd chapter01
python3 browser01-ex1.py
```

## Learning Approach

This codebase prioritizes **educational clarity** over production-ready features:

- Uses 2-space indentation for consistency with the book
- Implements protocols from first principles (raw sockets vs. HTTP libraries)
- Adds complexity incrementally across chapters
- Focuses on core browser concepts

## License

Educational project following the Web Browser Engineering book.
