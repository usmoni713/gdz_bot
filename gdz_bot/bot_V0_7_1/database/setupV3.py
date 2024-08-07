import asyncio
from pprint import pprint
from time import time
from typing import Any, Literal, Self
import asyncpg
import json
import sys
from random import randint
sys.path.append(
    "d:\\gdz_bot\\gdz_bot"
)  # Добавление пути в список путей для поиска модулей
from GdzAPI import gdz_api as gdz_api


class Database:
    """Объект для работы с базой данных PostgreSQL"""

    def __init__(
        self,
        db_name: str = "db_test",
        db_user: str = "postgres",
        db_password: str = "usmoni03",
        db_host: str = "localhost",
        db_port: int = 5432,
    ):
        """Инициализирует подключение к базе данных"""
        self._db_name: str = db_name
        self._db_user: str = db_user
        self._db_password: str = db_password
        self._db_host: str = db_host
        self._db_port: int = db_port
        self._conn: asyncpg.Connection | None = None
        self.have_conn: bool = False
        self.need_close_conn: bool = False
        self.db_id = randint(1000, 999999)

    async def _connect(self) -> None:
        """Соединяет с базой данных"""
        # print(f"подключается к базе данных: {self.have_conn=}")
        if self.have_conn:
            return
        self._conn = await asyncpg.connect(
            database=self._db_name,
            user=self._db_user,
            password=self._db_password,
            host=self._db_host,
            port=self._db_port,
        )
        self.have_conn = True

    async def _close(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.need_close_conn:
            if self.have_conn:
                await self._conn.close()
                print(f"закрывается соединение с базой данных: {self.have_conn=}")
                self.have_conn = False

    async def execute_query(
        self,
        query: str,
    ) -> None:
        """Выполняет SQL-запрос

        :param query: SQL-запрос
        :param args: параметры запроса
        :return: None
        """
        # print(f"выполняется запрос: {query=}")
        if not self.have_conn:
            await self._connect()
            await self._conn.execute(query)
            await self._close()
        else:
            await self._conn.execute(query)

    async def create_tables(
        self,
        table_names_with_fields: list[tuple[str, list[tuple[str, str]]]],
    ) -> None:
        """Создает таблицы в базе данных и их столбцы"""
        # Соединяемся с базой данных
        await self._connect()
        # Если таблицы еще не существуют,
        # то создаем их
        for table_name, fields in table_names_with_fields:
            await self._conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(map(lambda field_with_type: f'{field_with_type[0]} {field_with_type[1]}', fields))});"
            )
        await self._close()

    async def fill_table(
        self,
        table_name: str,  # имя таблицы
        field_names: list[str],  # имена полей таблицы
        values: list[Any],  # значения для вставки
    ) -> None:
        """Заполняет таблицу данными

        :param table_name: имя таблицы
        :param field_names: имена полей таблицы
        :param values: значения для вставки,
               каждое значение должно быть в
               виде кортежа с количеством элементов,
               равным количеству полей в таблице
        """
        # Вставляем данные в таблицу
        query = ""
        for s_values in values:
            query += f"INSERT INTO {table_name} ({', '.join(field_names)}) VALUES {s_values}; \n "
        await self.execute_query(
            query,
        )

    async def get_table_data(
        self,
        table_name: str,  # имя таблицы
        field_names: list[str] | None = None,  # имена полей таблицы
        conditions: str = "",
    ) -> list[asyncpg.Record] | Any:
        """Возвращает значения полей из таблицы
        :param table_name: имя таблицы
        :param field_names: имена полей таблицы
        :return: список кортежей, каждый кортеж - это значения полей
                 из одной строки таблицы
        """
        # Соединяемся с базой данных
        if not self.have_conn:
            await self._connect()
        # Запрашиваем данные из таблицы
        records: list[asyncpg.Record]
        query = ""

        if not field_names is None:
            query += f"SELECT {', '.join(field_names)} FROM {table_name}"
        else:
            query += f"SELECT * FROM {table_name}"
        if conditions != "":
            query += f" WHERE {conditions}"
        records = await self._conn.fetch(f"{query};")

        # Закрываем соединение
        if not self.have_conn:
            await self._close()

        return records

    async def delete_value_from_table(
        self,
        table_name: str,  # имя таблицы
        field_name: str,  # имя поля
        value_to_delete: str,  # значение для удаления
    ):
        """Удаляет значение из поля в таблице"""

        query = f"DELETE FROM {table_name} WHERE {field_name} = {value_to_delete};"
        await self.execute_query(
            query,
        )

    async def chec_user_in_database(
        self,
        user_id: int,
        table_name: str = "users",
        field_name: str = "id_user",
    ) -> bool:
        """Проверяет наличие пользователя в базе данных"""
        records = await self.get_table_data(
            table_name=table_name,
            field_names=(field_name,),
            conditions=f"{field_name} = {user_id}",
        )
        if len(records) == 0:
            return False
        else:
            return True

    async def add_new_user_in_database(
        self,
        user_id: int,
        class_: int,
    ):
        """Добавляет пользователя в базу данных"""
        await self.fill_table(
            table_name="users",
            field_names=("id_user", "class_"),
            values=((user_id, class_),),
        )

    async def add_book_on_user_selected_books_in_database(
        self,
        user_id: int,
        user_book: gdz_api.Book,
    ):
        """Обновляет данные пользователя в базе данных"""
        ls_books = await self.get_user_selected_books(user_id=user_id)
        ls_books.append(user_book)
        list_of_books = [book.__dict__ for book in ls_books]
        json_data = json.dumps(list_of_books)
        qyuery = f"UPDATE users SET user_selected_books = '{json_data}' WHERE id_user = {user_id};"
        await self.execute_query(
            qyuery,
        )

    async def update_user_class_in_database(
        self,
        user_id: int,
        class_: int,
    ):
        """Обновляет данные пользователя в базе данных"""
        qyuery = f"UPDATE users SET class_ = {class_} WHERE id_user = {user_id};"
        await self.execute_query(
            qyuery,
        )

    async def update_user_chapter_in_database(
        self,
        user_id: int,
        user_books: list[gdz_api.Book],
    ):
        """Обновляет данные пользователя в базе данных"""
        list_of_books = [book.__dict__ for book in user_books]
        json_data = json.dumps(list_of_books)
        qyuery = f"UPDATE users SET chapter = '{json_data}' WHERE id_user = {user_id};"
        await self.execute_query(
            qyuery,
        )

    async def update_user_selected_book_in_database(
        self,
        user_id: int,
        user_book: gdz_api.Book | None = None,
    ):
        """Обновляет данные пользователя в базе данных"""
        if user_book is None:
            await self.execute_query(
                f"UPDATE users SET selected_book = NULL WHERE id_user = {user_id};"
            )
            return
        book = user_book.__dict__
        json_data = json.dumps(book)
        qyuery = (
            f"UPDATE users SET selected_book = '{json_data}' WHERE id_user = {user_id};"
        )
        await self.execute_query(
            qyuery,
        )

    async def update_user_selected_books_in_database(
        self,
        user_id: int,
        user_books: list[gdz_api.Book],
    ):
        """Обновляет данные пользователя в базе данных"""
        list_of_books = [book.__dict__ for book in user_books]
        json_data = json.dumps(list_of_books)
        qyuery = f"UPDATE users SET user_selected_books = '{json_data}' WHERE id_user = {user_id};"
        await self.execute_query(
            qyuery,
        )

    async def update_user_section_in_database(
        self,
        user_id: int,
        user_section: str,
    ):
        """Обновляет данные пользователя в базе данных"""
        if user_section is None:
            user_section = "NULL"
        qyuery = f"UPDATE users SET user_section = '{user_section}' WHERE id_user = {user_id};"
        await self.execute_query(
            qyuery,
        )

    async def update_user_num_url_in_database(
        self,
        user_id: int,
        num_url: str,
    ):
        """Обновляет данные пользователя в базе данных"""
        qyuery = (
            f"UPDATE users SET user_num_url = '{num_url}' WHERE id_user = {user_id};"
        )
        await self.execute_query(
            qyuery,
        )

    async def delete_book_from_user_selected_books_in_database(
        self,
        user_id: int,
        index_of_book: int,
    ):
        """Обновляет данные пользователя в базе данных"""
        ls_books = await self.get_user_selected_books(user_id=user_id)
        del ls_books[index_of_book]
        list_of_books = [book.__dict__ for book in ls_books]
        json_data = json.dumps(list_of_books)
        qyuery = f"UPDATE users SET user_selected_books = '{json_data}' WHERE id_user = {user_id};"
        await self.execute_query(
            qyuery,
        )

    async def get_user_num_url(
        self,
        user_id: int,
    ) -> str:
        """Получает данные пользователя из базы данных"""
        user_num_url = await self.get_table_data(
            table_name="users",
            field_names=("user_num_url",),
            conditions=f"id_user = {user_id}",
        )

        user_num_url = user_num_url[0][0].get("user_num_url")
        return user_num_url

    async def get_user_selected_book(
        self,
        user_id: int,
    ) -> gdz_api.Book:
        """Получает данные пользователя из базы данных"""
        user_selected_book = (
            await self.get_table_data(
                table_name="users",
                field_names=("selected_book",),
                conditions=f"id_user = {user_id}",
            ),
        )

        user_selected_book = json.loads(user_selected_book[0][0].get("selected_book"))
        # print(f'user_selected_book: {user_selected_book}')
        user_selected_book = gdz_api.Book(**user_selected_book)

        return user_selected_book

    async def get_user_section(
        self,
        user_id: int,
    ) -> str:
        """Получает данные пользователя из базы данных"""
        user_section = (
            await self.get_table_data(
                table_name="users",
                field_names=("user_section",),
                conditions=f"id_user = {user_id}",
            ),
        )

        user_section = user_section[0][0].get("user_section")
        return user_section

    async def get_user_class(
        self,
        user_id: int,
    ) -> int:
        """Получает данные пользователя из базы данных"""
        record = (
            await self.get_table_data(
                table_name="users",
                field_names=("class_",),
                conditions=f"id_user = {user_id}",
            ),
        )
        user_class = record[0][0].get("class_")
        return user_class

    async def get_user_chapter(
        self,
        user_id: int,
    ) -> list[gdz_api.Book]:
        """Получает данные пользователя из базы данных"""
        user_chapter = (
            await self.get_table_data(
                table_name="users",
                field_names=("chapter",),
                conditions=f"id_user = {user_id}",
            ),
        )

        user_chapter = json.loads(user_chapter[0][0].get("chapter"))
        user_chapter = [gdz_api.Book(**book) for book in user_chapter]

        return user_chapter

    async def get_user_selected_books(
        self,
        user_id: int,
    ) -> list[gdz_api.Book]:
        """Получает данные пользователя из базы данных"""
        user_chapter = (
            await self.get_table_data(
                table_name="users",
                field_names=("user_selected_books",),
                conditions=f"id_user = {user_id}",
            ),
        )

        if user_chapter[0][0].get("user_selected_books") is None:
            return []
        user_chapter1 = json.loads(user_chapter[0][0].get("user_selected_books"))
        user_chapter = [gdz_api.Book(**book) for book in user_chapter1]
        return user_chapter

    async def get_user_auxiliary_variable(
        self,
        user_id: int,
    ) -> int:
        """Получает данные пользователя из базы данных"""
        user_auxiliary_variable = (
            await self.get_table_data(
                table_name="users",
                field_names=("auxiliary_variable",),
                conditions=f"id_user = {user_id}",
            ),
        )

        user_auxiliary_variable = user_auxiliary_variable[0][0].get(
            "auxiliary_variable"
        )
        return user_auxiliary_variable

    async def update_user_auxiliary_variable_in_database(
        self,
        user_id: int,
        auxiliary_variable: int,
    ):
        """Обновляет данные пользователя в базе данных"""
        qyuery = f"UPDATE users SET auxiliary_variable = {auxiliary_variable} WHERE id_user = {user_id};"
        await self.execute_query(
            qyuery,
        )


