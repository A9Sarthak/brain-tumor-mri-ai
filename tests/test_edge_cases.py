"""
Automated unit tests for graceful edge case and error handling:
non-existent files, zero-byte files, corrupt files, unsupported extensions,
and non-existent model files.
"""
import pytest
import tempfile
from pathlib import Path
from src.predict import predict_single_image
from src.utils import verify_image_file


def test_missing_image_file_raises_error():
    """Non-existent image file must raise ValueError."""
    fake_path = Path("data/raw/non_existent_image_12345.jpg")
    with pytest.raises(ValueError, match="does not exist"):
        predict_single_image(str(fake_path))


def test_zero_byte_file_rejected():
    """Zero-byte image file must be detected and rejected."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        is_valid, err_msg, _ = verify_image_file(tmp_path)
        assert not is_valid
        assert "Zero-byte" in err_msg

        with pytest.raises(ValueError, match="Zero-byte"):
            predict_single_image(str(tmp_path))
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_corrupted_image_header_rejected():
    """File with corrupted bytes must be detected and rejected."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(b"NOT_A_VALID_JPEG_HEADER_CONTENT_GARBAGE")
        tmp_path = Path(tmp.name)
    try:
        is_valid, err_msg, _ = verify_image_file(tmp_path)
        assert not is_valid
        assert "Corrupt" in err_msg or "cannot identify" in err_msg

        with pytest.raises(ValueError):
            predict_single_image(str(tmp_path))
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_unsupported_format_rejected():
    """Non-image format (e.g. text/pdf) must be rejected."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(b"Hello MRI")
        tmp_path = Path(tmp.name)
    try:
        is_valid, err_msg, _ = verify_image_file(tmp_path)
        assert not is_valid

        with pytest.raises(ValueError):
            predict_single_image(str(tmp_path))
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_missing_model_file_raises_error():
    """Non-existent model path must raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        predict_single_image("some_valid_or_dummy.jpg", model_or_path="models/non_existent_model.keras")
