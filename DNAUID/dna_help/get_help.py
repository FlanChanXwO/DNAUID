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


def get_help_data() -> Dict[str, PluginHelp]:
    # 读取文件内容
    with open(HELP_DATA, "r", encoding="utf-8") as file:
        data = json.load(file)

    # 为每个命令添加 RGBA 图标
    for cag_name, cag_data in data.items():
        for command in cag_data.get("data", []):
            command_name = command["name"]
            # 查找对应的图标文件
            icon_file = None
            for icon in ICON_PATH.glob("*.png"):
                if icon.stem == command_name:
                    icon_file = icon
                    break
            else:
                for icon in ICON_PATH.glob("*.png"):
                    if icon.stem in command_name:
                        icon_file = icon
                        break
                else:
                    if (ICON_PATH / "通用.png").exists():
                        icon_file = ICON_PATH / "通用.png"
                    else:
                        icon_files = list(ICON_PATH.iterdir())
                        if icon_files:
                            icon_file = icon_files[0]

            if icon_file:
                # 确保图标是 RGBA 模式
                command["icon"] = Image.open(icon_file).convert("RGBA")

    return data


plugin_help = get_help_data()


async def get_help(pm: int):
    # 确保 plugin_icon 是 RGBA 模式
    plugin_icon = Image.open(ICON).convert("RGBA")
    return await get_new_help(
        plugin_name="DNAUID",
        plugin_info={f"v{DNAUID_version}": ""},
        plugin_icon=plugin_icon,
        plugin_help=plugin_help,
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
