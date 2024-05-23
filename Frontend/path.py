import os
from pathlib import Path


## assets의 상대 경로 ##
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


## btn_img의 상대 경로 ##
def relative_to_btn_img(path: str) -> Path:
    return BTN_IMG_PATH / Path(path)


FILE_PATH = Path(__file__)
DIR_PATH = Path(os.getcwd())

ASSETS_PATH = DIR_PATH / "assets"
BTN_IMG_PATH = ASSETS_PATH / "btn_img"

FONT_PATH = relative_to_assets("malgun.ttf")
ICON_PATH = relative_to_assets("pointchecker.ico")

TOOL1_PATH = relative_to_btn_img("tool1.png")
TOOL2_PATH = relative_to_btn_img("tool2.png")