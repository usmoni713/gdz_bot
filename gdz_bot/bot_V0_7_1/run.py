import asyncio, logging
import sys

#
sys.path.append("d:\\fast-gdz\\gdz_bot")

from handlers.user import user_handlers

from aiogram import Bot, Dispatcher

from middlewares import middlewares

token = "6922595534:AAFK_4t-j_an2JhWXCsbk3_vKWY998MjwKg"
bot = Bot(token=token)
dp = Dispatcher()

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(
    level=logging.ERROR,
    format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
    "%(lineno)d - %(name)s - %(message)s",
)

# Инициализируем логгер модуля

logger = logging.getLogger(__name__)
logger.info("started!")


async def main_():
    """
    Регистрирует роутеры в диспетчере и запускает LongPoll.
    """
    dp.update.middleware(
        middleware=middlewares.check_new_user()
    )  # Добавление middleware для проверки на новых пользователей
    dp.update.middleware(middleware=middlewares.creat_connection_database())
    # Проверка на подписку
    dp.update.middleware(
        middleware=middlewares.chec_sub()
    )  # Добавление middleware для проверки на подписку

    dp.update.middleware(
        middlewares.get_user_id_database()
    )  # Добавление middleware для получения ID пользователя из базы данных

    # Регистрируем роутеры в диспетчере
    dp.include_router(user_handlers.user_router)

    # Запуск LongPoll
    await dp.start_polling(bot)


asyncio.run(main_())
