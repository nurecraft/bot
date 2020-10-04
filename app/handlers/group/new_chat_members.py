import asyncio
import datetime
from contextlib import suppress
from random import shuffle

from aiogram import types
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest, MessageCantBeDeleted
from loguru import logger

from app.services.apscheduller import scheduler

from app.misc import dp
from app.models.user import User
from app.services.join_list import join


DEFAULT_HELLO_MSG = (
    '{username}, ласкаво просимо в чат серверу NURECRAFT.\n\n'
    '<b>Ти сам звідки?</b>\n'
    '<i>(ти не зможеш нічого надіcлати, якщо не натиснеш кнопку, а також тебе буде вилучено з групи)</i>'
)

cb_join = CallbackData("join_chat", "id", "answer")


@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_chat_member(message: types.Message, user: User):

    # Delete "New member" notification
    with suppress(MessageCantBeDeleted):
        await message.delete()

    added_member_ids = [new_user_.id for new_user_ in message.new_chat_members]
    logger.info(
        "Received new chat member notification with {users} in chat {chat_id}",
        users=added_member_ids,
        chat_id=message.chat.id
    )
    if message.bot.id in added_member_ids:
        logger.warning(
            "User {user_id} try to add bot to chat {chat_id} {chat_name}",
            user_id=user.id,
            chat_id=message.chat.id,
            chat_name=message.chat.title,
        )
        # Not superuser add bot to group
        if not user.is_superuser:
            await message.bot.leave_chat(message.chat.id)
            logger.info(
                "Bot leave chat {chat_id} {chat_name}",
                chat_id=message.chat.id,
                chat_name=message.chat.title,
            )
            return True
        return True

    for new_member in message.new_chat_members:
        try:
            await message.chat.restrict(
                new_member.id,
                can_send_messages=False,
                can_send_other_messages=False,
                can_send_media_messages=False,
                can_add_web_page_previews=False
            )

        except BadRequest as e:
            logger.error(
                "Cannot restrict chat member {user} in chat {chat} with error: {error}",
                user=new_member.id,
                chat=message.chat.id,
                error=e,
            )
            continue

        buttons = [
            types.InlineKeyboardButton(text="ХНУРЕ", callback_data=cb_join.new(id=str(new_member.id), answer="nure")),
            types.InlineKeyboardButton(text="ХПИ", callback_data=cb_join.new(id=str(new_member.id), answer="khpi")),
            types.InlineKeyboardButton(text="ХАИ", callback_data=cb_join.new(id=str(new_member.id), answer="hai")),
            types.InlineKeyboardButton(text="Что?", callback_data=cb_join.new(id=str(new_member.id), answer="hz"))
        ]
        shuffle(buttons)
        # Отправить приветствие
        msg = await message.answer(
            DEFAULT_HELLO_MSG.format(
                username=new_member.get_mention(as_html=True),
                chat_title=message.chat.title
            ),
            parse_mode="HTML",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[buttons]),
        )
        # Поставить удаление в работу
        await join.create_task(
            chat_id=message.chat.id, message_id=msg.message_id, prefix="join", user_id=new_member.id
        )

    return True


@dp.callback_query_handler(cb_join.filter())
async def cq_new_member(query: types.CallbackQuery, callback_data: dict):
    cb_user_id = int(callback_data["id"])
    if cb_user_id != query.from_user.id:
        await query.answer("Сообщение не тебе!")
        return True

    await query.message.edit_reply_markup(None)

    JOB_PREFIX = "join_cleaner"
    job_key = f"{JOB_PREFIX}:join:{query.message.chat.id}:{query.from_user.id}"
    scheduler.remove_job(job_key)

    await asyncio.sleep(2)

    if callback_data["answer"] == "nure":
        logger.info(
            "User {user} confirm new member check in chat {chat}",
            user=query.from_user.id,
            chat=query.message.chat.id,
        )

        APPROVE_MESSAGE_TEMPLATE = (
            "Схоже, {username}, ти свій!\n\n"
            "<b>Рекомендую</b> тобі почати звідси: http://nurecraft.ml"
        )
        await query.message.edit_text(
            APPROVE_MESSAGE_TEMPLATE.format(
                username=query.from_user.get_mention(as_html=True)
            ),
            reply_markup=None
        )

        await query.answer("О, свої!")
        try:
            await query.message.chat.restrict(
                query.from_user.id,
                can_send_messages=True,
                can_send_other_messages=True,
                can_send_media_messages=True,
                can_add_web_page_previews=True
            )
        except BadRequest as e:
            logger.error(
                "Cannot restrict chat member {user} in chat {chat} with error: {error}",
                user=new_member.id,
                chat=message.chat.id,
                error=e,
            )

    else:
        logger.info(
            "User {user} kicked in chat {chat}",
            user=query.from_user.id,
            chat=query.message.chat.id
        )

        DECLINE_MESSAGE_TEMPLATE = (
            "{username} виявився засланим козачком.."
        )
        await query.message.edit_text(
            DECLINE_MESSAGE_TEMPLATE.format(
                username=query.from_user.get_mention(as_html=True)
            ),
            reply_markup=None
        )

        await query.answer("Вам не сюди..")
        await query.message.chat.kick(query.from_user.id)

        await asyncio.sleep(30)
        await query.message.chat.unban(query.from_user.id)

    return True
