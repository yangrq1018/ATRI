import requests
import datetime
import os
import re
import aiohttp
import aiofiles
import asyncio
import warnings

from ATRI.utils.apscheduler import scheduler
from ATRI import conf
from ATRI.log import log

url = "https://api.github.com/repos/hehonghui/{repo}/contents/{path}"
file_browser_path = "/etc/filebrowser/经济学人pdf/"
session = requests.session()


def list_repo_path(repo, path):
    session.headers.update(
        {"Authorization": "Bearer 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"}
    )
    res = session.get(url.format(repo=repo, path=path))
    if res.status_code != 200:
        raise ValueError(res.content)
    data = res.json()
    return data


def get_pdfs():
    pdfs = os.listdir(file_browser_path)
    return pdfs


def get_pdf_dates(pdfs):
    r = re.compile(r"\w+\.(\d{4}\.\d{2}\.\d{2})\.pdf")
    dates = set()
    for pdf in pdfs:
        m = r.match(pdf)
        if m:
            dates.add(m.group(1))
    return dates


PROXY_URL = conf.BotConfig.proxy


async def download_file(url):
    fname = url.split("/")[-1]
    with warnings.catch_warnings():  # aiohttp TLS in TLS crazy stuff...
        async with aiohttp.ClientSession(trust_env=True) as session:
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            async with session.get(url, proxy=PROXY_URL) as resp:
                assert resp.status == 200
                data = await resp.read()
                async with aiofiles.open(
                    os.path.join(file_browser_path, fname), "wb"
                ) as outfile:
                    await outfile.write(data)


REPO = "awesome-english-ebooks"


@scheduler.scheduled_job(
    "interval",
    name="检查经济学人PDF",
    next_run_time=datetime.datetime.now(),
    hours=12,
    misfire_grace_time=60,
)
async def download_more_pdfs():
    existed = get_pdf_dates(get_pdfs())
    log.info("开始检查经济学人PDF新资源")
    for content in list_repo_path(REPO, "01_economist"):
        name = content["name"]
        if name.startswith("te_"):
            date = name.replace("te_", "")
            if date not in existed:
                path = content["path"]
                files = list_repo_path(REPO, path)
                # find pdf
                mag_pdf = next(
                    f["download_url"] for f in files if f["name"].endswith(".pdf")
                )
                await download_file(mag_pdf)
                log.success(f"{date} download ok")
            else:
                log.debug(f"{date} already exist")
    log.info("检查完成!")


if __name__ == "__main__":
    asyncio.run(download_more_pdfs())
