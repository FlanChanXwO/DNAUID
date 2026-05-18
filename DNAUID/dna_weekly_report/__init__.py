from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .draw_weekly_report import draw_weekly_report_img

dna_weekly_report = SV("dna周报")


@dna_weekly_report.on_fullmatch(("本周周报", "周报"))
async def send_weekly_report_current(bot: Bot, ev: Event):
    await draw_weekly_report_img(bot, ev, week_type=1)


@dna_weekly_report.on_fullmatch(("上周周报",))
async def send_weekly_report_last(bot: Bot, ev: Event):
    await draw_weekly_report_img(bot, ev, week_type=2)
