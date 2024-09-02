from typing import Any
import json
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton
import sys

sys.path.append(
    "d:\\gdz_bot\\GdzApi"
)  # Добавление пути в список путей для поиска модулей
from GdzAPI import gdz_api
# from utils import function
from filters.ferma_callbacks import *
import logging
from database import setupV3 as database

logger = logging.getLogger(__name__)
logger.info("started!")


def _generate_bt_choice_class():
    """Функция, которая генерирует клавиатуру с
    выбором класса от 1 до 11."""
    builder_choice_class = InlineKeyboardBuilder()
    for i in range(1, 12):
        builder_choice_class.button(
            text=str(i), callback_data=choose_class_CallbackFactory(user_class=i)
        )

    builder_choice_class.adjust(4)
    return builder_choice_class.as_markup()


def _generate_bt_subscribe():
    """Функция, которая генерирует клавиатуру
    для подписки и проверки подписки."""
    builder_subscribe = InlineKeyboardBuilder()
    builder_subscribe.button(text="ПОДПИСАТЬСЯ", url="https://t.me/kaif_gdz")
    builder_subscribe.button(
        text="проверить подписку", callback_data="проверить подписку"
    )

    builder_subscribe.adjust(2)
    return builder_subscribe.as_markup()


choice_num_class = _generate_bt_choice_class()

btn_subscribe = _generate_bt_subscribe()


async def create_bt_chooce_obj(list_of_obj: list[str]):

    builder_choice_obj = InlineKeyboardBuilder()
    for obj in list_of_obj:
        builder_choice_obj.button(
            text=obj, callback_data=choose_obj_CallbackFactory(obj=obj.lower())
        )

    builder_choice_obj.button(
        text="< назад", callback_data=one_level_back_CallbackFactory(level="choose_obj")
    )
    builder_choice_obj.adjust(1)
    return builder_choice_obj.as_markup()


async def generate_bt__one_evel_back(level: str):
    buid = InlineKeyboardBuilder()
    buid.button(
        text="< назад", callback_data=one_level_back_CallbackFactory(level=level)
    )
    buid.adjust(1)
    return buid.as_markup()


async def get_bt_section(structure_sections: dict):
    """Функция, которая генерирует клавиатуру с выбором раздела книги."""

    section_ls = structure_sections.keys()
    # await function.inform(f"\n{section_ls=}\n")
    bt_section = InlineKeyboardBuilder()
    hp = 0
    for sec in section_ls:
        hp += 1
        if hp > 20:
            break
        sec_data: str = ""
        for i in sec:
            if (len(sec_data.encode("utf-8")) + len(i.encode("utf-8"))) > 57:
                break
            else:
                sec_data += i
        bt_section.button(
            text=sec,
            callback_data=choose_section_CallbackFactory(name_section=sec_data, c="a"),
        )

    bt_section.button(
        text="< назад",
        callback_data=one_level_back_CallbackFactory(level="choose_section"),
    )
    bt_section.adjust(1)
    return bt_section.as_markup()


async def get_bt_numbers(ls_numbers: list[gdz_api.Number],max_position: int, current_position: int = 0, ):
    """Функция, которая генерирует клавиатуру с выбором номера страницы"""
    bt_numbers = InlineKeyboardBuilder()
    

    for n in ls_numbers:

        bt_numbers.button(
            text=n,
            callback_data=choose_number_CallbackFactory(number=n),
        )

    bt_numbers.button(
        text=" < ",
        callback_data=flipping_number_CallbackFactory(max_position=max_position, current_position=current_position-1),
    )
    bt_numbers.button(
        text=" > ",
        callback_data=flipping_number_CallbackFactory(
            max_position=max_position, current_position=current_position+1
        ),
    )

    bt_numbers.button(
        text="< назад",
        callback_data=one_level_back_CallbackFactory(level="choose_number"),
    )
    structure_abjust = []
    for i in range(round(len(ls_numbers) / 6)):
        structure_abjust.append(6)
    structure_abjust.append(2)
    structure_abjust.append(1)
    bt_numbers.adjust(*structure_abjust)
    return bt_numbers.as_markup()


