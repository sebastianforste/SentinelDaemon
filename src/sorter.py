import os
import shutil
import logging
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Load env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logging.warning("GEMINI_API_KEY not found. AI sorting will be disabled.")

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
    Uses Gemini to determine the best folder for the file.
    """
    if not API_KEY:
        return

    projects = get_project_list()
    if not projects:
        logging.warning("No projects found in ~/Developer.")
        return

    filename = file_path.name
    # Optional: Read first few bytes/lines if text to give context?
    # For now, just sort based on filename to save tokens/complexity.

    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    I have a file named "{filename}".
    I have the following project folders: {', '.join(projects)}.
    
    Based on the filename, which folder does this file belong to?
    If it is a personal document, script, or specific to a project, choose the best match.
    If it clearly doesn't belong to any, reply with "NONE".
    
    Reply ONLY with the exact folder name or "NONE".
    """

    try:
        response = model.generate_content(prompt)
        folder_name = response.text.strip()
        
        if folder_name in projects:
            dest_dir = DEVELOPER_DIR / folder_name
            dest_path = dest_dir / filename
            
            logging.info(f"AI decided: {filename} -> {folder_name}")
            
            # Handle duplicates
            if dest_path.exists():
                timestamp = int(os.path.getmtime(file_path))
                dest_path = dest_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
            shutil.move(str(file_path), str(dest_path))
            logging.info(f"Moved to: {dest_path}")
        else:
            logging.info(f"AI could not classify {filename} (Response: {folder_name}). Leaving in Downloads.")

    except Exception as e:
        logging.error(f"AI Sorting failed: {e}")
