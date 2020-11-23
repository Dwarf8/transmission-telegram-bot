import telegram
import transmission_rpc as trans
from . import config, utils
from typing import Tuple


STATUS_LIST = {
    "downloading": "⏬",
    "seeding": "✅",
    "checking": "🔄",
    "check pending": "📡",
    "stopped": "🛑",
}
transClient = trans.Client(host=config.TRANSSMISION_HOST, port=9091)


def menu() -> str:
    text = (
        "List of available commands:\n"
        "/torrents - List all torrents\n"
        "/memory - Available memory\n"
    )
    return text


def get_memory() -> str:
    free_memory = trans.utils.format_size(transClient.free_space(config.DISK))
    formatted_memory = f"Вільно {round(free_memory[0], 2)} {free_memory[1]}"
    return formatted_memory


def torrent_menu(torrent_id: int) -> Tuple[str, telegram.InlineKeyboardMarkup]:
    torrent = transClient.get_torrent(torrent_id)
    text = (
        f"{torrent.name}\n"
        f"{utils.progress_bar(torrent.progress)}  {round(torrent.progress, 1)}% "
        f"{STATUS_LIST[torrent.status]}\n"
    )
    if download := torrent._fields["rateDownload"].value:
        speed = trans.utils.format_speed(download)
        text += (
            f"Time remaining: {utils.formated_eta(torrent)}\n"
            f"Download rate: {round(speed[0], 1)} {speed[1]}\n"
        )
    if upload := torrent._fields["rateUpload"].value:
        speed = trans.utils.format_speed(upload)
        text += f"Upload rate: {round(speed[0], 1)} {speed[1]}\n"
    reply_markup = telegram.InlineKeyboardMarkup(
        [
            [
                telegram.InlineKeyboardButton(
                    "🔄Reload",
                    callback_data=f"torrent_{torrent_id}_reload",
                )
            ],
            [
                telegram.InlineKeyboardButton(
                    "⏪Back",
                    callback_data="torrentsgoto_0",
                )
            ],
        ]
    )
    return text, reply_markup


def get_torrents(start_point: int = 0) -> Tuple[str, telegram.InlineKeyboardMarkup]:
    """
    Generates list of torrents with keyboard
    """
    SIZE_OF_LINE = 30
    KEYBORD_WIDTH = 5
    SIZE_OF_PAGE = 15
    torrents = transClient.get_torrents()
    torrents_count = 1
    count = start_point
    keyboard = [[]]
    column = 0
    row = 0
    torrent_list = ""
    for torrent in torrents[start_point:]:
        if torrents_count <= SIZE_OF_PAGE:
            if len(torrent.name) >= SIZE_OF_LINE:
                name = (
                    f"{torrent.name[:SIZE_OF_LINE]}.."
                    f"   {STATUS_LIST[torrent.status]}"
                )
            else:
                name = torrent.name
            torrent_list += f"{count+1}. {name}\n"
            if column >= KEYBORD_WIDTH:
                keyboard.append(list())
                column = 0
                row += 1
            keyboard[row].append(
                telegram.InlineKeyboardButton(
                    f"{count+1}", callback_data=f"torrent_{torrent.id}"
                )
            )
            column += 1
            count += 1
            torrents_count += 1
        else:
            keyboard.append(list())
            row += 1
            keyboard[row].append(
                telegram.InlineKeyboardButton(
                    "🔄Reload",
                    callback_data=f"torrentsgoto_{start_point}_reload",
                )
            )
            keyboard.append(list())
            row += 1
            if start_point != 0:
                keyboard[row].append(
                    telegram.InlineKeyboardButton(
                        "⏪Back",
                        callback_data=f"torrentsgoto_{start_point - SIZE_OF_PAGE}",
                    )
                )
            keyboard[row].append(
                telegram.InlineKeyboardButton(
                    "Next⏩",
                    callback_data=f"torrentsgoto_{count}",
                )
            )
            break
    else:
        keyboard.append(list())
        row += 1
        keyboard[row].append(
            telegram.InlineKeyboardButton(
                "🔄Reload",
                callback_data=f"torrentsgoto_{start_point}_reload",
            )
        )
        keyboard.append(list())
        row += 1
        if start_point != 0:
            keyboard[row].append(
                telegram.InlineKeyboardButton(
                    "⏪Back",
                    callback_data=f"torrentsgoto_{start_point - SIZE_OF_PAGE}",
                )
            )
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return torrent_list, reply_markup
