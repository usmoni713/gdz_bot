import logging
from typing import Any
from utils import function
from database import setupV3 as database
from bot_V0_7_1.keyboards.buttons import get_bt_numbers
from GdzAPI import gdz_api
from filters import ferma_callbacks
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)  # Импорт классов Message и CallbackQuery из aiogram

user_router = Router()
# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.info("started!")
from handlers.user import responder as rs


# Обработчик для команды "/start"
@user_router.message(F.text == "/start")
async def start(message: Message):
    await rs.send_meny(message=message)


# Обработчик для колбеков выбора класса
@user_router.callback_query(ferma_callbacks.choose_class_CallbackFactory.filter())
async def send_obj(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_class_CallbackFactory,
    user_id: int,
    db: database.Database,
):
    # Сохранение выбранного класса в информации о пользователе

    await db.update_user_class_in_database(
        user_id=user_id,
        class_=callback_data.user_class,
    )
    user_class = await db.get_user_class(
        user_id=user_id,
    )

    await rs.send_obj(callback=callback, user_class=user_class)


@user_router.callback_query(ferma_callbacks.choose_obj_CallbackFactory.filter())
async def save_obj_get_author(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_obj_CallbackFactory,  # Параметр, содержащий данные колбека (выбранный автор)
    user_id: int,
    db: database.Database,
):

    # Вызов функции для обработки выбора объекта
    await rs.save_obj_get_author(
        callback=callback,
        callback_data=callback_data,
        user_id=user_id,
        db=db,
    )


# Обработчик колбека для выбора объекта
@user_router.callback_query(ferma_callbacks.choose_author_CallbackFactory.filter())
async def save_author_get_cgapter(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_author_CallbackFactory,  # Параметр, содержащий данные колбека (выбранный объект)
    user_id: int,
    db: database.Database,
):

    # Вызов функции для обработки выбора объекта
    await rs.save_author_get_cgapter(
        callback=callback,
        callback_data=callback_data,
        user_id=user_id,
        db=db,
    )


# Обработчик колбека для перелистывание страницы для выбора учебника
@user_router.callback_query(ferma_callbacks.turn_over_CallbackFactory.filter())
async def turn_over(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.turn_over_CallbackFactory,  # Параметр, содержащий данные колбека (например, информация о том на какой странице находится пользователь)
    user_id: int,
    db: database.Database,
):
    # Вызов функции для обработки перелистывание страницы для выбора учебника
    await rs.turn_over(
        callback=callback,
        user_id=user_id,
        add_current_page=callback_data.add_current_page,
        for_sl_book=callback_data.for_sl_book,
        edit_text=True,
        db=db,
    )


# Обработчик колбека для выбора книги и получения раздела
@user_router.callback_query(ferma_callbacks.choose_book_CallbackFactory.filter())
async def save_book_get_section(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_book_CallbackFactory,  # Параметр, содержащий данные колбека (например, выбранная книга)
    user_id: int,
    db: database.Database,
):
    # Сохранение выбранной книги в информации о пользователе
    user_chapter = (
        await db.get_user_chapter(
            user_id=user_id,
        )
        if not callback_data.for_sl_book
        else await db.get_user_selected_books(
            user_id=user_id,
        )
    )
    await db.update_user_selected_book_in_database(
        user_id=user_id,
        user_book=user_chapter[callback_data.number_book],
    )

    # Удаление сообщения с колбеком
    await callback.message.delete()

    # Вызов функции для обработки выбора книги и получения раздела
    await rs.save_book_get_section(callback=callback, user_id=user_id, db=db)


