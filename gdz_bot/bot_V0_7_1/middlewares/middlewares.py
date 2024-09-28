from bot_V0_7_1.keyboards.buttons import btn_subscribe
from typing import Any, Awaitable, Callable, Dict
from aiogram.types.chat_member_banned import ChatMemberStatus
from database import setupV3 as database
import config

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


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


class CheckNewUser(BaseMiddleware):
    """Класс-посредник, который проверяет,
    является ли пользователь новым, и при
    необходимости добавляет его в базу данных."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Вызывает хэндлер, если пользователь
        является новым, и добавляет его в базу данных."""

        user: User = data.get("event_from_user")
        db = database.Database(
            db_name=config.db_name,
            db_user=config.db_user,
            db_password=config.db_password,
            db_host=config.db_host,
            db_port=config.db_port,
        )
        await db._connect()
        db.need_close_conn = True

        # Проверяем, является ли пользователь новым
        if not await db.chec_user_in_database(user_id=user.id):
            # Если пользователь новый, то добавляем его
            # в базу данных
            await db.add_new_user_in_database(user_id=user.id, class_=0)

        data["user_id"] = user.id
        data["db"] = db
        data["db_conn"] = db._conn

        # Проверяем, подписан ли пользователь
        # на канал
        member = await user.bot.get_chat_member(chat_id="@kaif_gdz", user_id=user.id)
        if not await check_sub_channal(member.status):
            # Если пользователь не подписан, то
            # отправляем сообщение с просьбой
            # подписаться
            await user.bot.send_message(
                user.id,
                text="Чтобы получить доступ к функциям бота, необходимо подписаться на ресурсы:",
                reply_markup=btn_subscribe,
            )
            db.need_close_conn = False
            await db._close()
            return

        # Вызываем хэндлер
        result = await handler(event, data)

        db.need_close_conn = False
        await db._close()

        return result
