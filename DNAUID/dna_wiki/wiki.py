from pathlib import Path

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.msgs.notify import dna_not_found
from ..utils.name_convert import alias_to_char_name

WIKI_PATH = Path(__file__).parent / "texture2d" / "role"


async def get_role_wiki(bot: Bot, ev: Event, char_name: str):
    real_name = alias_to_char_name(char_name)
    if not real_name:
        await dna_not_found(bot, ev, f"角色别名【{char_name}】")
        return

    img_path = WIKI_PATH / f"{real_name}.webp"
    if not img_path.exists():
        await dna_not_found(bot, ev, f"角色【{real_name}】图鉴")
        return

    img = await convert_img(img_path)
    await bot.send(img)
