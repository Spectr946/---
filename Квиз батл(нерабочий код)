# -*- coding: utf-8 -*-
"""
Чат-бот 'Сферум Квиз-Батл' для хакатона Идея фикс
Установка зависимостей:
pip install vkbottle
"""

from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
import random

# Вставьте ваш ключ сообщества из настроек группы/Сферума
TOKEN = "vk1.a.Xrp8jBSN8TOy2oiIeVsPC4C2iIZ1MwZw2V0GrV4Irzuld975pXR0_wa09LM8vFP9GnUf59EBGzPEj5-J2HsHEBx8iyUgrenY9nEXzVov-5UBQHuLZ45OFSXDu2esXtbN7jUocSSZZQEc3AT6VboarA9Sbn6T7NUFe9_pvBGFeXowJ9oKoCJV3_ha5QYbfj8G23tirdwuiVEYdmBxLIKd0w"
bot = Bot(token="vk1.a.Xrp8jBSN8TOy2oiIeVsPC4C2iIZ1MwZw2V0GrV4Irzuld975pXR0_wa09LM8vFP9GnUf59EBGzPEj5-J2HsHEBx8iyUgrenY9nEXzVov-5UBQHuLZ45OFSXDu2esXtbN7jUocSSZZQEc3AT6VboarA9Sbn6T7NUFe9_pvBGFeXowJ9oKoCJV3_ha5QYbfj8G23tirdwuiVEYdmBxLIKd0w")

# Хранилище очков в памяти (для прототипа)
user_scores = {}
user_state = {}

# База вопросов по предметам
QUIZ_DATA = {
    "История": [
        {
            "q": "В каком году произошло Ледовое побоище?",
            "options": ["1242", "1380", "1480", "1812"],
            "correct": "1242"
        },
        {
            "q": "Кто был первым царём из династии Романовых?",
            "options": ["Михаил", "Пётр I", "Иван Грозный", "Алексей"],
            "correct": "Михаил"
        }
    ],
    "Биология": [
        {
            "q": "Какая органелла клетки отвечает за синтез энергии (АТФ)?",
            "options": ["Митохондрия", "Рибосома", "Лизосома", "Ядро"],
            "correct": "Митохондрия"
        }
    ],
    "Русский язык": [
        {
            "q": "В каком слове ударение падает на второй слог?",
            "options": ["звонИт", "тОрты", "бАнты", "шАрфы"],
            "correct": "звонИт"
        }
    ]
}

def get_main_menu():
    return (
        Keyboard(one_time=False)
        .add(Text("⚡ Быстрый Квиз", payload={"cmd": "quiz"}), color=KeyboardButtonColor.POSITIVE)
        .add(Text("🏆 Мой рейтинг", payload={"cmd": "rating"}), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("📚 Выбрать предмет", payload={"cmd": "subject"}), color=KeyboardButtonColor.SECONDARY)
    ).get_json()

def get_subject_menu():
    kb = Keyboard(one_time=False)
    for subj in QUIZ_DATA.keys():
        kb.add(Text(subj, payload={"subj": subj}), color=KeyboardButtonColor.PRIMARY)
    kb.row().add(Text("🔙 Главное меню"), color=KeyboardButtonColor.NEGATIVE)
    return kb.get_json()

@bot.on.message(text=["Начать", "Привет", "Старт", "меню", "🔙 Главное меню"])
async def start_handler(message: Message):
    uid = message.from_id
    if uid not in user_scores:
        user_scores[uid] = 0
    await message.answer(
        "👋 Привет! Добро пожаловать в «Сферум Квиз-Батл»!\n\n"
        "Сражайся в интеллектуальных дуэлях на переменах, зарабатывай очки "
        "и помоги своему классу подняться в топ школы! 🚀",
        keyboard=get_main_menu()
    )

@bot.on.message(text=["🏆 Мой рейтинг", "рейтинг"])
async def rating_handler(message: Message):
    score = user_scores.get(message.from_id, 0)
    await message.answer(
        f"📊 Твоя статистика:\n"
        f"⭐ Очки: {score}\n"
        f"🎖 Лига: {'Знаток 🧠' if score > 50 else 'Новичок 🎒'}\n"
        f"🏫 Место в классе: 1-е!",
        keyboard=get_main_menu()
    )

@bot.on.message(text=["📚 Выбрать предмет", "предмет"])
async def choose_subject(message: Message):
    await message.answer("Выбери предмет для тренировки:", keyboard=get_subject_menu())

@bot.on.message(text=["⚡ Быстрый Квиз", "История", "Биология", "Русский язык"])
async def start_quiz(message: Message):
    subj = message.text if message.text in QUIZ_DATA else random.choice(list(QUIZ_DATA.keys()))
    question_obj = random.choice(QUIZ_DATA[subj])
    
    user_state[message.from_id] = {
        "correct": question_obj["correct"],
        "subj": subj
    }
    
    kb = Keyboard(one_time=True)
    for opt in question_obj["options"]:
        kb.add(Text(opt), color=KeyboardButtonColor.SECONDARY)
    kb.row().add(Text("🔙 Главное меню"), color=KeyboardButtonColor.NEGATIVE)
    
    await message.answer(
        f"📖 Предмет: {subj}\n\n"
        f"❓ Вопрос:\n{question_obj['q']}",
        keyboard=kb.get_json()
    )

@bot.on.message()
async def check_answer(message: Message):
    uid = message.from_id
    if uid in user_state:
        state = user_state[uid]
        if message.text == state["correct"]:
            user_scores[uid] = user_scores.get(uid, 0) + 10
            del user_state[uid]
            await message.answer(
                "🔥 ВЕРНО! +10 очков к твоему рейтингу! 🎉",
                keyboard=get_main_menu()
            )
        else:
            del user_state[uid]
            await message.answer(
                f"❌ Неверно. Правильный ответ: {state['correct']}",
                keyboard=get_main_menu()
            )
    else:
        await message.answer("Не понял команду. Нажми «Быстрый Квиз» или выбери предмет!", keyboard=get_main_menu())

if __name__ == "__main__":
    print("Бот успешно запущен и ожидает сообщений...")
    bot.run_forever()
