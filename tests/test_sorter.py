import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import sorter

MOCK_PROJECTS = ["Finance", "Legal", "Personal"]


@pytest.fixture
def mock_env(monkeypatch, tmp_path):
    dev_dir = tmp_path / "Developer"
    dev_dir.mkdir()

    for proj in MOCK_PROJECTS:
        (dev_dir / proj).mkdir()

    (dev_dir / ".hidden").mkdir()
    (dev_dir / "README.txt").write_text("not a directory")

    monkeypatch.setattr(sorter, "DEVELOPER_DIR", dev_dir)
    monkeypatch.setattr(sorter, "API_KEY", "fake-key")
    return dev_dir


def test_get_project_list_ignores_hidden_and_files(mock_env):
    projects = sorter.get_project_list()
    assert sorted(projects) == sorted(MOCK_PROJECTS)


@patch("src.sorter.genai.GenerativeModel")
def test_sort_file_success(mock_model_cls, mock_env, tmp_path):
    mock_response = MagicMock()
    mock_response.text = "Finance"

    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_cls.return_value = mock_model_instance

    source_file = tmp_path / "invoice.pdf"
    source_file.write_text("Invoice content")

    sorter.sort_file(source_file)

    expected_dest = mock_env / "Finance" / "invoice.pdf"
    assert expected_dest.exists()
    assert not source_file.exists()


@patch("src.sorter.genai.GenerativeModel")
def test_sort_file_none_keeps_file_in_place(mock_model_cls, mock_env, tmp_path):
    mock_response = MagicMock()
    mock_response.text = "NONE"

    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_cls.return_value = mock_model_instance

    source_file = tmp_path / "random.txt"
    source_file.write_text("Random content")

    sorter.sort_file(source_file)

    assert source_file.exists()
