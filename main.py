import sqlite3
import asyncio
import logging
import sys
import aiohttp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import db_language

from credentials import BOT_TOKEN
from request_utils import fetch_place_to_watch_movie
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from request_utils import fetch_movie_info


DATABASE = 'bot_database.db'
dp = Dispatcher()

# Database initialization
conn = sqlite3.connect(DATABASE, check_same_thread=False)
cursor = conn.cursor()
cursor.execute(db_language.CREATE_SEARCHES)
cursor.execute(db_language.CREATE_STATS)
conn.commit()


# Helper function to execute SQL queries
def execute_query(query, params=None):
    cursor.execute(query, params)
    conn.commit()


# Command handlers
@dp.message(Command('start', 'help'))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для поиска фильмов и сериалов. Просто напиши название, и я постараюсь помочь.\n"
                         "Доступные команды:\n"
                         "\n"
                         "/help  ->  памятка по работе с ботом\n"
                         "/stats  ->  статистика по просмотренным фильмам(с указанием того,"
                         " сколько раз ты смотрел фильм)\n"
                         "/history  ->  фильмы, которые ты когда-либо искал\n"
                         "\n"
                         "Хорошего вечера!\n")


@dp.message(Command('history'))
async def show_history(message: types.Message):
    user_id = message.from_user.id
    execute_query(db_language.SHOW_HISTORY, (user_id,))
    rows = cursor.fetchall()

    if rows:
        history_text = "История просмотров:\n"
        for row in rows:
            history_text += f"- {row[0]}\n"
        await message.answer(history_text)
    else:
        await message.answer("У вас пока нет истории поисковых запросов.")


@dp.message(Command('stats'))
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    execute_query(db_language.SHOW_STATS, (user_id,))
    rows = cursor.fetchall()

    if rows:
        stats_text = "Статистика просмотренных фильмов:\n"
        for row in rows:
            stats_text += f"- {row[0]}: {row[1]} раз(а)\n"
        await message.answer(stats_text)
    else:
        await message.answer("У вас пока нет статистики просмотренных фильмов.")


# Movie search handler
@dp.message()
async def search_movie(message: types.Message):
    async with aiohttp.ClientSession() as session:
        query = message.text
        user_id = message.from_user.id

        # fetching movie information from some API
        movie_info = await fetch_movie_info(session, query)

        if movie_info:
            # Save the search query and movie title to the database
            execute_query(db_language.ADD_TO_SEARCHERS, (user_id, movie_info['title'], movie_info['title']))

            # Update movie stats
            # Выполнение запроса для поиска существующей строки
            execute_query(db_language.select_query, (user_id, movie_info['title']))
            existing_row = cursor.fetchone()

            if existing_row:
                # Если строка существует, удалить ее и получить значение count
                count_value = existing_row[0]
                execute_query(db_language.delete_query, (user_id, movie_info['title']))
            else:
                # Если строки не существует, установить значение count в 0
                count_value = 0

            # Увеличить значение count на 1
            count_value += 1

            # Вставить новую строку с обновленным значением count
            execute_query(db_language.insert_query, (user_id, movie_info['title'], count_value))
            # Send movie information to the user
            movie_text = f"{movie_info['title']}, {movie_info['release_year']}\n\n{movie_info['description']}"

            hide_buttons_button = InlineKeyboardButton(text="Смотреть",
                                    url=await fetch_place_to_watch_movie(session, movie_info['title'], movie_info['release_year']))
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[hide_buttons_button]])

            await message.answer_photo(movie_info['poster_url'], caption=movie_text, reply_markup=inline_keyboard)
        else:
            await message.answer("Фильм не найден. Попробуйте другой запрос.")


# Command to start a new search
@dp.message(Command('search'))
async def start_search(message: types.Message):
    await message.answer("Введите название фильма или сериала для поиска.")


async def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
