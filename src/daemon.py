import sys
import time
import logging
import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
WATCH_DIR = os.path.expanduser("~/Downloads")
LOG_FORMAT = '%(asctime)s - %(message)s'

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

class SentinelHandler(FileSystemEventHandler):
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        super().__init__()

    def on_created(self, event):
        if event.is_directory:
            return
        self.executor.submit(self.process_wrapper, event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self.executor.submit(self.process_wrapper, event.dest_path)

    def process_wrapper(self, file_path: str):
        """Wrapper to catch exceptions in threads."""
        try:
            self.process(file_path)
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    def process(self, file_path: str):
        """
        Main entry point for file processing.
        1. Debounce (wait for download to finish)
        2. Filter (ignore temporaries)
        3. Route (OCR vs Sort vs Ignore)
        """
        path = Path(file_path)
        
        # Ignored extensions
        if path.suffix.lower() in ['.tmp', '.crdownload', '.part', '.download']:
            return

        # Debounce: Wait for file to be stable
        logging.info(f"Detected new file: {path.name}. Waiting for stability...")
        if self.wait_for_file_stability(path):
            logging.info(f"Processing: {path.name}")
            # Placeholder for OCR and AI Logic
            self.dispatch_tasks(path)
        else:
            logging.warning(f"File {path.name} was not stable or disappeared.")

    def wait_for_file_stability(self, path: Path, timeout: int = 60) -> bool:
        """Waits for file size to stop changing."""
        start_time = time.time()
        last_size = -1
        stable_count = 0
        
        while (time.time() - start_time) < timeout:
            if not path.exists():
                return False
            
            try:
                current_size = path.stat().st_size
            except FileNotFoundError:
                return False

            if current_size == last_size:
                stable_count += 1
                if stable_count > 3: # Stable for 3 checks (1.5s)
                    return True
            else:
                last_size = current_size
                stable_count = 0
            
            time.sleep(0.5)
        
        return False

    def dispatch_tasks(self, path: Path):
        """Decides what to do with the file."""
        # 1. Check if PDF -> OCR
        if path.suffix.lower() == '.pdf':
            logging.info(f"Helper: OCR candidate found: {path.name}")
            from ocr import run_ocr
            run_ocr(path)
        
        # 2. All files -> Sort
        logging.info(f"Helper: AI Sorting candidate: {path.name}")
        from sorter import sort_file
        sort_file(path)

def check_dependencies():
    """Verifies system dependencies are installed."""
    try:
        subprocess.run(['ocrmypdf', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("System check passed: ocrmypdf is installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("CRITICAL: 'ocrmypdf' not found. OCR features will fail.")
        logging.error("Please install via: brew install ocrmypdf")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()
    
    if not os.path.exists(WATCH_DIR):
        print(f"Error: Directory {WATCH_DIR} does not exist.")
        sys.exit(1)

    event_handler = SentinelHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    logging.info(f"Sentinel Daemon watching: {WATCH_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.executor.shutdown(wait=False)
    observer.join()
