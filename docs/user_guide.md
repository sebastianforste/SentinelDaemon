# User Guide for SentinelDaemon

SentinelDaemon is an intelligent background service that monitors your local environment and automatically organizes incoming files using OCR and AI-driven classification.

## 🛠️ Key Features

### 1. Smart File Watching
- **Directory Monitoring**: Watches `~/Downloads` for new or moved files.
- **Intelligent Debouncing**: Automatically waits for files to stabilize (finish downloading) before processing, preventing errors with partial files.
- **Concurrent Processing**: Handles multiple files simultaneously using a thread pool.

### 2. PDF OCR & Optimization
- **Automatic OCR**: Any PDF detected is processed via `ocrmypdf`.
- **Enhancements**: Includes automatic deskewing, cleaning, and basic optimization.
- **Efficiency**: Skips files that already contain a text layer to save resources.

### 3. AI-Driven Sorting
- **Project Classification**: Uses Google's Gemini Pro Flash model to analyze filenames against your `~/Developer` directory.
- **Direct Migration**: Automatically moves files to the most relevant project folder.
- **Duplicate Handling**: If a file with the same name exists in the destination, a timestamp is appended to prevent overwriting.

## ⚙️ Configuration & Setup

### Prerequisites
- **Python**: 3.12+ (managed via `uv` or `pip`).
- **System Dependencies**: `ocrmypdf` must be installed (`brew install ocrmypdf` on macOS).

### API Configuration
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```

### Running the Daemon
```bash
python src/daemon.py
```
To stop the daemon, press `Ctrl+C`. It will perform a graceful shutdown of active tasks.

## 📂 Processing Logic
1. **Detection**: New file arrives in `Downloads`.
2. **Stability Check**: Wait until the file size stops changing.
3. **OCR (PDFs only)**: Run OCR and metadata optimization.
4. **Classification**: AI analyzes the filename for project relevance.
5. **Disposition**: Move to `~/Developer/[Project]` or keep in `Downloads` if no match is found.
