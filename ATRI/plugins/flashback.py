from ATRI.service import Service
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from ATRI import conf
import re


fb = Service("闪照").document("捕捉闪照图片，发送给管理员")

record_flashback = fb.on_regex(r"CQ:image,file=.*,type=flash", "检测到闪照时自动触发")


@record_flashback.handle()
async def _record_flashback(bot: Bot, event: MessageEvent):
    """go-cqhttp 无法收到群聊闪照消息
    私聊闪照放撤回功能正常"""
    msg = event.get_message()
    if len(msg) < 1:
        return
    msg0: MessageSegment = msg[0]
    # msg0 is text type
    if isinstance(event, GroupMessageEvent):
        await record_flashback.send("接收到一条闪照(群聊)，发送给admin过目啦")
    elif isinstance(event, PrivateMessageEvent):
        await record_flashback.send("干嘛发给人家看啦，偷偷转发给admin了")

    msg0.type = "image"
    data = msg0.data
    data["file"] = re.search(r"file=(.*\.image)", data.pop("text")).group(1)
    data["type"] = ""

    for superuser in conf.BotConfig.superusers:
        await bot.send_private_msg(user_id=superuser, message=msg)
