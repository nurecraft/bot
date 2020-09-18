from loguru import logger

from aiogram import types

from app.misc import dp

from app.models.user import User

from app.services.rcon import RCONCommandSender


@dp.message_handler(commands=["register"])
async def command_register(message: types.Message, user: User):

    if not types.ChatType.is_private(message):
        reply_markup = None
        if message.get_args():
            await message.delete()

        if user.mc_username and not message.reply_to_message:
            answer_text = (
                f"Ти вже зареєстрований з нікнеймом - <b>{user.mc_username}</b>!\n\n"
                "Але нагадаю, що для реєстрації "
                "необхідно перейти в діалог з ботом @nurecraft_bot та повторити команду особисто."
            )
        else:
            answer_text = (
                "Для реєстрації на сервері "
                "перейдіть в діалог з ботом @nurecraft_bot та повторіть команду.\n\n"
                "Або просто натисніть кнопку:"
            )
            reply_markup = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton("Відкрити бота", url="https://t.me/nurecraft_bot?start=register")
                ]
            ])

        return await message.answer(
            answer_text,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )

    logger.info(
        "User {user_id} try to register {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    if user.mc_username:
        return await message.reply(
            "Ти вже зареєстрований на сервері з нікнеймом: "
            f"<b>{user.mc_username}</b>"
        )

    command = message.get_command()
    args = message.get_args().split()
    if 0 >= len(args) or len(args) > 2:
        return await message.reply(
            f"Напиши своє повідомлення так: <pre>{command} username "
            "password</pre>\n\nДе <b>username</b> - бажаний нікнейм на "
            "сервері, <b>password</b> - твій бажаний пароль."
        )

    username, password = args

    await message.chat.do("typing")

    try:
        responce = RCONCommandSender.send(
            "authme register {username} {password}".format(
                username=username,
                password=password
            )
        )
        logger.info("Server /register response: " + responce)

    except:
        return await message.answer("Сервер вимкнено, спробуй пізніше..")

    is_success = "пройшла успішно!" in responce
    await message.reply(
        responce + 'Тепер ти можеш грати на сервері!'
        if is_success else
        responce
    )

    if is_success:
        await user.update(mc_username=username).apply()

    return True
