from nonebot import get_bot
from ATRI.utils.apscheduler import scheduler
from ATRI.utils import request
from ATRI.log import log

from typing import Optional
from datetime import datetime


@scheduler.scheduled_job("cron", name="广播集思录A股温度", hour=9, minute=35)
@scheduler.scheduled_job("cron", name="广播集思录A股温度", hour=15, minute=5)
async def _():
    log.info("运行集思录任务")
    bot = get_bot()
    w_group = await bot.get_group_list()
    resp = await request.post(
        "https://www.jisilu.cn/data/indicator/get_last_indicator/"
    )
    indicator_data = resp.json()
    temp: Optional[str] = indicator_data.get("median_pb_temperature", None)
    if temp:
        for i in w_group:
            group_id = i["group_id"]
            if group_id != 852485822:
                continue
            if datetime.now().hour == 9:
                greeting = "开盘啦"
            else:
                greeting = "收盘啦"
            await bot.send_group_msg(
                group_id=group_id, message=f"{greeting}，现在A股温度为: {temp}℃"
            )
