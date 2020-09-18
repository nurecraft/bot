from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from app.models.user import User

class ACLMiddleware(BaseMiddleware):
    async def setup_chat(self, data: dict, tg_user: types.User, chat: Optional[types.Chat] = None):
        user_id = tg_user.id

        user = await User.get(user_id)
        if user is None:
            user = await User.create(
                id=user_id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username
            )

        data["user"] = user

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_chat(data, query.from_user, query.message.chat if query.message else None)
