import asyncio
import random
from datetime import datetime, timedelta
from typing import List

from ATRI.service import Service
from ATRI.log import log
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import ArgStr, CommandArg


class Roll:
    def add_item(self, name: str, draw_time: datetime, creator: str, count: int = 1):
        # database works here
        pass

    async def draw_later(
        self, after: timedelta, participants: List[str], count: int = 1
    ):
        await asyncio.sleep(after.total_seconds())
        winners = random.sample(participants, count)
        return winners


roll_service = Service("抽奖").document("适用于CSGO等游戏的抽奖工具")
create_roll = roll_service.on_command("/go.add", "创建抽奖")


@create_roll.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    msg = args.extract_plain_text()
    if msg:
        matcher.set_arg("roll", args)


@create_roll.got("item_name", "饰品名称？")
@create_roll.got("draw_time", "开奖时间？格式：2021-01-01 00:00:00")
@create_roll.got("count", "中奖人数？")
async def _create_roll(
    event: MessageEvent,
    item_name: str = ArgStr("item_name"),
    draw_time: str = ArgStr("draw_time"),
    count: str = ArgStr("count"),
):
    try:
        draw_time = datetime.strptime(draw_time, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        log.opt(exception=e).error("时间格式错误！")
        return
    try:
        count = int(count)
    except ValueError as e:
        log.opt(exception=e).error("中奖人数错误！")
        return
    from_user = event.user_id
    participants = [str(from_user)]
    if count > len(participants):
        count = len(participants)

    Roll().add_item(item_name, draw_time, from_user)
    create_roll.send()

    winners = await Roll().draw_later(
        draw_time - datetime.now(), participants, count=count
    )
    winners_str = "\n".join(winners)
    await create_roll.finish(
        f"""开奖啦！
{winners_str}
抽中了{item_name}
"""
    )
