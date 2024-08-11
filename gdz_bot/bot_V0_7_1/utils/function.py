from asyncio import sleep
import asyncio
from pprint import pprint
import sys
from typing import Any

sys.path.append("d:\\fast-gdz\\gdz_bot")
from GdzAPI import gdz_api
import bs4
import bs4, aiohttp, logging
from bot_V0_7_1.utils.levels import levels
from bot_V0_7_1.keyboards import buttons as buttons_gdz
from aiogram.types import Message, CallbackQuery
from handlers.user import responder as rs

logger = logging.getLogger(__name__)
logger.info("started!")
from database import setupV3 as database


async def one_level_back(
    level: str,
    callback: CallbackQuery,
    user_id: int,
    db: database.Database | None = None,
) -> None:
    need_close_conn = False

    if db is None:
        db = database.Database()
        await db._connect()

        need_close_conn = True
    """Функция, которая обрабатывает нажатие кнопки "назад" на различных уровнях."""
    if level == levels.choose_obj:
        await rs.start(message=callback.message)
        # Go to the start of conversation.

    elif level == levels.turn_over:
        await callback.message.delete()
        # Delete turn over message and send object message.
        user_class = await db.get_user_class(user_id=user_id)
        await rs.send_obj(callback=callback, user_class=user_class, edit_text=False)  # type: ignore

    elif level == levels.choose_section:
        await callback.message.delete()
        # Delete section message and turn over.
        await rs.turn_over(callback=callback, user_id=user_id)

    elif level == levels.choose_number:
        await rs.save_book_get_section(callback=callback, user_id=user_id, edit_text=True)  # type: ignore
        # Save book with new section number and get section.
    if need_close_conn:
        db.need_close_conn = True
        await db._close()


async def get_instance__dc_for_choose_book(
    for_sl_book: bool = False, user_id: int = 1234, db: database.Database | None = None
) -> gdz_api.Book:
    """Функция, которая возвращает книгу из списка книг пользователя для выбора.
    Возвращает экземпляр книги."""
    need_close_conn = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_close_conn = True

    c = await db.get_user_auxiliary_variable(user_id=user_id)
    if not for_sl_book:
        user_chapter = await db.get_user_chapter(user_id=user_id)
    else:
        user_chapter = await db.get_user_selected_books(user_id=user_id)
    if c > len(user_chapter):
        c = c % len(user_chapter)
    user_book = user_chapter[c]
    if need_close_conn:
        db.need_close_conn = True
        db._close()
    return user_book


async def delete_unnecessary_data(
    user_id: int = 1234, db: database.Database | None = None
) -> None:
    """Функция, которая удаляет ненужные данные из словаря пользователя"""
    need_close_conn = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_close_conn = True
    await db.update_user_auxiliary_variable_in_database(
        user_id=user_id, auxiliary_variable=0
    )
    await db.update_user_chapter_in_database(user_id=user_id, user_books=[])
    await db.update_user_selected_book_in_database(user_id=user_id, user_book=None)
    await db.update_user_section_in_database(user_id=user_id, user_section=None)
    if need_close_conn:
        db.need_close_conn = True
        await db._close()


async def inform(text) -> None:
    """Функция, которая отправляет сообщение на терминал для DEBUG."""
    print("\n\tDEBUG\n\n")
    pprint(text)
    print("\n\tDEBUG\n")
