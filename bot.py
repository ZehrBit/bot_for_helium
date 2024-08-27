import asyncio
import datetime as dt
from loguru import logger

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated

import config
from get_info import *
from database.DB import *

dp = Dispatcher()
bot = Bot(config.TELEGRAM_TOKEN)

logger.add("logs/bot.log", level="DEBUG", rotation="10 MB")


@logger.catch(level="ERROR")
async def send_messages():
    """Отправляет сообщения по чатам, которые есть в БД"""
    session = SessionLocal()
    chats = session.query(Chat).all()
    session.close()
    logger.info("Запрос к базе выполнен успешно")
    message = await create_message()
    for chat in chats:
        try:
            await bot.send_message(chat.chat_id, message)
            logger.info(f"Сообщение отправлено в чат: {chat.chat_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения в чат: {chat.chat_id}: {e}")


@logger.catch(level="ERROR")
async def create_message():
    try:
        date, price = await get_info()
        logger.info("Данные с сайта Газпрома получены")
        return (f'Дата последних торгов: {date}\n'
                f'Цена за 1м³: {price}₽\n'
                f'Цена за 40л(5,7м³) баллон: {int(int(price) * 5.7)}₽\n'
                f'Цена за 10л(1.425м³) баллон: {int(int(price) * 1.425)}₽')
    except:
        logger.error("Данные с сайта Газпрома не получены")

@logger.catch(level="ERROR")
async def timer():
    logger.info('Таймер запущен')
    """Запускает раз в сутки рассылку сообщений"""
    while True:
        if dt.datetime.now().strftime("%H:%M") == config.TIME_FOR_SENDING and dt.datetime.now().weekday() in config.WEEKDAY_FOR_SENDING:
            await send_messages()
            logger.info("Рассылка сообщений прошла")
        await asyncio.sleep(57)


@logger.catch(level="ERROR")
async def main() -> None:
    asyncio.create_task(timer())
    await dp.start_polling(bot)


@logger.catch(level="ERROR")
@dp.my_chat_member()
async def user_add_or_kick_bot(event: ChatMemberUpdated):
    """Обработчик событий:
    Event_1: Юзер добавил бота в чат
    Event_2: Юзер исключил бота из чата"""
    new_chat_member = event.new_chat_member
    chat = event.chat
    user = event.from_user
    if new_chat_member.status == 'member':
        logger.info(f'Пользователь: id - {user.id}, Имя - {user.first_name}, Никнейм - {user.username} ДОБАВИЛ бота в чат: id - {chat.id}, Имя чата - "{chat.title}"')
        add_chat_to_db(chat.id, chat.title, chat.type)
        logger.info('Данные сохранены в базе')
    elif new_chat_member.status in ['left', 'kicked']:
        logger.info(f'Пользователь: id - {user.id}, Имя - {user.first_name}, Никнейм - {user.username} ИСКЛЮЧИЛ бота из чат: id - {chat.id}, Имя чата - "{chat.title}"')
        remove_chat_from_db(chat.id)
        logger.info('Данные удалены из БД')


@logger.catch(level="ERROR")
@dp.message(Command("get_price"))
async def get_price(message: types.Message) -> None:
    logger.info(f'Получен запрос "/get_price" от пользователя: id - {message.chat.id}, Имя - {message.chat.first_name}, Никнейм - {message.chat.username}')
    temp_message = await message.answer('⏳ Получение данных...', parse_mode='HTML')
    await message.answer(await create_message(), parse_mode='HTML')
    await temp_message.delete()
    logger.info(f'Сообщение отправлено пользователю: id - {message.chat.id}, Имя - {message.chat.first_name}, Никнейм - {message.chat.username}')

if __name__ == "__main__":
    asyncio.run(main())
