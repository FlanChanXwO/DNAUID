from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .wiki import get_role_wiki
from ..utils.constants.constants import PATTERN

sv_dna_wiki = SV("dna图鉴")


@sv_dna_wiki.on_regex(rf"^(?P<char_name>{PATTERN})(?:图鉴|wiki|Wiki|WIKI)$", block=True)
async def send_role_wiki(bot: Bot, ev: Event):
    char_name = ev.regex_dict.get("char_name", "")
    await get_role_wiki(bot, ev, char_name)
