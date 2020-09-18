from loguru import logger

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from app.misc import dp

from app.models.user import User


cb_linking = CallbackData("tgb", "action", "mc_username")


@dp.message_handler(
    commands=["link"]
)
async def command_link(message: types.Message, user: User):
    logger.info(
        "User {user_id} start linking.",
        user_id=message.from_user.id
    )
    reply_to_msg = False
    reply_markup = None

    await message.chat.do("typing")

    # Message in Group
    is_group_chat_msg = not types.ChatType.is_private(message)
    if is_group_chat_msg and message.get_args():
        await message.delete()
        answer_text = (
            f"{message.from_user.get_mention()}, cпробуй надіслати те саме, але в чаті гри! 😂"
        )

    elif is_group_chat_msg and user.mc_username and not message.reply_to_message:
        answer_text = (
            f"Я знаю твій нікнейм - {user.mc_username}!\n\n"
            "Але нагадаю, що для зв'язування Minecraft аккаунту та Телеграм акаунту "
            "необхідно перейти в діалог з ботом @nurecraft_bot та повторити команду особисто."
        )
        reply_to_msg = True

    elif is_group_chat_msg:
        answer_text = (
            "Для зв'язування Minecraft аккаунту та Телеграм акаунту "
            "перейдіть в діалог з ботом @nurecraft_bot та повторіть команду.\n\n"
            "Або просто натисніть кнопку:"
        )
        reply_markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton("Відкрити бота", url="https://t.me/nurecraft_bot?start=link")
            ]
        ])
        reply_to_msg = True

    # Message in Private chat
    elif user.mc_username:
        answer_text = (
            f"До твого Телеграму акаунту вже прив'язано нік \"<b>{user.mc_username}</b>\" "
            "якщо ти хочет прив'язати інший нік, то виповни команду в чаті Minecraft:\n\n"
            f"<pre>/link {message.from_user.id}</pre>"
        )

    else:
       answer_text = (
            "Щоб я запам'ятав твій нік на сервері, будь ласка, скопіюй та "
            "надішли наступну команду в чаті Minecraft:\n\n"
            f"<pre>/link {message.from_user.id}</pre>"
        )

    await message.answer(
        answer_text,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=reply_markup,
        reply=reply_to_msg
    )
    return True


@dp.callback_query_handler(
    lambda cbq: types.ChatType.is_private(cbq.message),
    cb_linking.filter()
)
async def cq_linking(query: types.CallbackQuery, callback_data: dict, user: User):
    logger.info(
        "User {user_id} try to link Minecraft account to Telegram user.",
        user_id=query.from_user.id
    )

    if user.mc_username:
        query_answer_text = "Я пам'ятаю твій нікнейм."

        new_message_text = (
            f"Твій нік на сервері вже збережено - <b>{user.mc_username}</b>!"
        )

    else:
        await user.update(mc_username=callback_data["mc_username"]).apply()

        query_answer_text = "Я запам'ятав твій нікнейм!"
        new_message_text = (
            f"Я запам'ятав, що твій нік на сервері - <b>{user.mc_username}</b>!"
        )

    await query.answer(query_answer_text)

    await query.message.edit_text(new_message_text, reply_markup=None)
