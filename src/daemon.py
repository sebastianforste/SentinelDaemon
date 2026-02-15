import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Shared Intelligence Core
sys.path.append(str(Path("/Users/sebastian/Developer/scripts")))
try:
    from intelligence_core import apply_2026_standards
except ImportError:
    def apply_2026_standards(text: str) -> str:
        return text

class DaemonConfig(BaseSettings):
    watch_dir: Path = Field(default=Path(os.path.expanduser("~/Downloads")))
    max_workers: int = 5
    ocr_enabled: bool = True
    ai_sorting_enabled: bool = True
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_prefix="SENTINEL_", env_file=".env", extra="ignore")

config = DaemonConfig()

logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class SentinelHandler(FileSystemEventHandler):
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
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
        try:
            self.process(file_path)
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    def process(self, file_path: str):
        path = Path(file_path)
        
        if path.suffix.lower() in ['.tmp', '.crdownload', '.part', '.download']:
            return

        logging.info(f"Detected new file: {path.name}. Waiting for stability...")
        if self.wait_for_file_stability(path):
            logging.info(f"Processing: {path.name}")
            self.dispatch_tasks(path)
        else:
            logging.warning(f"File {path.name} was not stable or disappeared.")

    def wait_for_file_stability(self, path: Path, timeout: int = 60) -> bool:
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
                if stable_count > 3: # This line was part of the original code
                    return True
            else:
                last_size = current_size
                stable_count = 0
            
            time.sleep(0.5)
        
        return False

    def dispatch_tasks(self, path: Path):
        # 1. Check if PDF -> OCR
        if self.config.ocr_enabled and path.suffix.lower() == '.pdf':
            logging.info(f"Helper: OCR candidate found: {path.name}")
            from ocr import run_ocr
            run_ocr(path)
        
        # 2. All files -> Sort
        if self.config.ai_sorting_enabled:
            logging.info(f"Helper: AI Sorting candidate: {path.name}")
            from sorter import sort_file
            sort_file(path)

def check_dependencies():
    try:
        subprocess.run(['ocrmypdf', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("System check passed: ocrmypdf is installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("CRITICAL: 'ocrmypdf' not found. OCR features will fail.")
        logging.error("Please install via: brew install ocrmypdf")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()
    
    if not config.watch_dir.exists():
        logging.error("Error: Watch directory does not exist: %s", config.watch_dir)
        sys.exit(1)

    event_handler = SentinelHandler(config)
    observer = Observer()
    observer.schedule(event_handler, str(config.watch_dir), recursive=False)
    observer.start()

    logging.info(f"Sentinel Daemon watching: {config.watch_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.executor.shutdown(wait=False)
    observer.join()