async def get_json_data_from_ls_books(ls_books: list[gdz_api.Book]) -> str:
    """Get json data from list of books"""
    json_data = json.dumps([book.__dict__ for book in ls_books])
    return json_data


async def get_ls_books_from_json_data(json_data: str) -> list[gdz_api.Book]:
    list_of_obj_s = json.loads(json_data)
    list_of_obj = [gdz_api.Book(**obj) for obj in list_of_obj_s]
    return list_of_obj


table_names_with_fields = [
    (
        "users",
        [
            ("id_user", "BIGINT PRIMARY KEY"),
            ("class_", "SMALLINT"),
            ("chapter", "JSONB"),
            ("user_selected_books", "JSONB"),
            ("selected_book", "JSONB"),
            ("auxiliary_variable", "INTEGER"),
            ("user_section", "TEXT"),
            ("user_num_url", "TEXT"),
        ],
    ),
]

table_name = "users"
field_names = [
    "id_user",
    "class_",
    "chapter",
    "user_selected_books",
    "auxiliary_variable",
    "selected_book",
    # 'user_section',
]
# table1_name = "selected_books"
# field_names1 = ["id_user", "user_selsected_books"]


async def main() -> None:
    """Главная функция"""
    db = Database()

    print("Создаем таблицы")
    await db.create_tables(table_names_with_fields)

    print("Заполняем данные в Таблицу.")
    api = gdz_api.Api()
    list_of_obj_s = await api.get_chapter(9, "русский язык")
    # print(f'{list_of_obj_s=}')
    await list_of_obj_s.get_books()
    list_of_books = list_of_obj_s.books
    # # print(f'{list_of_books=}')
    json_data = await get_json_data_from_ls_books(list_of_books)
    list_of_obj_s = await api.get_chapter(chapter_class=4, chapter_subject="математика")
    await list_of_obj_s.get_books()
    list_of_books = list_of_obj_s.books
    json_data1 = await get_json_data_from_ls_books(list_of_books)
    selected_book = await get_json_data_from_ls_books([list_of_books[0]])
    selected_book1 = await get_json_data_from_ls_books([list_of_books[1]])
    values = (
        (123468978, 11, json_data, json_data1, 0, selected_book),
        (357, 4, json_data1, json_data, 0, selected_book1),
    )

    # values1 = (
    #     (123456789789, json_data1),
    #     (3456789, json_data),
    # )

    # await db.fill_table(table_name, field_names, values)
    # await db.fill_table(table1_name, field_names1, values1)
    # await db.update_user_auxiliary_variable_in_database(
    #     user_id=123456789789, auxiliary_variable=200
    # )

    print("Получаем данные из таблицы и вводим на экран.")
    await db.update_user_num_url_in_database(
        user_id=123456789789, num_url="http://example.com"
    )
    us_n_url = await db.get_user_num_url(user_id=123456789789)
    print(f"{us_n_url=}")
    # await db.update_user_section_in_database(user_id=123456789789, user_section="page_1")
    # rec = await db.get_user_section(user_id=123456789789)
    # print(f"{rec=}")
    # rec = await db.get_table_data(table_name=table_name, field_names=["chapter"], conditions='id_user = 123456789789')
    # t1 = await get_ls_books_from_json_data(rec[0][0].get("chapter", "none"))
    # print(f"{t1==json_data=}")
    # print(f"{sorted(list_of_books1)=}")
    # print((list_of_books == list_of_obj))
    # record_all_users = await db.get_table_data(table_name="users", field_names=("id_user",),conditions=f"id_user = {1999}")
    # print(f'{record_all_users[0][0].get("id_user", 'none')=}')

    # t_data = await db.get_table_data(table_name=table_name)
    # for record in t_data:
    # for field, value in record.items():

    #         print(f"{type(field)=}: {type(value)=}")
    # selected_books
    # Получение Список избранных книг юзера  123456789789.
    # t_data = await db.get_table_data(table_name=table1_name)
    # for record in t_data:
    #     for field, value in record.items():
    #         print(f"{field}: {value}")
    # #
    # Удаление записи из таблицы
    # print("Удаление записи из таблицы")
    # await db.delete_value_from_table(table_name=table1_name, field_name='id_user', value_to_delete="1992")
    # Проверяем наличие пользователя в базе данных
    # print("Проверяем наличие пользователя в базе данных")
    # await db.add_new_user_in_database(user_id=1234567897894321, class_=9)
    # await db.update_user_class_in_database(user_id=1234567897894321, class_=11)
    # res = await db.get_table_data(
    #     table_name="users", field_names=("class_",), conditions=f"id_user = {1234567897894321}"
    # )  # (user_id=1234567897894321)
    # print(f"{res=}")


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    start_time = time()  # измеряем время выполнения функции
    # loop.run_until_complete(main())

    asyncio.run(main())
    print(f"Функция выполнена за {time() - start_time} секунд")
