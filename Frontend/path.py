import os
from pathlib import Path

FILE_PATH = Path(__file__)
OUTPUT_PATH = FILE_PATH.parent

DIR_PATH = Path(os.getcwd())

ASSETS_PATH = DIR_PATH / "assets"
FONT_PATH = "Malgun Gothic"
ICON_PATH = "pointchecker.ico"
# ICON_PATH = ASSETS_PATH / "pointchecker.ico"