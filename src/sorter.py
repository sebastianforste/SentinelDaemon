import logging
import os
import shutil
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

# Load env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logging.warning("GEMINI_API_KEY / GOOGLE_API_KEY not found. AI sorting will be disabled.")

DEVELOPER_DIR = Path(os.path.expanduser("~/Developer"))

def get_project_list():
    """Returns a list of potential project directories."""
    if not DEVELOPER_DIR.exists():
        return []
    
    projects = []
    for item in DEVELOPER_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            projects.append(item.name)
    return projects

def sort_file(file_path: Path):
    """
    Uses Gemini 3 Flash to determine the best folder for the file.
    """
    if not API_KEY:
        return

    projects = get_project_list()
    if not projects:
        logging.warning("No projects found in ~/Developer.")
        return

    filename = file_path.name

    # Standardized 2026 Model
    model = genai.GenerativeModel('models/gemini-3-flash-preview')
    
    prompt = f"""
    You are a high-status sovereign logic engine.
    Task: Classify this file into the most relevant project folder.
    
    FILE: "{filename}"
    FOLDERS: {', '.join(projects)}
    
    CRITICAL PROTOCOLS:
    1. Reply ONLY with the exact folder name.
    2. If no folder matches perfectly, reply "NONE".
    3. Do not explain your reasoning.
    """

    try:
        response = model.generate_content(prompt)
        folder_name = response.text.strip().replace("`", "").replace('"', '')
        
        if folder_name in projects:
            dest_dir = DEVELOPER_DIR / folder_name
            dest_path = dest_dir / filename
            
            logging.info(f"AI decided: {filename} -> {folder_name}")
            
            # Handle duplicates
            if dest_path.exists():
                timestamp = int(os.path.getmtime(file_path))
                dest_path = dest_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.move(str(file_path), str(dest_path))
            logging.info(f"Successfully routed to: {dest_path.name}")
        else:
            logging.info(
                f"AI Classification: NONE for {filename}. Persistence: Original Directory."
            )

    except Exception as e:
        logging.error(f"AI Sorting engine failure: {e}")
