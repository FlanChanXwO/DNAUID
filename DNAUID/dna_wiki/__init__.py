from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .wiki import get_wiki
from ..utils.constants.constants import PATTERN

sv_dna_wiki = SV("dna图鉴")


@sv_dna_wiki.on_regex(rf"^(?P<name>{PATTERN})(?:图鉴|wiki|Wiki|WIKI)$", block=True)
async def send_wiki(bot: Bot, ev: Event):
    name = ev.regex_dict.get("name", "")
    await get_wiki(bot, ev, name)
