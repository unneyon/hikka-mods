__version__ = (1, 0, 0)
#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/gpl-3.0.html

# meta developer: @unneyon
# scope: hikka_only
# scope: hikka_min 1.6.3
# requires: git+https://github.com/tamland/python-tidal

import asyncio
import base64
import io
import json
import logging
import requests

import tidalapi
from telethon import types

from .. import loader, utils


logger = logging.getLogger(__name__)


@loader.tds
class TidalMod(loader.Module):
    """API wrapper over TIDAL Hi-Fi music streaming service"""

    strings = {
        "name": "Tidal",
        "_cfg_quality": "Select the desired quality for the tracks",
        "args": "<emoji document_id=5312526098750252863>❌</emoji> <b>Specify search query</b>",
        "404": "<emoji document_id=5312526098750252863>❌</emoji> <b>No results found</b>",
        "oauth": (
            "🔑 <b>Login to TIDAL</b>\n\n<i>This link will expire in 5 minutes</i>"
        ),
        "oauth_btn": "🔑 Login",
        "success": "✅ <b>Successfully logged in!</b>",
        "error": "❌ <b>Error logging in</b>",
        "search": "<emoji document_id=5370924494196056357>🖤</emoji> <b>{name}</b>\n<emoji document_id=6334768915524093741>⏰</emoji> <b>Release date (in Tidal):</b> <i>{release}</i>",
        "downloading_file": "\n\n<emoji document_id=5325617665874600234>🕔</emoji> <i>Downloading audio…</i>",
        "searching": "<emoji document_id=5309965701241379366>🔍</emoji> <b>Searching…</b>",
        "auth_first": "<emoji document_id=5312526098750252863>❌</emoji> <b>You need to login first</b>",
    }

    strings_ru = {
        "_cfg_quality": "Выберите желаемое качество для треков",
        "args": "<emoji document_id=5312526098750252863>❌</emoji> <b>Укажите поисковый запрос</b>",
        "404": "<emoji document_id=5312526098750252863>❌</emoji> <b>Ничего не найдено</b>",
        "oauth": (
            "🔑 <b>Авторизуйтесь в TIDAL</b>\n\n<i>Эта ссылка будет действительна в"
            " течение 5 минут</i>"
        ),
        "oauth_btn": "🔑 Авторизоваться",
        "success": "✅ <b>Успешно авторизованы!</b>",
        "error": "❌ <b>Ошибка авторизации</b>",
        "search": "<emoji document_id=5370924494196056357>🖤</emoji> <b>{name}</b>\n<emoji document_id=6334768915524093741>⏰</emoji> <b>Дата релиза (в Tidal):</b> <i>{release}</i>",
        "downloading_file": "\n\n<emoji document_id=5325617665874600234>🕔</emoji> <i>Загрузка аудио…</i>",
        "searching": "<emoji document_id=5309965701241379366>🔍</emoji> <b>Ищем…</b>",
        "auth_first": "<emoji document_id=5312526098750252863>❌</emoji> <b>Сначала нужно авторизоваться</b>",
    }


    def __init__(self):
        self.qualities = {
            "Low": tidalapi.Quality.low_96k,
            "High": tidalapi.Quality.low_320k,
            "HiFi": tidalapi.Quality.high_lossless,
            "HiFi+": tidalapi.Quality.hi_res,
            "Master": tidalapi.Quality.hi_res_lossless
        }
        self.tags_files = {
            "Low": "mp3",
            "High": "m4a",
            "HiFi": "flac",
            "HiFi+": "flac",
            "Master": "flac"
        }
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "quality",
                "HiFi",
                lambda: self.strings["_cfg_quality"],
                validator=loader.validators.Choice(["Low", "High", "HiFi", "HiFi+", "Master"]),
            )
        )


    def tidalLogin(self):
        login_credits = (
            self.get("token_type"),
            self.get("access_token"),
            self.get("refresh_token"),
            self.get("session_id")
        )
        tidal = tidalapi.Session()
        if not all(login_credits):
            return tidal

        try:
            tidal.load_oauth_session(*login_credits)
            if tidal.check_login():
                tidal.audio_quality = self.qualities.get(self.config['quality'], "High")
                return tidal
            return tidalapi.Session()
        except:
            logger.exception("Error loading OAuth session")
            return tidalapi.Session()


    @loader.command(
        ru_doc="Авторизация в TIDAL"
    )
    async def tlogincmd(self, message: types.Message):
        """Open OAuth window to login into TIDAL"""
        tidal_session = self.tidalLogin()
        result, future = tidal_session.login_oauth()
        form = await self.inline.form(
            message=message,
            text=self.strings("oauth"),
            reply_markup={
                "text": self.strings("oauth_btn"),
                "url": f"https://{result.verification_uri_complete}",
            },
            gif="https://0x0.st/oecP.MP4",
        )

        outer_loop = asyncio.get_event_loop()

        def callback(*args, **kwargs):
            nonlocal form, outer_loop
            if tidal_session.check_login():
                asyncio.ensure_future(
                    form.edit(
                        self.strings("success"),
                        gif="https://c.tenor.com/IrKex2lXvR8AAAAC/sparkly-eyes-joy.gif",
                    ),
                    loop=outer_loop,
                )
                self.set("token_type", tidal_session.token_type)
                self.set("session_id", tidal_session.session_id)
                self.set("access_token", tidal_session.access_token)
                self.set("refresh_token", tidal_session.refresh_token)
            else:
                asyncio.ensure_future(
                    form.edit(
                        self.strings("error"),
                        gif="https://i.gifer.com/8Z2a.gif",
                    ),
                    loop=outer_loop
                )

        future.add_done_callback(callback)


    @loader.command(
        ru_doc="<запрос> - Поиск трека в TIDAL"
    )
    async def tidalcmd(self, message: types.Message):
        """<query> - Search TIDAL"""

        tidal_session = self.tidalLogin()
        if not await utils.run_sync(tidal_session.check_login):
            await utils.answer(message, self.strings("auth_first"))
            return

        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("searching"))

        result = tidal_session.search(query=query)
        if not result or not result.get('tracks'):
            await utils.answer(message, self.strings("404"))
            return

        track = result['tracks'][0]
        track_res = {
            "url": None, "id": track.id,
            "artists": [], "name": track.name,
            "tags": [], "duration": track.duration
        }

        meta = (
            tidal_session.request.request(
                "GET",
                f"tracks/{track_res['id']}",
            )
        ).json()

        artists = track_res['artists']
        for i in meta["artists"]:
            if i['name'] not in artists:
                artists.append(i['name'])
        full_name = f"{', '.join(artists)} - {track_res['name']}"

        tags = track_res['tags']
        if meta.get("explicit"):
            tags += ["#explicit🤬"]
        if isinstance(meta.get("audioModes"), list):
            for tag in meta["audioModes"]:
                tags += [f"#{tag}🎧"]
        if tags:
            track_res['tags'] = tags

        text = self.strings("search").format(
            name=utils.escape_html(full_name),
            release=track.tidal_release_date.strftime(
                "%d.%m.%Y"
            )
        )
        message = await utils.answer(
            message, text + self.strings("downloading_file")
        )

        q = self.qualities.get(self.config['quality'], "HIGH")
        q = q.value if type(q) != str else q
        t = tidal_session.request.request(
            "GET",
            f"tracks/{track_res['id']}/playbackinfopostpaywall",
            {
                "audioquality": q,
                "playbackmode": "STREAM",
                "assetpresentation": "FULL"
            }
        ).json()
        man = json.loads(base64.b64decode(t['manifest']).decode('utf-8'))
        track_res['url'] = man['urls'][0]
        track_res['tags'].append(f"#{q}🔈")

        with requests.get(track_res['url']) as r:
            audio = io.BytesIO(r.content)
            audio.name = f"audio.{self.tags_files.get(self.config['quality'], 'mp3')}"
            audio.seek(0)

        text += f"\n\n{', '.join(track_res['tags'])}"
        text += f"\n\n<emoji document_id=5359582743992737342>🎵</emoji> " \
                f"<b><a href='https://tidal.com/browse/track/{track_res['id']}'>Tidal</a></b>"

        await utils.answer_file(
            message, audio, text,
            attributes=([
                types.DocumentAttributeAudio(
                    duration=track_res['duration'],
                    title=track_res['name'],
                    performer=', '.join(track_res['artists'])
                )
            ])
        )