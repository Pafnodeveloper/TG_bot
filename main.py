from config import TOKEN, my_telegram_id
from youtube import get_audio
from inline_buttons import layout
from aiohttp_test import get_song_name

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageToDeleteNotFound
from datetime import datetime as dt
from inspect import getgeneratorstate
from pathlib import Path

from logging.handlers import TimedRotatingFileHandler
import logging
import glob
import os
import asyncio


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, loop=asyncio.get_event_loop())
gen = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")

file_handler = TimedRotatingFileHandler("sheduler_log", when="midnight", interval=1)
file_handler.setFormatter(formatter)
file_handler.suffix = "%Y%m%d"

logger.addHandler(file_handler)


@dp.message_handler(commands="gimme")
async def send_song(message: types.Message):
    global gen
    needed_song = message.text.split("gimme")
    if needed_song[1] == "":
        await bot.send_message(my_telegram_id, "Необходимо указать исполнителя или название песни")
        logger.debug("Не было указано ни имя артиста ни название песни")
    else:
        search = get_audio()
        gen = search
        song = search.send(needed_song[1])
        await bot.send_audio(my_telegram_id, open(song, "rb"))
        await bot.send_message(my_telegram_id, "Это то, что вы хотели?", reply_markup=layout)
        loop = asyncio.get_event_loop()
        loop.create_task(del_markup(message.message_id, 60), name="del_markup")
        # task = loop.call_later(0, asyncio.create_task, del_markup(message.message_id, 10))
        logger.debug("The song has benn sent")


@dp.message_handler(content_types=types.ContentType.TEXT)
async def check_user_id(message: types.Message):
    await bot.send_message(my_telegram_id, text="Hi " + '🙋')
    logger.debug(f"{message.from_user.id} were answered")


@dp.callback_query_handler(text="yes")
async def answer_yes(callback: types.CallbackQuery):
    task = list(filter(lambda x: x.get_name() == 'del_markup', asyncio.all_tasks()))
    task[0].cancel()
    logger.debug(f"Task {task[0].get_name()} отменена")
    await bot.send_message(my_telegram_id, "Я рад, что вам понравилось")
    await callback.answer()
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    gen.close()
    logger.debug("То что надо")
    logging.debug(getgeneratorstate(gen))


@dp.callback_query_handler(text="no")
async def answer_no(callback: types.CallbackQuery):
    task = list(filter(lambda x: x.get_name() == 'del_markup', asyncio.all_tasks()))
    task[0].cancel()
    logger.debug(f"Task {task[0].get_name()} отменена")
    msg = await bot.send_message(my_telegram_id, "Продолжаю поиск")
    await callback.answer()
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    song = next(gen)
    await bot.send_audio(my_telegram_id, open(song, "rb"))
    await bot.send_message(my_telegram_id, "Это то, что вы хотели?", reply_markup=layout)
    logger.debug("Найденный вариант не понравился. Продолжаем поиск")
    loop = asyncio.get_event_loop()
    loop.create_task(del_markup(callback.message.message_id, 60), name="del_markup")


async def reminder():
    if dt.now().hour == 22:
        await bot.send_message(my_telegram_id, text="Пора учить SQL!!!" + " 📖")
        logger.debug("SQL reminder has been sent")
        loop = asyncio.get_event_loop()
        loop.call_later(3600, asyncio.create_task, reminder())
    else:
        asyncio.create_task(reminder())


async def payday():
    if dt.now().day == 21 and dt.now().hour == 10:
        await bot.send_message(my_telegram_id, text="‼Время проверить счетчики‼")
        logger.debug("Utility meter reminder has been sent")
        loop = asyncio.get_event_loop()
        loop.call_later(86400, asyncio.create_task, payday())
    else:
        asyncio.create_task(payday())


async def greeting2():
    if dt.now().hour == 7 and dt.now().minute == 45:
        await bot.send_message(my_telegram_id, text="Good morning" + ' ☀')
        logger.debug("Greetings has been sent")
        loop = asyncio.get_event_loop()
        loop.call_later(900, asyncio.create_task, greeting2())
    else:
        asyncio.create_task(greeting2())


async def purge_song_dir():
    path = Path(__file__).parent.absolute()
    files = glob.glob(f"{path}/songs/*")
    for f in files:
        os.remove(f)
    logger.debug("Песни удалены из папки")
    loop = asyncio.get_event_loop()
    loop.call_later(3600, asyncio.create_task, purge_song_dir())


async def del_markup(msg_id: int, sleep_time: int):
    await asyncio.sleep(sleep_time)
    global gen
    try:
        await bot.delete_message(chat_id=my_telegram_id, message_id=(msg_id + 3))
        gen.close()
        logger.debug("Пользователь не нажал выбор, удаляю markup")
        logging.debug(getgeneratorstate(gen))
    except MessageToDeleteNotFound:
        await bot.delete_message(chat_id=my_telegram_id, message_id=(msg_id + 2))
        gen.close()
        logger.debug("Пользователь не нажал выбор, удаляю markup")
        logging.debug(getgeneratorstate(gen))


async def true_del_markup(msg_id: int, sleep_time: int):
    await asyncio.sleep(sleep_time)
    global gen
    try:
        await bot.delete_message(chat_id=my_telegram_id, message_id=msg_id)
        gen.close()
        logger.debug("Пользователь не нажал выбор, удаляю markup")
        logging.debug(getgeneratorstate(gen))
    except MessageToDeleteNotFound:
        gen.close()
        logger.debug("Пользователь не нажал выбор, удаляю markup")
        logging.debug(getgeneratorstate(gen))


async def get_new_from_spotify():
    global gen
    song = get_song_name()
    if song:
        search = get_audio()
        gen = search
        song = search.send(song)
        await bot.send_audio(my_telegram_id, open(song, "rb"))
        msg = await bot.send_message(my_telegram_id, "Это то, что вы хотели?", reply_markup=layout)
        loop = asyncio.get_event_loop()
        loop.create_task(true_del_markup(msg["message_id"], 60), name="del_markup")
        logger.debug("The song has been sent")

        loop = asyncio.get_event_loop()
        loop.call_later(90, asyncio.create_task, get_new_from_spotify())
    else:
        loop = asyncio.get_event_loop()
        loop.call_later(90, asyncio.create_task, get_new_from_spotify())


async def main():
    task1 = asyncio.create_task(reminder())
    task2 = asyncio.create_task(greeting2())
    task3 = asyncio.create_task(payday())
    task4 = asyncio.create_task(purge_song_dir())
    task5 = asyncio.create_task(get_new_from_spotify())
    await asyncio.gather(task1, task2, task3, task4, task5)

if __name__ == "__main__":
    dp.loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)
