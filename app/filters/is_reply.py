from dataclasses import dataclass

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


@dataclass
class IsReplyFilter(BoundFilter):
    """
    Filtered message should be reply to another message
    """

    key = "is_reply"

    is_reply: bool

    async def check(self, message: types.Message) -> bool:
        return self.is_reply and message.reply_to_message


@dataclass
class IsRepostFilter(BoundFilter):
    """
    Filtered message should be reply to another message
    """

    key = "is_repost"

    is_repost: bool

    async def check(self, message: types.Message) -> bool:
        return self.is_repost and (
            message.forward_date
            or message.forward_from
            or message.forward_from_chat
            or message.forward_signature
        )

