import pytest
from pathlib import Path
from src.load_to_duckdb import check_input_path


def test_check_input_path(tmp_path: Path):
    """
    """
    tmp_csv_path = tmp_path / "test.csv"
    tmp_sql_path = tmp_path / "test.sql"
    tmp_file_path = tmp_path / "file.txt"
    fake_path = Path("fake_path/path/file.file")

    tmp_file_path.touch()
    tmp_csv_path.touch()
    tmp_sql_path.touch()

    tmp_dir = tmp_path

    with pytest.raises(NotADirectoryError):
        check_input_path(path=tmp_file_path, filetype=None)

    with pytest.raises(FileNotFoundError):
        check_input_path(path=fake_path, filetype=None)
        check_input_path(path=fake_path, filetype=".csv")
        check_input_path(path=fake_path, filetype=".txt")
        check_input_path(path=fake_path, filetype=".file")

    with pytest.raises(IsADirectoryError):
        check_input_path(path=tmp_dir, filetype=".csv")
        check_input_path(path=tmp_dir, filetype=".txt")
        check_input_path(path=tmp_dir, filetype=".file")

    with pytest.raises(ValueError):
        check_input_path(path=tmp_sql_path, filetype=".csv")
        check_input_path(path=tmp_csv_path, filetype=".sql")