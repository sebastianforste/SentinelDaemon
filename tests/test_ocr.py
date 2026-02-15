import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.ocr import run_ocr


def test_run_ocr_returns_false_when_binary_missing(tmp_path):
    input_file = tmp_path / "sample.pdf"
    input_file.write_text("pdf")

    with patch("src.ocr.shutil.which", return_value=None):
        assert run_ocr(input_file) is False


def test_run_ocr_returns_true_on_success_exit_code(tmp_path):
    input_file = tmp_path / "sample.pdf"
    input_file.write_text("pdf")

    with patch("src.ocr.shutil.which", return_value="/usr/bin/ocrmypdf"):
        with patch("src.ocr.subprocess.run", return_value=SimpleNamespace(returncode=0, stderr="")):
            assert run_ocr(input_file) is True


def test_run_ocr_returns_true_when_text_already_present(tmp_path):
    input_file = tmp_path / "sample.pdf"
    input_file.write_text("pdf")

    with patch("src.ocr.shutil.which", return_value="/usr/bin/ocrmypdf"):
        with patch("src.ocr.subprocess.run", return_value=SimpleNamespace(returncode=6, stderr="")):
            assert run_ocr(input_file) is True


def test_run_ocr_returns_false_on_error_exit_code(tmp_path):
    input_file = tmp_path / "sample.pdf"
    input_file.write_text("pdf")

    with patch("src.ocr.shutil.which", return_value="/usr/bin/ocrmypdf"):
        with patch(
            "src.ocr.subprocess.run",
            return_value=SimpleNamespace(returncode=2, stderr="failed"),
        ):
            assert run_ocr(input_file) is False
