# Code Explanation for SentinelDaemon

## Architecture

SentinelDaemon is a reactive background service built on **Watchdog** and **ThreadPoolExecutor** for concurrent file processing.

### 1. The Watcher (`src/daemon.py`)

The core is the `SentinelHandler` class, which extends `FileSystemEventHandler`:

- **Event Detection**: Monitors `~/Downloads` for `on_created` and `on_moved` events
- **Thread Pool**: Uses `ThreadPoolExecutor(max_workers=5)` to process files concurrently
- **Error Isolation**: Each file is processed in a separate thread with exception handling via `process_wrapper()`

### 2. File Stability Mechanism

The `wait_for_file_stability()` function prevents processing incomplete downloads:

- **Polling**: Checks file size every 0.5 seconds
- **Stability Threshold**: Requires 3 consecutive checks with unchanged size (1.5s total)
- **Timeout**: Gives up after 60 seconds
- **Edge Cases**: Handles files that disappear during download

### 3. The Dispatcher (`dispatch_tasks`)

Routes files to specialized processors based on file type:

- **PDF Files**: Calls `ocr.run_ocr()` to add text layers using ocrmypdf
- **All Files**: Calls `sorter.sort_file()` for AI-based organization
- **Extensible**: Easy to add new file type handlers

### 4. Dependency Checking

On startup, `check_dependencies()` verifies system tools:

- **ocrmypdf**: Required for PDF processing
- **Exit on Failure**: Prevents silent failures by exiting if dependencies are missing

## Technical Details

- **Ignored Extensions**: `.tmp`, `.crdownload`, `.part`, `.download` are automatically skipped
- **Logging**: Structured logging with timestamps for debugging
- **Graceful Shutdown**: Handles `KeyboardInterrupt` to cleanly stop observer and thread pool
