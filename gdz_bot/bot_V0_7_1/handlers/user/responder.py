from typing import Any
from bot_V0_7_1.keyboards import buttons as buttons_gdz
from utils import function
import sys

sys.path.append("d:\\fast-gdz\\gdz_bot")
# D:\fast-gdz\gdz_bot
from GdzAPI import gdz_api
from filters import ferma_callbacks
from database import setupV3 as database

# from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_media_photo import InputMediaPhoto


async def start(message: Message, edit_text: bool = True):
    """Функция, которая отправляет приветственное сообщение
    и клавиатуру выбора класса. Возвращает None."""
    (
        await message.edit_text(
            f"Добро пожаловать!\nКласс:",
            reply_markup=buttons_gdz.choice_num_class,
        )
        if edit_text
        else await message.answer(
            f"Добро пожаловать!\nКласс:",
            reply_markup=buttons_gdz.choice_num_class,
        )
    )


async def send_obj(
    callback: CallbackQuery, user_class: int = 1, edit_text: bool = True
):
    """Функция, которая отправляет сообщение с выбором предмета
    на основе переданных данных пользователя. Возвращает None."""
    ls_chapters = await gdz_api.Api().get_available_chapters()
    ls_chapters = ls_chapters[str(user_class)]
    ls_obj = []
    for chapter in ls_chapters:
        ls_obj.append(chapter.subject)
    (
        await callback.message.edit_text(
            f"class: {user_class}\nвыберите предмет:",
            reply_markup=await buttons_gdz.create_bt_chooce_obj(list_of_obj=ls_obj),
        )
        if edit_text
        else await callback.message.answer(
            f"class: {user_class}\nвыберите предмет:",
            reply_markup=await buttons_gdz.create_bt_chooce_obj(list_of_obj=ls_obj),
        )
    )
    await callback.answer()


async def save_obj_get_author(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_obj_CallbackFactory,
    user_id: int = 1234,
    db: database.Database | None = None,
):
    """Функция, которая отправляет сообщение с выбором предмета
    на основе переданных данных пользов
    need_to_close_connection = Falseателя. Возвращает None."""
    need_to_close_connection = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_to_close_connection = True
    user_class = await db.get_user_class(user_id=user_id)
    chapter: gdz_api.Chapter = await gdz_api.Api().get_chapter(
        chapter_class=user_class, chapter_subject=callback_data.obj
    )
    await chapter.get_books()
    authors = await function.get_all_unique_authors(ls_books=chapter.books)

    await callback.message.edit_text(
        text=f"Выберите одного автора вашего учебника:",
        reply_markup=await buttons_gdz.creat_bt_choose_author(
            ls_authors=authors, db=db
        ),
    )
    await db.update_user_obj_in_database(user_id=user_id, user_obj=callback_data.obj)
    await callback.answer()
    if need_to_close_connection:
        db.need_close_conn = True
        await db._close()


async def save_author_get_cgapter(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_author_CallbackFactory,
    user_id: int = 1234,
    db: database.Database | None = None,
):
    """Функция, которая отправляет сообщение с выбором предмета
    на основе переданных данных пользов
    need_to_close_connection = Falseателя. Возвращает None."""
    need_to_close_connection = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_to_close_connection = True
    user_class = await db.get_user_class(user_id=user_id)
    user_obj = await db.get_user_obj(user_id=user_id)
    chapter: gdz_api.Chapter = await gdz_api.Api().get_chapter(
        chapter_class=user_class, chapter_subject=user_obj
    )
    await chapter.get_books()
    user_books = [
        book for book in chapter.books if callback_data.author in book.authors
    ]
    await db.update_user_chapter_in_database(user_id=user_id, user_books=user_books)

    await callback.message.edit_text(
        f"автор: {callback_data.author}\nвыберите учебник:",
    )
    await db.update_user_auxiliary_variable_in_database(
        user_id=user_id,
        auxiliary_variable=0,
    )
    user_book: gdz_api.Book = await function.get_instance__dc_for_choose_book(
        user_id=user_id,
        db=db,
    )
    await function.inform(text=user_book.cover_url)
    # await db.update_user_selected_book_in_database()
    await callback.message.answer_photo(
        photo=user_book.cover_url,
        caption=f"{user_book.publisher}\n{user_book.authors}",
        reply_markup=await buttons_gdz.creat_bt_choose_book(user_id=user_id, db=db),
    )
    await callback.answer()
    if need_to_close_connection:
        db.need_close_conn = True
        await db._close()


