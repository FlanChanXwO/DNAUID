import json
from typing import Dict
from pathlib import Path

from PIL import Image

from gsuid_core.help.model import PluginHelp
from gsuid_core.help.draw_new_plugin_help import get_new_help

from ..version import DNAUID_version
from ..dna_config import DNA_PREFIX
from ..utils.image import get_footer

ICON = Path(__file__).parent.parent.parent / "ICON.png"
HELP_DATA = Path(__file__).parent / "help.json"
ICON_PATH = Path(__file__).parent / "icon_path"
TEXT_PATH = Path(__file__).parent / "texture2d"


def load_help_data() -> Dict[str, PluginHelp]:
    """加载帮助数据"""
    with open(HELP_DATA, "r", encoding="utf-8") as file:
        return json.load(file)


def ensure_rgba(img: Image.Image) -> Image.Image:
    """确保图像为 RGBA 模式"""
    if img.mode != "RGBA":
        return img.convert("RGBA")
    return img


def find_icon_rgba(name: str) -> Image.Image:
    """查找图标并确保为 RGBA 模式"""
    for icon in ICON_PATH.glob("*.png"):
        if icon.stem == name:
            return ensure_rgba(Image.open(icon))

    for icon in ICON_PATH.glob("*.png"):
        if icon.stem in name:
            return ensure_rgba(Image.open(icon))

    if (ICON_PATH / "通用.png").exists():
        return ensure_rgba(Image.open(ICON_PATH / "通用.png"))

    return ensure_rgba(Image.open(next(ICON_PATH.iterdir())))


def prepare_help_data(data: Dict[str, PluginHelp]) -> Dict[str, PluginHelp]:
    """为所有命令预加载 RGBA 图标"""
    for cag_data in data.values():
        for command in cag_data.get("data", []):
            command["icon"] = find_icon_rgba(command["name"])
    return data


# 预加载帮助数据和图标
_plugin_help = prepare_help_data(load_help_data())
_plugin_icon = ensure_rgba(Image.open(ICON))


async def get_help(pm: int):
    return await get_new_help(
        plugin_name="DNAUID",
        plugin_info={f"v{DNAUID_version}": ""},
        plugin_icon=_plugin_icon,
        plugin_help=_plugin_help,
        plugin_prefix=DNA_PREFIX,
        help_mode="dark",
        banner_bg=Image.open(TEXT_PATH / "banner_bg.jpg"),
        banner_sub_text="穿过寒夜，去往有你的春天。",
        help_bg=Image.open(TEXT_PATH / "bg.jpg"),
        cag_bg=Image.open(TEXT_PATH / "cag_bg.png"),
        item_bg=Image.open(TEXT_PATH / "item.png"),
        icon_path=ICON_PATH,
        footer=get_footer(),
        enable_cache=False,
        column=4,
        pm=pm,
    )
