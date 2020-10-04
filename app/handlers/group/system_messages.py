from contextlib import suppress

from loguru import logger

from aiogram import types
from aiogram.utils.exceptions import Unauthorized

from app.misc import dp

@dp.message_handler(
    content_types=types.ContentTypes.LEFT_CHAT_MEMBER | \
    types.ContentTypes.PINNED_MESSAGE | types.ContentTypes.LOCATION | \
    types.ContentTypes.CONTACT | types.ContentTypes.PINNED_MESSAGE,
    is_superuser=False
)
async def delete_system_messages(message: types.Message):
    logger.info(
        "User {user_id} left the {chat_id}.",
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )
    if message.left_chat_member:
        notification = (
            f"Нажаль {message.from_user.get_mention()} не витримав нашої компанії.."
        )
        await message.answer(notification)

    with suppress(Unauthorized):
        await message.delete()

    return True
