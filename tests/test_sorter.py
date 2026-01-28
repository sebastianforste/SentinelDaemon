import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from sorter import sort_file, get_project_list

# Mock data
MOCK_PROJECTS = ["Finance", "Legal", "Personal"]

@pytest.fixture
def mock_env(monkeypatch, tmp_path):
    """Sets up a temporary developer environment."""
    dev_dir = tmp_path / "Developer"
    dev_dir.mkdir()
    
    # Create mock project folders
    for proj in MOCK_PROJECTS:
        (dev_dir / proj).mkdir()
        
    monkeypatch.setattr("sorter.DEVELOPER_DIR", dev_dir)
    monkeypatch.setattr("sorter.API_KEY", "fake-key")
    return dev_dir

@patch("sorter.genai.GenerativeModel")
def test_sort_file_success(mock_model_cls, mock_env, tmp_path):
    """Test successful sorting into a folder."""
    # Setup mock LLM response
    mock_response = MagicMock()
    mock_response.text = "Finance"
    
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_cls.return_value = mock_model_instance
    
    # Create dummy file to sort
    source_file = tmp_path / "invoice.pdf"
    source_file.write_text("Invoice content")
    
    # Run sorter
    sort_file(source_file)
    
    # Verify file moved
    expected_dest = mock_env / "Finance" / "invoice.pdf"
    assert expected_dest.exists()
    assert not source_file.exists()

@patch("sorter.genai.GenerativeModel")
def test_sort_file_none(mock_model_cls, mock_env, tmp_path):
    """Test when LLM returns NONE (no sort)."""
    # Setup mock LLM response
    mock_response = MagicMock()
    mock_response.text = "NONE"
    
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_cls.return_value = mock_model_instance
    
    # Create dummy file
    source_file = tmp_path / "random.txt"
    source_file.write_text("Random content")
    
    # Run sorter
    sort_file(source_file)
    
    # Verify file stayed
    assert source_file.exists()
    
