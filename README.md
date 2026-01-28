# Sentinel Daemon

## Overview
A background service that intelligently organizes your digital life.
It watches folders (Downloads, Teams), processes files (OCR PDFs, Transcribe Audio), and uses AI to sort them into the correct project directories.

## Features
- **File Watching**: Monitors `~/Downloads` for new files in real-time using Watchdog
- **Smart Debouncing**: Waits for downloads to complete before processing (prevents partial file processing)
- **Concurrent Processing**: Uses ThreadPoolExecutor to handle multiple files simultaneously
- **OCR Integration**: Automatically adds text layers to PDFs using `ocr_rename`
- **AI Sorting**: Uses Gemini to analyze content and move files to destination folders
- **Robust Error Handling**: Each file processed in isolation with comprehensive error logging

## Quick Start

### Prerequisites
- Python 3.12+
- `ocrmypdf` installed on your system

```bash
# Install ocrmypdf (macOS)
brew install ocrmypdf

# Install Python dependencies
uv install -r requirements.txt
```

### Running the Daemon

```bash
# Run directly
python src/daemon.py

# The daemon will:
# 1. Check for required dependencies
# 2. Start watching ~/Downloads
# 3. Process new files automatically
# 4. Log all activity to console
```

### Stopping the Daemon
Press `Ctrl+C` to gracefully shutdown. The daemon will:
- Stop the file observer
- Wait for in-progress files to complete (or force-stop after timeout)
- Clean up resources

## Troubleshooting

### "ocrmypdf not found"
Install via Homebrew: `brew install ocrmypdf`

### Files not being processed
- Check that files are in `~/Downloads`
- Verify file extensions aren't in the ignore list (`.tmp`, `.crdownload`, etc.)
- Check logs for error messages

### High CPU usage
Reduce `max_workers` in `SentinelHandler.__init__()` from 5 to a lower number


## Development Standards

This project follows the "Senior Staff Mentor" persona standards.

### 1. Technology Stack
*   **Python**: 3.12+ (Use modern features like `pathlib`, f-strings).
*   **Typing**: Strict Type Hints with **Pydantic V2**.
*   **Style**: **Black** formatting and **Ruff** linting.

### 2. Engineering Principles
*   **structure**: Code in `src/`, tests in `tests/`, docs in `docs/`.
*   **Safety**: No secrets in code (use `.env`).
*   **Testing**: `pytest` for all logic.

### 3. Workflow
*   **Commits**: Conventional Commits (e.g., `feat: add user login`).