async def generate_bt_choose_sl_book(user_id: int, db: database.Database | None = None):
    """Функция, которая создает клавиатуру для выбора книги и перелистывания"""
    need_close_db = False
    if db is None:
        db = database.Database()
        await db._connect()
        need_close_db = True

    c = await db.get_user_auxiliary_variable(user_id=user_id)
    current_page = c + 1
    ls_selected = await db.get_user_selected_books(user_id=user_id)
    all_page = len(ls_selected)
    del ls_selected
    bt_choose_obj = InlineKeyboardBuilder()
    bt_choose_obj.button(
        text="<",
        callback_data=turn_over_CallbackFactory(
            for_sl_book=True, add_current_page=-1, name="<"
        ),
    )
    bt_choose_obj.button(
        text=f"{current_page}/{all_page}",
        callback_data=turn_over_CallbackFactory(
            for_sl_book=True, add_current_page=-1, name="integer"
        ),
    )
    bt_choose_obj.button(
        text=">",
        callback_data=turn_over_CallbackFactory(
            for_sl_book=True, add_current_page=1, name=">"
        ),
    )
    bt_choose_obj.button(
        text="выбрать",
        callback_data=choose_book_CallbackFactory(number_book=c, for_sl_book=True),
    )
    bt_choose_obj.button(
        text="удалить из списка избранных",
        callback_data=add_or_del_on_ls_selected_books_CallbackFactory(
            number_book=c,
            del_book=True,
        ),
    )

    bt_choose_obj.button(
        text="повысить приоритет",
        callback_data=increase_or_lower_priority_sl_book_CallbackFactory(
            coeficiant=-1, number_book=c
        ),
    )
    bt_choose_obj.button(
        text="понизить приоритет",
        callback_data=increase_or_lower_priority_sl_book_CallbackFactory(
            coeficiant=1, number_book=c
        ),
    )

    bt_choose_obj.button(
        text="<  назад",
        callback_data=one_level_back_CallbackFactory(level="turn_over"),
    )
    bt_choose_obj.adjust(3, 2, 2, 1)
    if need_close_db:
        db.need_close_conn = True
        await db._close()
    return bt_choose_obj.as_markup()


async def creat_bt_choose_author(
    ls_authors: list[str], db: database.Database | None = None
):
    """Функция, которая создает клавиатуру для выбора автора"""

    bt_choose_author = InlineKeyboardBuilder()

    need_close_conn = False
    if db is None:
        db = database.Database()
        db._conn()
        need_close_conn = True

    for author in ls_authors:
        bt_choose_author.button(
            text=author,
            callback_data=choose_author_CallbackFactory(author=author),
        )
    if need_close_conn:
        db.need_close_conn = True
        await db._close()
        db.need_close_conn = False
    bt_choose_author.adjust(2)
    return bt_choose_author.as_markup()


async def creat_bt_choose_book(
    user_id: int, for_sl_book: bool = False, db: database.Database | None = None
):
    """Функция, которая создает клавиатуру для выбора книги и перелистывания"""
    if for_sl_book:
        bt_choose_books = await generate_bt_choose_sl_book(user_id=user_id)
        return bt_choose_books
    bt_choose_obj = InlineKeyboardBuilder()
    bt_choose_obj.button(
        text="<", callback_data=turn_over_CallbackFactory(add_current_page=-1, name="<")
    )
    need_close_conn = False
    if db is None:
        db = database.Database()
        db._conn()
        need_close_conn = True
    user_chapter = await db.get_user_chapter(user_id=user_id)
    c = await db.get_user_auxiliary_variable(user_id=user_id)
    all_page = len(user_chapter)
    del user_chapter
    current_page = c + 1
    # await db.update_user_auxiliary_variable_in_database(user_id=user_id, auxiliary_variable=current_page)
    bt_choose_obj.button(
        text=f"{current_page}/{all_page}",
        callback_data=turn_over_CallbackFactory(add_current_page=-1, name="integer"),
    )
    bt_choose_obj.button(
        text=">", callback_data=turn_over_CallbackFactory(add_current_page=1, name=">")
    )
    bt_choose_obj.button(
        text="выбрать",
        callback_data=choose_book_CallbackFactory(number_book=current_page - 1),
    )
    bt_choose_obj.button(
        text="добавить в избранные",
        callback_data=add_or_del_on_ls_selected_books_CallbackFactory(
            number_book=current_page - 1
        ),
    )
    bt_choose_obj.button(
        text="<  назад",
        callback_data=one_level_back_CallbackFactory(level="turn_over"),
    )
    bt_choose_obj.adjust(3, 1, 1)
    if need_close_conn:
        db.need_close_conn = True
        await db._close()
        db.need_close_conn = False
    return bt_choose_obj.as_markup()


async def get_bt__meny():
    """Функция, которая создает клавиатуру для выбора действий в меню"""
    build_meny = ReplyKeyboardBuilder()
    build_meny.button(
        text="GDZ",
    )
    build_meny.button(text="HELP")
    build_meny.button(
        text="список избранных книг",
    )
    build_meny.adjust(2, 1)
    # a = build_meny.as_markup(resize_keyboard=True)

    return build_meny.as_markup(resize_keyboard=True)
