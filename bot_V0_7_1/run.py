import asyncio, logging
import sys

from config import path_to_bot, TOKEN_BOT

sys.path.append(path_to_bot)

from handlers.user import user_handlers

from aiogram import Bot, Dispatcher

from middlewares import middlewares

bot = Bot(token=TOKEN_BOT)
dp = Dispatcher()

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(
    level=logging.ERROR,
    format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
    "%(lineno)d - %(name)s - %(message)s",
)

# Инициализируем логгер модуля

logger = logging.getLogger(__name__)
logger.error("started!")


async def main_():
    """
    Регистрирует роутеры в диспетчере и запускает LongPoll.
    """
    dp.update.middleware(
        middleware=middlewares.CheckNewUser()
    )  # Добавление middleware для проверки на новых пользователей
    # Проверка на подписку
  
    # Регистрируем роутеры в диспетчере
    dp.include_router(user_handlers.user_router)

    # Запуск LongPoll
    await dp.start_polling(bot)


asyncio.run(main_())
