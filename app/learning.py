import json
from pathlib import Path


def load_courses(data_directory: Path) -> list[dict]:
    """Load the versioned, self-authored lessons shipped with the application."""
    catalog_file = data_directory / 'courses.json'
    return json.loads(catalog_file.read_text(encoding='utf-8'))['courses']


def load_curriculum(data_directory: Path) -> dict:
    """Return the THPT subject directory and the legal references behind it."""
    return json.loads((data_directory / 'curriculum.json').read_text(encoding='utf-8'))
