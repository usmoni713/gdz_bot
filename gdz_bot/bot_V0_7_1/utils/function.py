from filters.ferma_callbacks import *
from pprint import pprint
from GdzAPI import gdz_api
import logging
from bot_V0_7_1.utils.levels import levels
from aiogram.types import CallbackQuery
from handlers.user import responder as rs

logger = logging.getLogger(__name__)
logger.info("started!")
from database import setupV3 as database


async def one_level_back(
    level: str, callback: CallbackQuery, user_id: int, db: database.Database
):
    """Функция, которая обрабатывает нажатие кнопки "назад" на различных уровнях."""
    if level == levels.choose_obj:
        await rs.start(message=callback.message)
        # Go to the start of conversation.

    elif level == levels.turn_over:
        await callback.message.delete()
        # Delete turn over message and send object message.
        user_class = await db.get_user_class(user_id=user_id)
        await rs.send_obj(callback=callback, user_class=user_class, edit_text=False)

    elif level == levels.choose_section:
        await callback.message.delete()
        # Delete section message and turn over.
        await rs.turn_over(callback=callback, user_id=user_id, db=db)

    elif level == levels.choose_number:
        await rs.save_book_get_section(
            callback=callback, user_id=user_id, edit_text=True, db=db
        )
        # Save book with new section number and get section.


async def get_instance__dc_for_choose_book(
    db: database.Database,
    for_sl_book: bool = False,
    user_id: int = 1234,
) -> gdz_api.Book:
    """Функция, которая возвращает книгу из списка книг пользователя для выбора.
    Возвращает экземпляр книги."""

    c = await db.get_user_auxiliary_variable(user_id=user_id)
    if not for_sl_book:
        user_chapter = await db.get_user_chapter(user_id=user_id)
    else:
        user_chapter = await db.get_user_selected_books(user_id=user_id)
    if c > len(user_chapter):
        c = c % len(user_chapter)
    user_book = user_chapter[c]
    return user_book


async def delete_unnecessary_data(
    db: database.Database,
    user_id: int = 1234,
) -> None:
    """Функция, которая удаляет ненужные данные из словаря пользователя"""

    await db.update_user_auxiliary_variable_in_database(
        user_id=user_id, auxiliary_variable=0
    )
    await db.update_user_chapter_in_database(user_id=user_id, user_books=[])
    await db.update_user_selected_book_in_database(user_id=user_id, user_book=None)
    await db.update_user_section_in_database(user_id=user_id, user_section=None)


async def get_all_unique_authors(ls_books: list[gdz_api.Book]) -> list[str]:
    """Функция, которая возвращает список уникальных авторов."""
    ls_authors = []
    for book in ls_books:
        for author in book.authors:
            ls_authors.append(author)
    return list(set(ls_authors))


async def split_buttons(ls_numbers: list[gdz_api.Number]):
    """Функция, которая генерирует клавиатуру с выбором номера страницы"""
    hp = 0
    current_position = 0
    stucture_of_buttons = [[]]
    for sec in ls_numbers:
        hp += 1
        sec_data: str = ""

        if hp > 84:
            current_position += 1
            stucture_of_buttons.append([])
            hp = 0

        for n in sec.num:

            if (len(sec_data.encode("utf-8")) + len(n.encode("utf-8"))) > 57:
                break

            else:
                sec_data += n

        stucture_of_buttons[current_position].append(sec_data)
    # await inform(stucture_of_buttons)

    return stucture_of_buttons


async def inform(text) -> None:
    """Функция, которая отправляет сообщение на терминал для DEBUG."""
    print("\n\tDEBUG\n\n")
    pprint(text)
    print("\n\tDEBUG\n")
