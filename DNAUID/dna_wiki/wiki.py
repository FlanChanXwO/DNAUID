from pathlib import Path

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.msgs.notify import dna_not_found
from ..utils.name_convert import alias_to_char_name, alias_to_weapon_name

WIKI_PATH = Path(__file__).parent / "texture2d"
ROLE_PATH = WIKI_PATH / "role"
WEAPON_PATH = WIKI_PATH / "weapon"
SPIRIT_PATH = WIKI_PATH / "spirit"


async def get_wiki(bot: Bot, ev: Event, name: str):
    # 角色
    real_name = alias_to_char_name(name)
    if real_name:
        img_path = ROLE_PATH / f"{real_name}.webp"
        if img_path.exists():
            logger.info(f"[二重螺旋] 发送{real_name}角色图鉴")
            await bot.send(await convert_img(img_path))
            return

    # 武器
    weapon_name = alias_to_weapon_name(name)
    img_path = WEAPON_PATH / f"{weapon_name}.webp"
    if img_path.exists():
        logger.info(f"[二重螺旋] 发送{weapon_name}武器图鉴")
        await bot.send(await convert_img(img_path))
        return

    # 魔灵
    img_path = SPIRIT_PATH / f"{name}.webp"
    if img_path.exists():
        logger.info(f"[二重螺旋] 发送{name}魔灵图鉴")
        await bot.send(await convert_img(img_path))
        return

    await dna_not_found(bot, ev, f"【{name}】图鉴")
