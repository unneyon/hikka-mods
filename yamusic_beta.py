__version__ = (1, 0, "1b")
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
# requires: aiohttp asyncio requests git+https://github.com/MarshalX/yandex-music-api

import aiohttp
import asyncio
import io
import json
import logging
import re
import requests
import uuid
import yandex_music

import telethon
from telethon import types

from .. import loader, utils


logger = logging.getLogger(__name__)



class YaMusicMod(loader.Module):
    """The module for Yandex.Music streaming service [BETA]"""

    strings = {
        "name": "YaMusic [BETA]",
        "no_token": "<emoji document_id=5312526098750252863>❌</emoji> <b>You didn't specify the access token in the config!</b>",
        "autobio_e": "<emoji document_id=5429189857324841688>🎧</emoji> <b>Autobio is on now</b>",
        "autobio_d": "<emoji document_id=5429189857324841688>🎧</emoji> <b>Autobio is off now</b>",
        "there_is_no_playing": "<emoji document_id=5210956306952758910>👀</emoji> <b>You don't " \
                               "listening to anything right now.</b>",
        "queue_types": {
            "VARIOUS": "Your queue",
            "RADIO": "«My Wave»",
            "PLAYLIST": "Playlist «{}»",
            "ALBUM": "Album «{}»"
        },
        "now": "<emoji document_id=5438616889632761336>🎧</emoji> <b>{performer} — {title}</b>\n\n" \
               "<emoji document_id=5407025283456835913>📱</emoji> <b>Now is listening on</b> <code>{device}" \
               "</code>\n" \
               "<emoji document_id=5431736674147114227>🗂</emoji> <b>Playing from:</b> {playing_from}\n\n" \
               "<emoji document_id=5429189857324841688>🎵</emoji> <b><a href=\"https://music.yandex.ru/" \
               "album/{album_id}/track/{track_id}\">Yandex.Music</a> | <a href=\"https://song.link/ya/{track_id}\">song.link</a></b>",
        "search": "<emoji document_id=5438616889632761336>🎧</emoji> <b>{performer} — {title}</b>\n" \
               "<emoji document_id=5429189857324841688>🎵</emoji> <b><a href=\"https://music.yandex.ru/" \
               "album/{album_id}/track/{track_id}\">Yandex.Music</a> | <a href=\"https://song.link/ya/{track_id}\">song.link</a></b>",
        "downloading": "\n\n<emoji document_id=5325617665874600234>🕔</emoji> <i>Downloading audio…</i>",
        "args": "<emoji document_id=5312526098750252863>❌</emoji> <b>Specify search query</b>",
        "404": "<emoji document_id=5312526098750252863>❌</emoji> <b>No results found</b>",
        "searching": "<emoji document_id=5309965701241379366>🔍</emoji> <b>Searching…</b>",
        "guide": "<emoji document_id=6334657396698253102>📜</emoji> <b><a " \
                 "href=\"https://github.com/MarshalX/yandex-music-api/discussions/513" \
                 "#discussioncomment-2729781\">Guide for obtaining a Yandex.Music token</a></b>",
        "invalid_message_link": "<emoji document_id=5312383351217201533>⚠️</emoji> " \
                                "<b>You have specified an incorrect link, or do not have access " \
                                "to the chat where the message/post was published! Try again</b>",
        "widget_added": "<emoji document_id=5314250708508220914>✅</emoji> <b>Widget was created! " \
                        "Use <code>{prefix}ywidget {link}</code> to disable it</b>",
        "widget_disabled": "<emoji document_id=5258130763148172425>🗑</emoji> <b>Widget was disabled! " \
                        "Use <code>{prefix}ywidget {link}</code> to enable it</b>",
        "widgets_enabled": "<emoji document_id=5440895653251129804>😎</emoji> <b>All widgets was enabled! " \
                           "Use <code>{prefix}yautomsg</code> to disable it</b>",
        "widgets_disabled": "<emoji document_id=5242500556819274882>⛔️</emoji> <b>All widgets was disabled! " \
                            "Use <code>{prefix}yautomsg</code> to enable it</b>",
        "_cfg_token": "Your access token of Yandex.Music",
        "_cfg_autobio": "Automatic bio template (may contain {artist} and {title})",
        "_cfg_no_playing_bio": "Bio that is set when nothing is playing",
        "_cfg_autowidget": "Automatic widget template (may contain {artist}, {title}, {link}, {track_id}, {playing_from} and {device_name})",
        "_cfg_no_playing_widget": "Text of the widget that is placed when nothing is playing"
    }

    strings_ru = {
        "_cls_doc": "Модуль для стримингового сервиса Яндекс.Музыка [BETA]",
        "no_token": "<emoji document_id=5312526098750252863>❌</emoji> <b>Ты не " \
                    "указал токен Яндекс.Музыки в конфиге!</b>",
        "autobio_e": "<emoji document_id=5429189857324841688>🎧</emoji> <b>Автобио включено</b>",
        "autobio_d": "<emoji document_id=5429189857324841688>🎧</emoji> <b>Автобио выключено</b>",
        "there_is_no_playing": "<emoji document_id=5210956306952758910>👀</emoji> <b>Ты ничего не " \
                               "слушаешь сейчас.</b>",
        "queue_types": {
            "VARIOUS": "Ваша очередь",
            "RADIO": "«Моя Волна»",
            "PLAYLIST": "Плейлист «{}»",
            "ALBUM": "Альбом «{}»"
        },
        "now": "<emoji document_id=5438616889632761336>🎧</emoji> <b>{performer} — {title}</b>\n\n" \
               "<emoji document_id=5407025283456835913>📱</emoji> <b>Сейчас слушаю на</b> <code>{device}" \
               "</code>\n" \
               "<emoji document_id=5431736674147114227>🗂</emoji> <b>Откуда играет:</b> {playing_from}\n\n" \
               "<emoji document_id=5429189857324841688>🎵</emoji> <b><a href=\"https://music.yandex.ru/" \
               "album/{album_id}/track/{track_id}\">Яндекс.Музыка</a> | <a href=\"https://song.link/ya/{track_id}\">song.link</a></b>",
        "search": "<emoji document_id=5438616889632761336>🎧</emoji> <b>{performer} — {title}</b>\n" \
               "<emoji document_id=5429189857324841688>🎵</emoji> <b><a href=\"https://music.yandex.ru/" \
               "album/{album_id}/track/{track_id}\">Яндекс.Музыка</a> | <a href=\"https://song.link/ya/{track_id}\">song.link</a></b>",
        "downloading": "\n\n<emoji document_id=5325617665874600234>🕔</emoji> <i>Загрузка трека…</i>",
        "args": "<emoji document_id=5312526098750252863>❌</emoji> <b>Укажите поисковый запрос</b>",
        "404": "<emoji document_id=5312526098750252863>❌</emoji> <b>Ничего не найдено</b>",
        "searching": "<emoji document_id=5309965701241379366>🔍</emoji> <b>Ищем…</b>",
        "guide": "<emoji document_id=6334657396698253102>📜</emoji> <b><a " \
                 "href=\"https://github.com/MarshalX/yandex-music-api/discussions/513" \
                 "#discussioncomment-2729781\">Гайд по получению токена Яндекс.Музыки</a></b>",
        "invalid_message_link": "<emoji document_id=5312383351217201533>⚠️</emoji> " \
                                "<b>Вы указали неправильную ссылку, или не имеете доступа к чату, " \
                                "где было опубликовано сообщение/пост! Попробуйте ещё раз</b>",
        "widget_added": "<emoji document_id=5314250708508220914>✅</emoji> <b>Виджет создан! " \
                        "Чтобы его отключить, используй <code>{prefix}ywidget {link}</code></b>",
        "widget_disabled": "<emoji document_id=5258130763148172425>🗑</emoji> <b>Виджет был отключен! " \
                        "Чтобы его включить, используй <code>{prefix}ywidget {link}</code></b>",
        "widgets_enabled": "<emoji document_id=5440895653251129804>😎</emoji> <b>Все виджеты были включены! " \
                           "Чтобы их выключить, используйте <code>{prefix}yautomsg</code></b>",
        "widgets_disabled": "<emoji document_id=5242500556819274882>⛔️</emoji> <b>Все виджеты были выключены! " \
                           "Чтобы их включить, используйте <code>{prefix}yautomsg</code></b>",
        "_cfg_token": "Твой токен от Яндекс.Музыки",
        "_cfg_autobio": "Шаблон автоматического био (может содержать {artist} и {title})",
        "_cfg_no_playing_bio": "Био, которое ставится, когда ничего не играет",
        "_cfg_autowidget": "Шаблон автоматического виджета (может содержать {artist}, {title}, {link}, {track_id}, {playing_from} и {device_name})",
        "_cfg_no_playing_widget": "Текст виджета, который ставится, когда ничего не играет"
    }


    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "token",
                None,
                lambda: self.strings["_cfg_token"],
                validator=loader.validators.Hidden()
            ),
            loader.ConfigValue(
                "autobio",
                "🎧 {artist} - {title}",
                lambda: self.strings["_cfg_autobio"],
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "no_playing_bio",
                "Hello!",
                lambda: self.strings["_cfg_no_playing_bio"],
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "widget",
                "",
                lambda: self.strings["_cfg_autowidget"],
                validator=loader.validators.String()
            )
        )

    async def on_dlmod(self):
        if not self.get("guide_send", False):
            await self.inline.bot.send_message(
                self._tg_id,
                self.strings("guide").replace("<emoji document_id=6334657396698253102>📜</emoji>", "📜"),
            )
            self.set("guide_send", True)

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.ym_client = self.get_client()
        self.auth_session = False

        me = await self.client.get_me()
        self._premium = me.premium if hasattr(me, "premium") else False
        self.premium_check.start()

        if self.get("autobio", False):
            self.autobio.start()
        if self.get("automsg", False):
            self.automsg.start()

    def get_client(self):
        client = None
        if self.config['token']:
            client = yandex_music.Client(self.config['token']).init()
        return client


    @loader.loop(1800)
    async def premium_check(self):
        me = await self.client.get_me()
        self._premium = me.premium if hasattr(me, "premium") else False


    @loader.loop(30)
    async def autobio(self):
        if not self.config['token']:
            self.autobio.stop()
            return
        if not self.ym_client: self.ym_client = self.get_client()

        now = await self.get_now_playing(self.config['token'])
        track, ynison = json.loads(now[0].data), now[1]
        if len(ynison.get("player_state", {}).get("player_queue", {}).get("playable_list", [])) == 0:
            try:
                await self.client(
                    telethon.functions.account.UpdateProfileRequest(
                        about=self.config['no_playing_bio'][:(140 if self._premium else 70)]
                    )
                )
            except: pass
        elif ynison.get("player_state", {}).get("status", {}).get("paused", True):
            try:
                await self.client(
                    telethon.functions.account.UpdateProfileRequest(
                        about=self.config['no_playing_bio'][:(140 if self._premium else 70)]
                    )
                )
            except: pass

        index = ynison.get("player_state", {}).get("player_queue", {}).get("current_playable_index", 0)
        playable_list = ynison.get("player_state", {}).get("player_queue", {}).get("playable_list", [])
        playable = playable_list[index] if len(playable_list) >= index+1 else playable_list[0]

        track_info = self.ym_client.tracks(playable["playable_id"])

        bio = self.config["autobio"].format(
            artist=", ".join([x.name for x in track_info[0].artists]),
            title=track_info[0].title + (
                f" ({track_info[0].version})" if track_info[0].version else ""
            )
        )

        try:
            await self.client(
                telethon.functions.account.UpdateProfileRequest(about=bio[:(140 if self._premium else 70)])
            )
        except telethon.errors.rpcerrorlist.FloodWaitError as e:
            logger.info(f"Sleeping {max(e.seconds, 60)} bc of floodwait")
            await asyncio.sleep(max(e.seconds, 60))
            return


    @loader.loop(30)
    async def automsg(self):
        if not self.config['token']:
            self.automsg.stop()
            return

        now = await self.get_now_playing(self.config['token'])
        track, ynison = json.loads(now[0].data), now[1]
        if len(ynison.get("player_state", {}).get("player_queue", {}).get("playable_list", [])) == 0:
            return
        elif ynison.get("player_state", {}).get("status", {}).get("paused", True):
            return

        index = ynison.get("player_state", {}).get("player_queue", {}).get("current_playable_index", 0)
        playable_list = ynison.get("player_state", {}).get("player_queue", {}).get("playable_list", [])
        playable = playable_list[index] if len(playable_list) >= index+1 else playable_list[0]

        track_info = self.ym_client.tracks(playable["playable_id"])
        device = "Unknown device"
        playing_on = ynison.get("active_device_id_optional", "")
        for i in ynison.get("devices", []):
            if i['info']['device_id'] == playing_on:
                device = i['info']['title']
                break

        playing_from = self.strings("queue_types").get("RADIO")
        if "{playing_from}" in self.config["widget"]:
            playlist_name = "Любимое"
            playing_from = ynison.get("player_state", {}).get("player_queue", {}).get("entity_type", "VARIOUS")
            if playing_from == "PLAYLIST":
                playlist_id = ynison.get("player_state", {}).get("player_queue", {}).get(
                    "entity_id",
                    f"{self.ym_client.me.account.uid}:3"
                )
                playlist = self.ym_client.playlists_list(
                    playlist_id
                )
                if len(playlist) > 0:
                    playlist_name = f"<b><a href=\"https://music.yandex.ru/users/" \
                                    f"{self.ym_client.me.account.login}/playlists/" \
                                    f"{playlist_id.split(':')[1]}\">{playlist[0].title}</a></b>"
            elif playing_from == "ALBUM":
                album_id = ynison.get("player_state", {}).get("player_queue", {}).get(
                    "entity_id"
                )
                album = self.ym_client.albums(album_id)
                if len(album) > 0:
                    logger.error(album)
                    playlist_name = f"<b><a href=\"https://music.yandex.ru/album/{album[0].id}\">" \
                                    f"{album[0].title}</a></b>"
                    logger.error(playlist_name)
            playing_from = self.strings("queue_types").get(playing_from, "RADIO").format(playlist_name)

        out = self.config["widget"].format(
            artist=", ".join([x.name for x in track_info[0].artists]),
            title=track_info[0].title + (
                f" ({track_info[0].version})" if track_info[0].version else ""
            ),
            link=f"https://music.yandex.ru/album/{track_info[0].albums[0].id}/track/{track_info[0].id}",
            track_id=track_info[0].id,
            device_name=device,
            playing_from=playing_from
        )

        try:
            for widget in self.get("widgets", []):
                try:
                    msg = await self.client.get_messages(widget['chat_id'], ids=widget['message_id'])
                    await msg.edit(text=out)
                except: pass
        except telethon.errors.rpcerrorlist.FloodWaitError as e:
            logger.info(f"Sleeping {max(e.seconds, 60)} bc of floodwait")
            await asyncio.sleep(max(e.seconds, 60))
            return


    @loader.command(
        ru_doc="- Включить/выключить автобио",
        alias="yb"
    )
    async def ybio(self, message: types.Message):
        """- Enable/disable autobio"""

        if not self.config['token']:
            return await utils.answer(message, self.strings("no_token"))

        bio_now = self.get("autobio", False)
        self.set("autobio", not bio_now)
        if (not bio_now):
            self.autobio.start()
        else:
            self.autobio.stop()
            try:
                await self.client(
                    telethon.functions.account.UpdateProfileRequest(
                        about=self.config['no_playing_bio'][:(140 if self._premium else 70)]
                    )
                )
            except: pass

        await utils.answer(
            message,
            self.strings(f"autobio_{'e' if (not bio_now) else 'd'}")
        )


    @loader.command(
        ru_doc="- Гайд по получению токена Яндекс.Музыки",
        alias="yg"
    )
    async def yguide(self, message: types.Message):
        """- Guide for obtaining a Yandex.Music token"""

        await utils.answer(
            message,
            self.strings("guide")
        )


    @loader.command(
        ru_doc="- Получить трек, который играет сейчас",
        alias="yn"
    )
    async def ynow(self, message: types.Message):
        """- Get now playing track"""

        if not self.config['token']:
            return await utils.answer(message, self.strings("no_token"))
        if not self.ym_client: self.ym_client = self.get_client()

        now = await self.get_now_playing(self.config['token'])
        track, ynison = json.loads(now[0].data), now[1]
        if len(ynison.get("player_state", {}).get("player_queue", {}).get("playable_list", [])) == 0:
            return await utils.answer(message, self.strings("there_is_no_playing"))
        elif ynison.get("player_state", {}).get("status", {}).get("paused", True):
            return await utils.answer(message, self.strings("there_is_no_playing"))

        index = ynison.get("player_state", {}).get("player_queue", {}).get("current_playable_index", 0)
        playable_list = ynison.get("player_state", {}).get("player_queue", {}).get("playable_list", [])
        playable = playable_list[index] if len(playable_list) >= index+1 else playable_list[0]

        track_info = self.ym_client.tracks(playable["playable_id"])
        device = "Unknown device"
        playing_on = ynison.get("active_device_id_optional", "")
        for i in ynison.get("devices", []):
            if i['info']['device_id'] == playing_on:
                device = i['info']['title']
                break

        playlist_name = "Любимое"
        playing_from = ynison.get("player_state", {}).get("player_queue", {}).get("entity_type", "VARIOUS")
        if playing_from == "PLAYLIST":
            playlist_id = ynison.get("player_state", {}).get("player_queue", {}).get(
                "entity_id",
                f"{self.ym_client.me.account.uid}:3"
            )
            playlist = self.ym_client.playlists_list(
                playlist_id
            )
            if len(playlist) > 0:
                playlist_name = f"<b><a href=\"https://music.yandex.ru/users/" \
                                f"{self.ym_client.me.account.login}/playlists/" \
                                f"{playlist_id.split(':')[1]}\">{playlist[0].title}</a></b>"
        elif playing_from == "ALBUM":
            album_id = ynison.get("player_state", {}).get("player_queue", {}).get(
                "entity_id"
            )
            album = self.ym_client.albums(album_id)
            if len(album) > 0:
                logger.error(album)
                playlist_name = f"<b><a href=\"https://music.yandex.ru/album/{album[0].id}\">" \
                                f"{album[0].title}</a></b>"
                logger.error(playlist_name)

        out = self.strings("now").format(
            title=track_info[0].title + (
                f" ({track_info[0].version})" if track_info[0].version else ""
            ),
            performer=", ".join([x.name for x in track_info[0].artists]),
            device=device,
            playing_from=self.strings("queue_types").get(playing_from, "RADIO").format(playlist_name),
            album_id=track_info[0].albums[0].id, track_id=track_info[0].id
        )
        logger.error(out)
        message = await utils.answer(message, out+self.strings("downloading"))

        info = self.ym_client.tracks_download_info(track_info[0].id, True)
        link = info[0].direct_link
        audio = None
        audio = io.BytesIO((await utils.run_sync(requests.get, link)).content)
        audio.name = "audio.mp3"

        await utils.answer_file(
            message=message, file=audio, caption=out,
            attributes=([
                types.DocumentAttributeAudio(
                    duration=int(track_info[0].duration_ms / 1000),
                    title=track_info[0].title,
                    performer=", ".join([x.name for x in track_info[0].artists])
                )
            ])
        )


    @loader.command(
        ru_doc="<запрос> - Поиск трека в Яндекс.Музыке",
        alias="yq"
    )
    async def ysearch(self, message: types.Message):
        """<query> - Search track in Yandex.Music"""

        if not self.config['token']:
            return await utils.answer(message, self.strings("no_token"))
        if not self.ym_client: self.ym_client = self.get_client()

        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("args"))
            return

        message = await utils.answer(message, self.strings("searching"))

        search = self.ym_client.search(query, type_="track")
        if (not search.tracks) or (len(search.tracks.results) == 0):
            return await utils.answer(message, self.strings("404"))

        out = self.strings("search").format(
            title=search.tracks.results[0].title + (
                f" ({search.tracks.results[0].version})" if search.tracks.results[0].version else ""
            ),
            performer=", ".join([x.name for x in search.tracks.results[0].artists]),
            album_id=search.tracks.results[0].albums[0].id, track_id=search.tracks.results[0].id
        )
        message = await utils.answer(message, out+self.strings("downloading"))

        info = self.ym_client.tracks_download_info(search.tracks.results[0].id, True)
        link = info[0].direct_link
        audio = None
        audio = io.BytesIO((await utils.run_sync(requests.get, link)).content)
        audio.name = "audio.mp3"

        await utils.answer_file(
            message=message, file=audio, caption=out,
            attributes=([
                types.DocumentAttributeAudio(
                    duration=int(search.tracks.results[0].duration_ms / 1000),
                    title=search.tracks.results[0].title,
                    performer=", ".join([x.name for x in search.tracks.results[0].artists])
                )
            ])
        )


    @loader.command(
        ru_doc="- Включить все виджеты",
        alias="yam"
    )
    async def yautomsg(self, message: types.Message):
        """- Enable all widgets"""

        if self.get("automsg", False):
            self.automsg.stop()
            self.set("automsg", False)
            await utils.answer(
                message,
                self.strings("widgets_disabled").format(prefix=self.get_prefix())
            )
        else:
            self.automsg.start()
            self.set("automsg", True)
            await utils.answer(
                message,
                self.strings("widgets_enabled").format(prefix=self.get_prefix())
            )


    @loader.command(
        ru_doc="<ссылка на сообщение/пост> - Сделать сообщение/пост виджетом",
        alias="yw"
    )
    async def ywidget(self, message: types.Message):
        """<link to message/post> - Make a message/post a widget"""

        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("args"))

        curl = re.findall(r"t\.me/c/([a-zA-Z0-9_\.]+)/(\d+)", args); curl = curl[0] if curl else ""
        url = re.findall(r"t\.me/([a-zA-Z0-9_\.]+)/(\d+)", args); url = url[0] if url else ""
        if (not curl) and (not url):
            return await utils.answer(message, self.strings("invalid_message_link") + "\n\nAAAAAAAAAAAA")

        if curl:
            channel_id = int(f"-100{curl[0]}")
            post_id = int(curl[1])
        elif url:
            channel_id = (await self.client.get_entity(url[0])).id
            channel_id = int(f"-100{channel_id}") if (not str(channel_id).startswith("-100")) else channel_id
            post_id = int(url[1])
        link = f"https://t.me/c/{str(channel_id)[4:]}/{post_id}"
        widgets = self.get("widgets", [])

        if {"chat_id": channel_id, "message_id": post_id} not in widgets:
            widgets.append({"chat_id": channel_id, "message_id": post_id})
            await utils.answer(
                message,
                self.strings("widget_added").format(
                    prefix=self.get_prefix(),
                    link=link
                )
            )
        else:
            widgets.remove({"chat_id": channel_id, "message_id": post_id})
            await utils.answer(
                message,
                self.strings("widget_disabled").format(
                    prefix=self.get_prefix(),
                    link=link
                )
            )
        self.set("widgets", widgets)


    async def get_now_playing(self, token: str):
        device_info = {"app_name": "Chrome", "type": 1}
        ws_proto = {
            "Ynison-Device-Id": "wvpqyqihpxcqjdmf",
            "Ynison-Device-Info": json.dumps(device_info)
        }

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                url="wss://ynison.music.yandex.ru/redirector.YnisonRedirectService/GetRedirectToYnison",
                headers={
                    "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(ws_proto)}",
                    "Origin": "http://music.yandex.ru",
                    "Authorization": f"OAuth {token}",
                },
            ) as ws:
                recv = await ws.receive()
                data = json.loads(recv.data)

            new_ws_proto = ws_proto.copy()
            new_ws_proto["Ynison-Redirect-Ticket"] = data["redirect_ticket"]

            to_send = {
                "update_full_state": {
                    "player_state": {
                        "player_queue": {
                            "current_playable_index": -1,
                            "entity_id": "",
                            "entity_type": "VARIOUS",
                            "playable_list": [],
                            "options": {
                                "repeat_mode":"NONE"
                            },
                            "entity_context": "BASED_ON_ENTITY_BY_DEFAULT",
                            "version": {
                                "device_id": ws_proto["Ynison-Device-Id"],
                                "version": "0",
                                "timestamp_ms": "0"
                            },
                            "from_optional": ""
                        },
                        "status": {
                            "duration_ms": 0,
                            "paused": True,
                            "playback_speed": 1,
                            "progress_ms":0,
                            "version": {
                                "device_id": ws_proto["Ynison-Device-Id"],
                                "version": "0",
                                "timestamp_ms": "0"
                            }
                        }
                    },
                    "device": {
                        "capabilities": {
                            "can_be_player": False,
                            "can_be_remote_controller": True,
                            "volume_granularity": 0
                        },
                        "info": {
                            "device_id": ws_proto["Ynison-Device-Id"],
                            "type": "ANDROID",
                            "app_version": "2024.05.1 #46gpr",
                            "title": "Xiaomi",
                            "app_name": "Yandex Music"
                        },
                        "volume_info": {
                            "volume": 0
                        },
                        "is_shadow": False
                    },
                    "is_currently_active": False
                },
                "rid": str(uuid.uuid4()),
                "player_action_timestamp_ms": 0,
                "activity_interception_type": "DO_NOT_INTERCEPT_BY_DEFAULT"
            }

            async with session.ws_connect(
                url=f"wss://{data['host']}/ynison_state.YnisonStateService/PutYnisonState",
                headers={
                    "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(new_ws_proto)}",
                    "Origin": "http://music.yandex.ru",
                    "Authorization": f"OAuth {token}",
                },
                method="GET"
            ) as ws:
                await ws.send_str(json.dumps(to_send))
                await asyncio.sleep(3)

                async for message in ws:
                    ynison = json.loads(message.data)
                    player_info = {
                        "update_playing_status": {
                                "playing_status": {
                                    "progress_ms": ynison['player_state']['status']['progress_ms'],
                                    "duration_ms": ynison['player_state']['status']['duration_ms'],
                                    "paused": not ynison["player_state"]["status"]["paused"],
                                    "playback_speed": 1,
                                    "version": {
                                        "device_id": ws_proto["Ynison-Device-Id"],
                                        "version": "0",
                                        "timestamp_ms": "0"
                                    }
                                }
                            },
                            "rid": str(uuid.uuid4()),
                    }
                    await ws.send_str(json.dumps(player_info))
                    recv = await ws.receive()
                    return recv, ynison