@user_router.callback_query(
    ferma_callbacks.add_or_del_on_ls_selected_books_CallbackFactory.filter()
)
async def save_book_in_ls_selected_books(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_book_CallbackFactory,  # Параметр, содержащий данные колбека (например, выбранная книга)
    user_id: int,
    db: database.Database,
):

    # Сохранение выбранной книги в информации о пользователе
    if not callback_data.del_book:
        user_chapter = await db.get_user_chapter(
            user_id=user_id,
        )
        user_book = user_chapter[callback_data.number_book]
        await db.add_book_on_user_selected_books_in_database(
            user_id=user_id,
            user_book=user_book,
        )
        await callback.answer(
            "книга добавлена в список избранных книг", show_alert=True
        )
    else:
        await db.delete_book_from_user_selected_books_in_database(
            user_id=user_id,
            index_of_book=callback_data.number_book,
        )
        user_selected_books = await db.get_user_selected_books(
            user_id=user_id,
        )
        await callback.answer("книга удалена из списка избранных книг", show_alert=True)
        await db.update_user_auxiliary_variable_in_database(
            user_id=user_id,
            auxiliary_variable=0,
        )

        if len(user_selected_books) <= 0:
            await callback.message.delete()
            await rs.send_meny(message=callback.message)
        else:
            await rs.turn_over(
                user_id=user_id,
                callback=callback,
                add_current_page=0,
                for_sl_book=True,
                edit_text=True,
                db=db,
            )


@user_router.callback_query(
    ferma_callbacks.increase_or_lower_priority_sl_book_CallbackFactory.filter()
)
async def increase_or_lower_priority_sl_book(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.increase_or_lower_priority_sl_book_CallbackFactory,  # Параметр, содержащий данные колбека (например, увеличивать или уменьшать приоритет избранного учебника)
    user_id: int,
    db: database.Database,
):
    # coeficiant - значение, на которое меняется индекс выбранного учебника в списке избранных
    coeficiant = callback_data.coeficiant
    # number_book - индекс выбранного учебника в списке избранных
    number_book = callback_data.number_book

    # если мы пытаемся увеличить приоритет первого или уменьшить приоритет последнего учебника в списке,
    # то отвечаем пользователю без изменений
    ls_selected_books = await db.get_user_selected_books(
        user_id=user_id,
    )

    if (number_book == 0 and coeficiant == -1) or (
        number_book == len(ls_selected_books) - 1 and coeficiant == 1
    ):
        await callback.answer()
        return

    # меняем местами два элемента списка выбранных учебников
    # меняем элементы на coeficiant позиций вперед
    (
        ls_selected_books[number_book],
        ls_selected_books[number_book + coeficiant],
    ) = (
        ls_selected_books[number_book + coeficiant],
        ls_selected_books[number_book],
    )
    await db.update_user_selected_books_in_database(
        user_id=user_id,
        user_books=ls_selected_books,
    )
    # обновляем индекс выбранного учебника в списке избранных
    await db.update_user_auxiliary_variable_in_database(
        user_id=user_id,
        auxiliary_variable=number_book + coeficiant,
    )

    # переходим к выбранному учебнику в списке избранных
    await rs.turn_over(
        user_id=user_id,
        callback=callback,
        add_current_page=0,
        for_sl_book=True,
        edit_text=True,
        db=db,
    )


# Обработчик колбека для выбора раздела и получения номеров
@user_router.callback_query(ferma_callbacks.choose_section_CallbackFactory.filter())
async def save_section__get_numbers(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_book_CallbackFactory,  # Параметр, содержащий данные колбека (например, выбранный раздел)
    user_id: int,
    db: database.Database,
):
    user_book = await db.get_user_selected_book(
        user_id=user_id,
    )
    section_structure = await user_book.get_num_structure()
    del user_book
    user_section: str
    for key in section_structure.keys():
        if callback_data.name_section == key[0 : len(callback_data.name_section) :]:
            user_section = key
            break
    await db.update_user_section_in_database(
        user_id=user_id,
        user_section=f"{user_section}",
    )

    # Вызов функции для обработки выбора раздела и получения номеров
    await rs.save_section__get_numbers(
        callback=callback, user_section=user_section, user_id=user_id, db=db
    )


# Обработчик колбека для перелистывания страниц
@user_router.callback_query(ferma_callbacks.flipping_number_CallbackFactory.filter())
async def flipping_number(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.flipping_number_CallbackFactory,  # Параметр, содержащий данные колбека (например, выбранный номер)
    user_id: int,
    db: database.Database,
):
    structure_of_buttons = await db.get_user_structure_of_numbers(user_id=user_id)
    current_position = (
        callback_data.current_position
        if callback_data.current_position < callback_data.max_position
        else 0
    )
    ls_numbers = structure_of_buttons[current_position]
    await callback.message.edit_text(
        text=f"Номер: ",
        reply_markup=await get_bt_numbers(
            ls_numbers=ls_numbers,
            current_position=current_position,
            max_position=callback_data.max_position,
        ),
    )


