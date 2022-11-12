from ATRI.service import Service
from ATRI.permission import ADMIN, MASTER
from ATRI.rule import to_bot
from nonebot.params import ArgStr
import pathlib
import valve.rcon
from ATRI import conf


def execute(command: str) -> str:
    return valve.rcon.execute(
        (conf.SourceMod.host, conf.SourceMod.port), conf.SourceMod.password, command
    )


csa = Service("CSGO服务器管理员").document("写入管理员信息SourceMod simple admin配置文件")

CSGO_SERVER_INSTALL_PATH = pathlib.Path("~/csgo/").expanduser()
SOURCE_MOD_ADMIN_SIMPLE_CFG = (
    CSGO_SERVER_INSTALL_PATH / "csgo/addons/sourcemod/configs/admins_simple.ini"
)


add_admin = csa.on_command(
    "添加SM管理员",
    "增加一个SouceMod管理员，仅限QQ群主和管理员",
    rule=to_bot(),
    permission=ADMIN | MASTER,
)


@add_admin.got("steamid", prompt="请输入你的SteamID信息，可在控制台用status命令查看，如STEAM_1:1:564855229")
async def _(steam_id: str = ArgStr("steamid")):
    steam_id = steam_id.strip()
    with open(SOURCE_MOD_ADMIN_SIMPLE_CFG, "a") as f:
        f.write(
            """
// added by ATRI bot
"{steam_id}"    "99:z"
""".format(
                steam_id=steam_id
            )
        )
    await add_admin.send("添加成功！")
    execute("sm_reloadadmins")
    await add_admin.finish("配置文件已重载")


get_admin = csa.on_command("查看SM管理员", "查看当前服务器管理员列表")


@get_admin.handle()
async def _():
    admins = []
    with open(SOURCE_MOD_ADMIN_SIMPLE_CFG, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if not line.startswith("//"):
                tokens = (x for x in line.split(" ") if x != "")
                try:
                    name = next(tokens)
                    permission = next(tokens)
                    admins.append((name, permission))
                except StopIteration:
                    pass
    await get_admin.finish("\n".join(f"用户ID{n} 权限{p}" for n, p in admins))


get_plugins = csa.on_command("SM插件列表", "RCON: 列出加载的SM插件")


@get_plugins.handle()
async def _():
    msg = execute("sm plugins list")
    await get_plugins.finish(msg)


refresh_admin = csa.on_command("刷新SM管理员", "RCON：命令SourceMod读取管理员文件")


@refresh_admin.handle()
async def _():
    await refresh_admin.finish(execute("sm_reloadadmins"))
