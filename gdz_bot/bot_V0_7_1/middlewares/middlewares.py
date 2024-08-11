from database import config as cfg
from bot_V0_7_1.keyboards.buttons import btn_subscribe
from typing import Any, Awaitable, Callable, Dict
import sys
from aiogram.types.chat_member_banned import ChatMemberStatus
from database import setupV3 as database

sys.path.append("d:\\fast-gdz\\gdz_bot")


from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class check_new_user(BaseMiddleware):
    """Класс-посредник, который проверяет,
    является ли пользователь новым, и при
    необходимости добавляет его в базу данных."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        user: User = data.get("event_from_user")
        db = database.Database()
        await db._connect()
        result_check = await db.chec_user_in_database(user_id=user.id)
        db.need_close_conn = True
        await db._close()
        if result_check is False:
            await db.add_new_user_in_database(user_id=user.id, class_=0)
        result = await handler(event, data)

        return result


class get_user_id_database(BaseMiddleware):
    """Класс-посредник, который получает данные
    пользователя из базы данных и добавляет их в
    контекст обработчика."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        user: User = data.get("event_from_user")
        data["user_id"] = user.id

        # ...

        result = await handler(event, data)
        # ...

        return result


class creat_connection_database(BaseMiddleware):
    """Класс-посредник, который создает подключение
    к базе данных и закрывает его после обработки
    запроса."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        db = database.Database()
        await db._connect()
        db.have_conn = True
        data["db"] = db
        data["db_conn"] = db._conn
        # print(f'in midleware:: db: {id(db)} db_conn: {id(data['db_conn'])}')
        # ...
        result = await handler(event, data)
        # ...
        print(db.have_conn)
        db.need_close_conn = True
        await db._close()

        return result


async def check_sub_channal(chat_member_status):
    """Функция, которая проверяет статус участия пользователя в канале.
    Возвращает True, если пользователь является участником канала,
    и False в противном случае."""
    if ((chat_member_status == ChatMemberStatus.LEFT)) or (
        chat_member_status == ChatMemberStatus.KICKED
    ):

        return False
    else:
        return True


class chec_sub(BaseMiddleware):
    """Класс-посредник, который проверяет подписку
    пользователя на канал и позволяет доступ к
    функциям бота в зависимости от статуса подписки."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        user: User = data.get("event_from_user")
        member = await user.bot.get_chat_member(chat_id="@kaif_gdz", user_id=user.id)
        res = await check_sub_channal(member.status)
        if res:
            result = await handler(event, data)
        else:
            await user.bot.send_message(
                user.id,
                text="Чтобы получить доступ к функциям бота, необходимо подписаться на ресурсы:",
                reply_markup=btn_subscribe,
            )
            return
        return result
