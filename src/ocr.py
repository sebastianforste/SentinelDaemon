import subprocess
import logging
import shutil
from pathlib import Path

def run_ocr(input_path: Path):
    """
    Runs OCR on the given PDF path using ocrmypdf.
    If the file already has text, it will be skipped by --skip-text.
    """
    if not shutil.which("ocrmypdf"):
        logging.error("ocrmypdf not found in PATH. Please install it with 'brew install ocrmypdf'.")
        return False

    output_path = input_path # In-place replacement
    
    cmd = [
        "ocrmypdf",
        "--skip-text",        # Skip if text exists
        "--clean",            # Clean up image
        "--deskew",           # Internet PDFs are often skewed
        "--optimize", "1",    # Slight optimization
        str(input_path),
        str(output_path)
    ]

    logging.info(f"Starting OCR on {input_path.name}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info(f"OCR Complete: {input_path.name}")
            return True
        elif result.returncode == 6: 
            # Exit code 6 means "Input file already contains text" (with --skip-text)
            logging.info(f"OCR Skipped (Already has text): {input_path.name}")
            return True
        else:
            logging.error(f"OCR Failed for {input_path.name}: {result.stderr}")
            return False

    except Exception as e:
        logging.error(f"OCR Exception for {input_path.name}: {e}")
        return False
