from ATRI.service import Service
from ATRI.permission import ADMIN, MASTER
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, Bot
from nonebot.params import ArgStr
from pathlib import Path
import random
import asyncio

PERFECT_WORLD_ACCOUNTS_DIR = Path(".") / "data" / "plugins" / "pf_accounts"

PERFECT_WORLD_ACCOUNTS_DIR.mkdir(exist_ok=True)

pfa = Service("完美小号").document("查询完美小号账号密码")

query_account = pfa.on_command("完美账号", "获得一个完美账号和密码", permission=ADMIN | MASTER)


@query_account.got("index", '要第几个？如：8；或者说"随便"')
async def _(bot: Bot, event: MessageEvent, index: str = ArgStr("index")):
    FILE = PERFECT_WORLD_ACCOUNTS_DIR / "accounts.txt"
    with open(FILE, "r") as f:
        text = f.read()
        pieces = text.split("\n\n")

    if index.strip() == "随便":
        index = random.randrange(0, len(pieces))
    else:
        try:
            index = int(index) + 1
        except ValueError:
            await query_account.reject("请输入数字!")

    if index >= len(pieces) or index < 0:
        await query_account.reject("这份账号不存在")

    msg = await bot.send(event, pieces[index])
    if isinstance(event, GroupMessageEvent):
        await query_account.send("将在5秒后删除。。。")
        await asyncio.sleep(5)
        await bot.delete_msg(message_id=msg["message_id"])
