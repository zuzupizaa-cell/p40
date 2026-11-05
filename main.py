import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
from aiogram.utils.i18n import gettext as _, lazy_gettext as __, I18n, FSMI18nMiddleware

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from models import Base, engine, User, Word

load_dotenv()


TOKEN = getenv("BOT_TOKEN")


dp = Dispatcher()
session = Session(bind=engine)

class WordForm(StatesGroup):
    word = State()


async def command_start_handler(message: Message) -> None:
    query = select(User).where(User.id == message.from_user.id)
    data = list(session.execute(query).scalars())
    if not data:
        query = insert(User).values(id=message.from_user.id , first_name=message.from_user.first_name)
        session.execute(query)
        session.commit()
    btn = button_menu()
    await message.answer(_("Hello!"), reply_markup=btn)


def button_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text=_("Add Word")),
        KeyboardButton(text=_("My Words")),
        KeyboardButton(text=_("Language")),
    ])
    rkb.adjust(2,1)
    return rkb.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    query = select(User).where(User.id == message.from_user.id)
    data = list(session.execute(query).scalars())
    if not data:
        query = insert(User).values(id=message.from_user.id , first_name=message.from_user.first_name)
        session.execute(query)
        session.commit()
    btn = button_menu()
    await message.answer(_("Hello!"), reply_markup=btn)

@dp.message(F.text == __("Add Word"))
async def add_word_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(WordForm.word)
    await message.answer(_("Enter your word"))

@dp.message(F.text, WordForm.word)
async def new_word_handler(message: Message, state: FSMContext) -> None:
    word = message.text
    query = insert(Word).values(word=word, user_id=message.from_user.id)
    session.execute(query)
    session.commit()
    await state.clear()
    btn = button_menu()
    await message.answer(_("Successfully added!"), reply_markup=btn)

@dp.message(F.text == __("My Words"))
async def show_words_handler(message: Message, state: FSMContext) -> None:
    query = select(Word).where(Word.user_id == message.from_user.id)
    words = list(session.execute(query).scalars())
    for word in words:
        await message.answer(text=word.word)

@dp.message(F.text == __("Language"))
async def language_handler(message: Message):
    btns = [KeyboardButton(text="English"), KeyboardButton(text="Uzbek")]
    rkb = ReplyKeyboardBuilder()
    rkb.add(*btns)
    rkb.adjust(2)
    btn = rkb.as_markup(resize_keyboard=True)
    await message.answer(_("Choice language"), reply_markup=btn)


@dp.message(F.text.in_(["English", "Uzbek"]))
async def choice_lang_handler(message: Message, state: FSMContext, i18n:I18n) -> None:
    map = {
        "English": "en",
        "Uzbek": "uz",
    }
    lang = map.get(message.text)
    await state.update_data(locale=lang)
    i18n.current_locale = lang
    btns = button_menu()
    await message.answer(_("Change language"), reply_markup=btns)


async def main() -> None:
    Base.metadata.create_all(engine)
    i18n = I18n(path="locales", default_locale="en")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.update.middleware(FSMI18nMiddleware(i18n=i18n))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
