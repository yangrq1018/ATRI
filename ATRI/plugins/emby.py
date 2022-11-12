from http import HTTPStatus

from nonebot.adapters.onebot.v11 import (
    MessageEvent,
)
from nonebot.params import ArgStr

from ATRI import conf
from ATRI.log import log
from ATRI.service import Service
from ATRI.utils import request


EMBY_URL = "http://127.0.0.1:8096"


class Emby:
    def __init__(self):
        self.api_key = conf.Emby.emby_key

    async def get_users(self):
        res = await request.get(EMBY_URL + "/emby/Users?api_key=" + self.api_key)
        users = res.json()
        return users

    async def create_user(self, username: str) -> str:
        endpoint = EMBY_URL + "/emby/Users/New?api_key=" + self.api_key
        res = await request.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json={"Name": username},
        )

        if res.status_code != 200:
            error_msg = res.read().decode("utf-8")
            log.error(error_msg)
            await emby_create.finish("开通失败")
        user = res.json()
        username = user["Name"]
        return username

    @classmethod
    async def delete_user(self, user_id: str) -> bool:
        endpoint = EMBY_URL + "/emby/Users/" + user_id + "?api_key=" + self.api_key
        res = await request.delete(endpoint)
        if res.status_code != HTTPStatus.NO_CONTENT:
            error_msg = res.read().decode("utf-8")
            log.error(f"{res.status_code} {error_msg}")
            return False
        return True


emby_service = Service("综合管理").document("一些乱七八糟的功能")
emby_create = emby_service.on_command("注册emby", "开通EMBY账号", aliases={"注册EMBY"})


@emby_create.got("username", "请输入用户名")
async def _create_emby(event: MessageEvent, username: str = ArgStr("username")):
    username = await Emby().create_user(username)
    await emby_create.finish(f"EMBY: 成功创建用户，用户名为{username}，默认密码为空，请登录{EMBY_URL}修改密码和观影")


emby_delete = emby_service.on_command("注销emby", "注销EMBY账号", aliases={"注销EMBY"})


@emby_delete.got("username", "请输入用户名")
async def _delete_emby(event: MessageEvent, username: str = ArgStr("username")):
    current_users = await Emby().get_users()
    try:
        user_id = [u for u in current_users if u["Name"] == username][0]["Id"]
    except IndexError:
        await emby_delete.finish(f"无法找到用户{username}")

    if not await Emby().delete_user(user_id):
        await emby_delete.finish("注销失败")
    await emby_delete.finish(f"已注销用户{username}")
