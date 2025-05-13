import json
from pathlib import Path
from typing import Final

from amazon_parser.settings import BASE_DIR


ALL_BOOKS_PARSING_STATUS: Final[str] = "all_books_parsing"
CACHE_FILE_PATH: Final[Path] = BASE_DIR / "parsing_status.json"

if not CACHE_FILE_PATH.exists():
    with open(CACHE_FILE_PATH, 'w') as f:
        json.dump({}, f)

def get_parsing_status() -> bool:
    with open(CACHE_FILE_PATH, "r") as f:
        try:
            data = json.load(f)
            return data.get(ALL_BOOKS_PARSING_STATUS, False)
        except Exception:
            return False

def set_parsing_status(status: bool) -> None:
    with open(CACHE_FILE_PATH, "w") as f:
        data = {ALL_BOOKS_PARSING_STATUS: status}
        json.dump(data, f)

def clear_parsing_status() -> None:
    with open(CACHE_FILE_PATH, "w") as f:
        json.dump({}, f)
