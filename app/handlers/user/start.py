from loguru import logger

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from app.misc import dp

from app.models.user import User

from app.handlers.user.register import command_register
from app.handlers.user.link_mc_account import command_link

from app.utils.about_server import info_buttons


@dp.message_handler(CommandStart("register"))
async def command_start(message: types.Message, user: User):
    return await command_register(message, user)


@dp.message_handler(CommandStart("link"))
async def command_start(message: types.Message, user: User):
    return await command_link(message, user)


@dp.message_handler(CommandStart())
async def command_start(message: types.Message, user: User):
    logger.info(
        "User {user_id} start conversation {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    if types.ChatType.is_private(message):
        await user.update(start_conversation=True).apply()

    is_registered = bool(user.mc_username)
    register_msg = (
        "Для реєстрації на сервері використовуй команду <pre>/register</pre> "
        "й додавай свій бажаний нікнейм і пароль.\n"
        "Ось так: /register username password\n\n"
    )

    await message.answer(
        "Привіт! Я бот серверу NURECRAFT, ось інформація яка допоможе почати "
        "грати на нашому проекті:\n\n"
        "{register}" # Insert registration tutorial for not registered users
        "<b>IP серверу</b>: <pre>vanilla.nurecraft.ml</pre>\n"
        "Команди ботa: /help\n".format(
            register="" if is_registered else register_msg
        ),
        parse_mode="html",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=info_buttons),
        disable_web_page_preview=True
    )
    return True