async def save_book_get_section(
    callback: CallbackQuery,
    user_id: int,
    edit_text=False,
    db: database.Database | None = None,
) -> None:
    """Функция, которая отправляет сообщение с выбором секции
    на основе переданных данных пользователя. Возвращает None.
    """
    need_to_close_connection = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_to_close_connection = True
    user_book = await db.get_user_selected_book(
        user_id=user_id,
    )
    structure_sections = await user_book.get_num_structure()
    bt_sec = await buttons_gdz.get_bt_section(structure_sections)

    (
        await callback.message.answer(
            text="Название интересующей секции:",
            reply_markup=bt_sec,
        )
        if not edit_text
        else await callback.message.edit_text(
            text="Название интересующей секции:",
            reply_markup=bt_sec,
        )
    )
    await callback.answer()
    if need_to_close_connection:
        db.need_close_conn = True
        await db._close()


async def save_section__get_numbers(
    callback: CallbackQuery,
    user_section: str,
    user_id: int,
    db: database.Database | None = None,
) -> None:
    """Эта функция отправляет сообщение с выбором номера
    (в выбранной секции). Возвращает None.
    """
    need_to_close_connection = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_to_close_connection = True
    user_book = await db.get_user_selected_book(
        user_id=user_id,
    )
    # user_section= await db.get_user_section(user_id=user_id)
    section_structure = await user_book.get_num_structure()
    numbers = section_structure.get(user_section)
    ls_numbers = []
    if type(numbers) == dict:
        for i in numbers.values():
            for j in i:

                ls_numbers.append(j)
    elif type(numbers) == list:
        ls_numbers = list(numbers)
    await callback.message.edit_text(
        text=f"Номер: ",
        reply_markup=await buttons_gdz.get_bt_numbers(
            ls_numbers=ls_numbers,
        ),
    )
    await callback.answer()
    if need_to_close_connection:
        db.need_close_conn = True
        await db._close()


# Эта функция перелистывает страницы для выбора учебника
# Если передан параметр for_sl_book, то переход происходит
# по выбору учебников из списка.
# Также эта функция отправляет сообщение с выбором учебника.
# Если передан callback, то ответ на этот callback происходит, иначе ответ на сообщение.
# Если add_current_page != 0, то это означает, что нужно перейти на следующую
# или предыдущую страницу (add_current_page = -1 или 1 соответственно),
# иначе нужно перейти на первую страницу (add_current_page=0).
async def turn_over(
    user_id: int,
    message: Message = None,
    add_current_page: int = 0,
    for_sl_book: bool = False,
    callback: CallbackQuery = None,
    edit_text: bool = False,
    db: database.Database | None = None,
) -> None:
    """Функция, которая позволяет пользователю перелистывать
    страницы для выбора учебника. Возвр
    need_to_close_connection = Falseащает None."""
    need_to_close_connection = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_to_close_connection = True
    # c= await db.get_user_auxiliary_variable(user_id=user_id)
    c = await db.get_user_auxiliary_variable(
        user_id=user_id,
    )
    c += add_current_page
    user_chapter: list[gdz_api.Book] = (
        await db.get_user_chapter(
            user_id=user_id,
        )
        if not for_sl_book
        else await db.get_user_selected_books(
            user_id=user_id,
        )
    )
    if (c < 0) and (add_current_page == -1):
        c = len(user_chapter) - 1
    elif (c >= len(user_chapter)) and (add_current_page == 1):
        c = 0
    await db.update_user_auxiliary_variable_in_database(
        user_id=user_id,
        auxiliary_variable=c,
    )
    message: Message = callback.message if message is None else message
    user_book: gdz_api.Book = await function.get_instance__dc_for_choose_book(
        user_id=user_id, for_sl_book=for_sl_book, db=db
    )
    cover_img = user_book.cover_url
    caption = f"{user_book.title}\n{user_book.publisher}\n{user_book.authors}"

    cover = InputMediaPhoto(media=cover_img, caption=caption)
    (
        await message.edit_media(
            media=cover,
            reply_markup=await buttons_gdz.creat_bt_choose_book(
                user_id=user_id, for_sl_book=for_sl_book, db=db
            ),
        )
        if edit_text
        else await message.answer_photo(
            photo=cover_img,
            caption=caption,
            reply_markup=await buttons_gdz.creat_bt_choose_book(
                user_id=user_id, for_sl_book=for_sl_book, db=db
            ),
        )
    )
    await callback.answer() if not for_sl_book else None
    if need_to_close_connection:
        db.need_close_conn = True
        await db._close()


async def send_meny(message: Message) -> None:
    """Функция, которая отправляет сообщение с кнопками
    для выбора действий. Возвращает None."""
    await message.answer(
        text="выберите интересующий действий",
        reply_markup=await buttons_gdz.get_bt__meny(),
    )