# Обработчик колбека для выбора номера и отправки ответа
@user_router.callback_query(ferma_callbacks.choose_number_CallbackFactory.filter())
async def save_number_send_answer(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.choose_number_CallbackFactory,  # Параметр, содержащий данные колбека (например, выбранный номер)
    user_id: int,
    db: database.Database,
):

    # Получение URL вопроса по номеру
    user_book = await db.get_user_selected_book(
        user_id=user_id,
    )
    section = await db.get_user_section(
        user_id=user_id,
    )
    section_structure = await user_book.get_num_structure()
    numbers = section_structure[section]
    if type(numbers) == dict:
        for i in numbers.values():
            for j in i:
                if j.num == callback_data.number:
                    url_num = j.url
                    break
    elif type(numbers) == list:
        for i in numbers:
            if i.num == callback_data.number:
                url_num = i.url
                break
    else:
        await function.inform(
            f"[error]in user_handlers.save_number_send_answer: {numbers=}"
        )
    # url_num = section_structure[section]
    user_number: gdz_api.Number = gdz_api.Number(url=url_num, num="")
    # Получение ответов на вопросы по URL
    answers = await user_number.get_answers()

    # Удаление сообщения с колбеком
    await callback.message.delete()

    # Отправка фотографий с ответами
    for name, url in answers.items():
        await callback.message.answer_photo(photo=url, caption=name)

    # Удаление ненужных данных о пользователе
    await function.delete_unnecessary_data(user_id=user_id, db=db)

    # Отправка сообщения с главным меню
    await rs.send_meny(message=callback.message)

    await callback.answer()


# Обработчик колбека для проверки подписки
@user_router.callback_query(F.data == "проверить подписку")
async def chec_sub_reply_thanks(callback: CallbackQuery):

    await callback.message.edit_text(
        text="спасибо!\n теперь у вас есть доступ к функциям бота"
    )
    await rs.send_meny(message=callback.message)
    await callback.answer()


# Обработчик колбека для показа предупреждения "will_be_soon"
@user_router.callback_query(
    ferma_callbacks.show_alert__will_be_soon_CallbackFactory.filter()
)
async def answer__will_be_soon(
    callback: CallbackQuery,
):

    await callback.answer("will_be_soon!!", show_alert=True)


# Обработчик колбека для показа кнопки для выбора класса
@user_router.message(F.text == "GDZ")
async def send_class(message: Message):
    await rs.start(message=message, edit_text=False)


@user_router.message(F.text == "HELP")
async def send_help(message: Message):
    await message.answer(
        """Бот был создан для помощи пользователям в решении различных задач и вопросов. 
        Он использует ресурсы из интернета для анализа запросов и предоставления ответов. Бот может помочь с выполнением различных задач, связанных с школьной программой. Бот постоянно обновляется и улучшается, чтобы быть более эффективным и полезным для пользователей.\n
        По возникновеному вопросам или желанию сотрудничества можно писать в телеграм @usmoni03"""
    )


@user_router.message(F.text == "список избранных книг")
async def send_ls_selected_books(
    message: Message,
    user_id: int,
    db: database.Database,
):
    await db.update_user_auxiliary_variable_in_database(
        user_id=user_id,
        auxiliary_variable=0,
    )
    await rs.turn_over(
        message=message,
        user_id=user_id,
        add_current_page=0,
        for_sl_book=True,
        db=db,
    )


# Обработчик колбека для возвращения на один уровень назад
@user_router.callback_query(ferma_callbacks.one_level_back_CallbackFactory.filter())
async def one_level_back(
    callback: CallbackQuery,
    callback_data: ferma_callbacks.one_level_back_CallbackFactory,  # Параметр, содержащий данные колбека (например, уровень возврата)
    user_id: int,
    db: database.Database,
):
    # Вызов функции для возврата на один уровень назад
    await function.one_level_back(
        level=callback_data.level,  # Передача уровня возврата в функцию
        callback=callback,
        user_id=user_id,
        db=db,
    )

    await callback.answer()
