from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from database.engine import session_maker
from database.models import Data
from database.orm_query import orm_add_topic
from kbds import reply
from kbds.reply import more_keyboard, remove_kbd

user_private_router = Router()


class AddDataState(StatesGroup):
    URL = State()
    keywords = State()


class SearchDataState(StatesGroup):
    waiting_for_keywords = State()
    waiting_for_more = State()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет! Данный бот предназначен для хранения и поиска интересных статей.",
                         reply_markup=reply.start_keyboard)


@user_private_router.message(StateFilter(None), F.text.lower() == 'добавить')
async def add_URL(message: types.Message, state: FSMContext):
    await message.answer("Введите URL статьи:", reply_markup=reply.remove_kbd)
    await state.set_state(AddDataState.URL)


@user_private_router.message(AddDataState.URL, F.text)
async def add_keyword(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(URL=text)
    await message.answer("Введите ключевые слова статьи: ")
    await state.set_state(AddDataState.keywords)


@user_private_router.message(AddDataState.keywords, F.text)
async def add_db(message: types.Message, state: FSMContext, session: AsyncSession):
    chat_id = message.chat.id
    text = message.text
    await state.update_data(keywords=text)
    data = await state.get_data()
    try:
        await orm_add_topic(session, data, chat_id)
        await message.answer("Спасибо! Ваша информация сохранена.")
        await state.clear()
        await message.answer("Хотите добавить ещё статью?", reply_markup=reply.close_keyboard)
    except Exception as e:
        await message.answer("Ошибка, не получилось добавить тему!")
        await state.clear()


@user_private_router.message(F.text.lower().contains('да'))
async def text_yes(message: types.Message, state: FSMContext):
    await add_URL(message, state)


@user_private_router.message(F.text.lower().contains('нет'))
async def text_no(message: types.Message):
    await message.answer("Пока!", reply_markup=reply.remove_kbd)
    await message.leave_chat(message.chat.id)


@user_private_router.message(StateFilter(None), F.text.lower() == 'поиск')
async def search_article(message: types.Message, state: FSMContext):
    await message.answer("Введите ключевые слова статьи:", reply_markup=reply.remove_kbd)
    await state.set_state(SearchDataState.waiting_for_keywords)


@user_private_router.message(SearchDataState.waiting_for_keywords, F.text)
async def input_keyword_for_search(message: types.Message, state: FSMContext):
    keywords = [word.lower() for word in message.text.split()]
    await state.update_data(keywords=keywords)
    async with session_maker() as session:
        stmt = select(Data).filter(or_(func.lower(Data.keyword).like(f"%{keyword}%") for keyword in keywords))
        result = await session.execute(stmt)
        urls = [row.URL for row in result.scalars().all()]
    if not urls:
        await message.reply("Совпадений нет!")
        await state.clear()
    else:
        await state.update_data(urls=urls)
        await message.reply(urls.pop(0), reply_markup=more_keyboard)
        await state.update_data(urls=urls)
        await state.set_state(SearchDataState.waiting_for_more)


@user_private_router.message(SearchDataState.waiting_for_more, F.text.lower() == 'продолжить поиск')
async def handle_more(message: types.Message, state: FSMContext):
    data = await state.get_data()
    urls = data.get('urls')
    if urls:
        await message.reply(urls.pop(0), reply_markup=more_keyboard)  # And here
        await state.update_data(urls=urls)
    else:
        await message.reply('Больше нет совпадений.',
                            reply_markup=remove_kbd)
        await message.leave_chat(message.chat.id)

