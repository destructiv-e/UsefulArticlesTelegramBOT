import asyncio
import os

from aiogram import Bot, Dispatcher, types

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from general_menu_comand.user_private_cmd import private_chat
from handlers.user_private_handlers import user_private_router
from middlewares.db import DataBaseSession

from database.engine import create_db, drop_db, session_maker

ALLOW_UPDATES = ["message"]

bot = Bot(token=os.getenv("TOKEN"))

dp = Dispatcher()

dp.include_router(user_private_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print("бот выключен")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private_chat, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOW_UPDATES)


asyncio.run(main())
