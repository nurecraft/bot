from loguru import logger

from aiogram import types

from app.misc import dp
from app.config import MAIN_GROUP_ID

from app.models.user import User

from app.services.server_info import ServerInfo
from app.services.rcon import RCONCommandSender
from app.utils.about_server import info_buttons


@dp.message_handler(commands=["online"])
async def command_online(message: types.Message):
    logger.info(
        "User {user_id} get users online count from {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    await message.chat.do("typing")

    server = ServerInfo.get_info()

    information = (
        f"<b>Зараз на сервері</b>: {server.players.online} гравців"
        if server else
        "Сервер вимкнено"
    )
    await message.reply(information, parse_mode="html")
    return True


@dp.message_handler(commands=["list"])
async def command_list(message: types.Message):
    logger.info(
        "User {user_id} get users list from {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    await message.chat.do("typing")

    server = ServerInfo.get_info()

    if server:
        players = '\n' + '\n'.join(server.players.names) if server.players.names else 'нікого нема'
        information = f"<b>На сервері ({server.players.online}/{server.players.max})</b>: {players}"
    else:
        information = "Сервер вимкнено."
    await message.reply(information, parse_mode="html")
    return True


@dp.message_handler(commands=["tps", "wtf"])
async def command_tps(message: types.Message):
    logger.info(
        "User {user_id} get tps from {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    await message.chat.do("typing")

    try:
        information = RCONCommandSender.send_with_timeout("tps")
    except:
        information = "Сервер вимкнено."

    await message.reply(information, parse_mode="html")
    return True


@dp.message_handler(commands=["ip"])
async def command_ip(message: types.Message):
    logger.info(
        "User {user_id} get server ip from {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    information = "<b>IP серверу</b>: <pre>vanilla.nurecraft.ml</pre>"
    await message.reply(information, parse_mode="html")
    return True


@dp.message_handler(commands=["info"])
async def command_info(message: types.Message):
    logger.info(
        "User {user_id} get server info from {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    information = (
        "<b>IP серверу</b>: <pre>vanilla.nurecraft.ml</pre>\n\n"
        "Команди ботa: /help\n"
    )
    await message.reply(
        information,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=info_buttons)
    )
    return True


@dp.message_handler(commands=["help"])
async def command_help(message: types.Message):
    logger.info(
        "User {user_id} get help from {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    help_text = (
        "Мої команди: \n\n"
        "/info - інформація про сервер\n"
        "/ip - показати IP серверу\n"
        "/online - показати кількість гравців на сервері\n"
        "/list - отримати список гравців онлайн\n"
        "/tps - отримати TPS серверу (показник навантаження на сервер)\n"
        "/mc або /minecraft - надіслати повідомлення на сервер (працює лише в нашій группі @nure_minecraft_chat)\n"
        "/register - зареєструватись на сервері (працює лише в чаті з ботом)"
        "/link - прив'язати свій акаунт Minecraft до твого Телеграм акаунту (працює лише в чаті з ботом)"
    )
    await message.reply(help_text, parse_mode="html")
    return True


@dp.message_handler(commands=["minecraft", "mc"])
async def command_minecraft(message: types.Message, user: User):
    # Skip if not superuser sent command to private chat or not to main group
    if (not user.is_superuser and message.chat.type == "private") \
        or (message.chat.id != MAIN_GROUP_ID and message.chat.type != "private"):
        return False

    logger.info(
        "User {user_id} try to send message to Minecraft {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    if not user.mc_username:
        await message.reply(
            "Я не знаю твій нікнейм на сервері, "
            "будь ласка зв'яжи акаунти за допомогою команди /link "
            "або зареєструйся на сервері /register."
        )
        return False

    command = message.get_command()
    text = message.get_args()
    if not text:
        await message.reply(f"Напиши своє повідомлення так: {command} test")
        return False

    await message.chat.do("typing")

    try:
        responce = RCONCommandSender.send(
            "telegram-chat-response <{username} {confirmed}> {text}".format(
                username=user.mc_username,
                text=text,
                confirmed="✔" if bool(user.mc_username) else "⚠"
            )
        )
        logger.info("Server /mc response: ", responce)

        is_sent = "Message sent to Minecraft Chat." in responce

        if is_sent:
            answer = f"Повідомлення доставлено під ніком <b>{user.mc_username}</b>."

        else:
            answer = "Повідомлення не доставлено."
    except:
        answer = "Сервер вимкнено"

    await message.reply(answer)
    return True


@dp.message_handler(commands=["username"])
async def command_username(message: types.Message, user: User):
    logger.info(
        "User {user_id} get users online count from {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    await message.chat.do("typing")

    if message.reply_to_message:
        if message.reply_to_message.from_user.id == dp.bot.id:
            await message.reply("Ой, не смішно!")
            return True

        if message.reply_to_message.forward_from:
            another_user_id = message.reply_to_message.forward_from.id
        else:
            another_user_id = message.reply_to_message.from_user.id

        another_user: User = await User.get(another_user_id)
        mc_username = another_user.mc_username
    else:
        mc_username = user.mc_username

    answer = (
        f"Нік на сервері: <b>{mc_username}</b>"
        if mc_username else
        "Я таких не знаю!"
    )
    await message.reply(answer, parse_mode="html")
    return True
