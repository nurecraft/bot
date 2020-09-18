from typing import List

from aiogram import types

from app.misc import dp
from app.services.rcon import RCONCommandSender
from app.utils.superuser import create_super_user

from app.models.user import User


@dp.message_handler(
    types.ChatType.is_private,
    commands=["set_superuser"],
    is_superuser=True
)
async def cmd_superuser(message: types.Message):
    args = message.get_args()
    if not args or not args[0].isdigit():
        return False
    args = args.split()
    user_id = int(args[0])
    remove = len(args) == 2 and args[1] == "-rm"

    try:
        result = await create_super_user(user_id=user_id, remove=remove)
    except ValueError:
        result = False

    if result:
        return await message.answer(
            "Пользователь {user} теперь {is_superuser} администратор".format(
                is_superuser="" if not remove else "не", user=user_id
            )
        )
    return await message.answer(
        "Не получилось назначить {is_superuser} администратором пользователя {user}".format(
            is_superuser="" if not remove else "не", user=user_id
        )
    )


@dp.message_handler(
    types.ChatType.is_private,
    commands=["server"],
    is_superuser=True
)
async def cmd_server(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("Please send command.")
        return
    responce = RCONCommandSender.send(args)
    await message.reply(responce or "No responce.")


@dp.message_handler(
    commands=['find'],
    is_superuser=True
)
async def command_find(message: types.Message):
    args = message.get_args()
    users: List[User] = await User.query.where(User.mc_username.contains(args)).gino.all()

    user_lines = [
        user.first_name + " " + (user.last_name or "")
        + " (" + user.mc_username + ") - "
        + ("@" + user.username if user.username else "id: " + str(user.id))
        for user in users
    ]
    await message.reply(
        "З таким ніком:\n"
        + "\n".join(user_lines) if user_lines else "нікого не знайдено"
    )
