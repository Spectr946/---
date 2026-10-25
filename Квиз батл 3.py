# -*- coding: utf-8 -*-
"""
Сферум Квиз-Батл — версия для VK API / vk_api.
Запуск: python quiz_bot.py
"""

import json
import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


TOKEN = "vk1.a.Xrp8jBSN8TOy2oiIeVsPC4C2iIZ1MwZw2V0GrV4Irzuld975pXR0_wa09LM8vFP9GnUf59EBGzPEj5-J2HsHEBx8iyUgrenY9nEXzVov-5UBQHuLZ45OFSXDu2esXtbN7jUocSSZZQEc3AT6VboarA9Sbn6T7NUFe9_pvBGFeXowJ9oKoCJV3_ha5QYbfj8G23tirdwuiVEYdmBxLIKd0w"
GROUP_ID = 241787154  # ID сообщества из адреса club241787154

# Очки и текущие вопросы хранятся в памяти.
# При перезапуске программы они сбросятся.
user_scores = {}
user_state = {}

QUIZ_DATA = {
    "История": [
        {
            "q": "В каком году произошло Ледовое побоище?",
            "options": ["1242", "1380", "1480", "1812"],
            "correct": "1242",
        },
        {
            "q": "Кто был первым царём из династии Романовых?",
            "options": ["Михаил", "Пётр I", "Иван Грозный", "Алексей"],
            "correct": "Михаил",
        },
    ],
    "Биология": [
        {
            "q": "Какая органелла клетки отвечает за синтез энергии (АТФ)?",
            "options": ["Митохондрия", "Рибосома", "Лизосома", "Ядро"],
            "correct": "Митохондрия",
        },
    ],
    "Русский язык": [
        {
            "q": "В каком слове ударение падает на второй слог?",
            "options": ["звонИт", "тОрты", "бАнты", "шАрфы"],
            "correct": "звонИт",
        },
    ],
}


def make_keyboard(buttons, one_time=False):
    """Создаёт клавиатуру VK из списка (текст, цвет, payload)."""
    keyboard = VkKeyboard(one_time=one_time)

    for index, (label, color, payload) in enumerate(buttons):
        keyboard.add_button(
            label=label,
            color=color,
            payload=json.dumps(payload, ensure_ascii=False) if payload else None,
        )

        # Располагаем по две кнопки в строке.
        if index % 2 == 1 and index != len(buttons) - 1:
            keyboard.add_line()

    return keyboard.get_keyboard()


def main_menu():
    return make_keyboard([
        ("⚡️ Быстрый Квиз", VkKeyboardColor.POSITIVE, {"cmd": "quiz"}),
        ("🏆 Мой рейтинг", VkKeyboardColor.PRIMARY, {"cmd": "rating"}),
        ("📚 Выбрать предмет", VkKeyboardColor.SECONDARY, {"cmd": "subject"}),
    ])


def subject_menu():
    buttons = [
        (subject, VkKeyboardColor.PRIMARY, {"subj": subject})
        for subject in QUIZ_DATA
    ]
    buttons.append(("🔙 Главное меню", VkKeyboardColor.NEGATIVE, {"cmd": "menu"}))
    return make_keyboard(buttons)


def answer_keyboard(options):
    buttons = [
        (option, VkKeyboardColor.SECONDARY, {"answer": option})
        for option in options
    ]
    buttons.append(("🔙 Главное меню", VkKeyboardColor.NEGATIVE, {"cmd": "menu"}))
    return make_keyboard(buttons, one_time=True)


def send(vk, peer_id, text, keyboard=None):
    """Отправляет сообщение в личный или групповой диалог."""
    params = {
        "peer_id": peer_id,
        "message": text,
        "random_id": 0,
    }
    if keyboard is not None:
        params["keyboard"] = keyboard
    vk.messages.send(**params)


def start_quiz(vk, peer_id, user_id, subject=None):
    if subject not in QUIZ_DATA:
        subject = random.choice(list(QUIZ_DATA.keys()))

    question = random.choice(QUIZ_DATA[subject])
    user_state[user_id] = {
        "correct": question["correct"],
        "subject": subject,
    }

    send(
        vk,
        peer_id,
        f"📖 Предмет: {subject}\n\n"
        f"❓ Вопрос:\n{question['q']}\n\n"
        "Выбери ответ кнопкой:",
        answer_keyboard(question["options"]),
    )


def handle_message(vk, message):
    peer_id = message.get("peer_id")
    user_id = message.get("from_id")
    text = (message.get("text") or "").strip()
    lower_text = text.lower()

    # Payload приходит при нажатии на кнопку; если его нет, используем текст.
    payload = message.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {}
    if not isinstance(payload, dict):
        payload = {}

    command = payload.get("cmd")
    subject = payload.get("subj")
    button_answer = payload.get("answer")

    # Старт, меню и возврат в меню.
    if lower_text in {"начать", "привет", "старт", "меню"} or command == "menu":
        user_scores.setdefault(user_id, 0)
        user_state.pop(user_id, None)
        send(
            vk,
            peer_id,
            "👋 Привет! Добро пожаловать в «Сферум Квиз-Батл»!\n\n"
            "Сражайся в интеллектуальных квизах, зарабатывай очки "
            "и поднимайся в рейтинге! 🚀",
            main_menu(),
        )
        return

    # Рейтинг.
    if lower_text == "рейтинг" or "Мой рейтинг" in text or command == "rating":
        score = user_scores.get(user_id, 0)
        league = "Знаток 🧠" if score > 50 else "Новичок 🎒"
        send(
            vk,
            peer_id,
            f"📊 Твоя статистика:\n"
            f"⭐️ Очки: {score}\n"
            f"🎖 Лига: {league}\n"
            f"🏫 Место в классе: пока нет данных",
            main_menu(),
        )
        return

    # Показать предметы.
    if lower_text == "предмет" or "Выбрать предмет" in text or command == "subject":
        user_state.pop(user_id, None)
        send(vk, peer_id, "Выбери предмет для тренировки:", subject_menu())
        return

    # Быстрый квиз или выбор предмета.
    if command == "quiz" or "Быстрый Квиз" in text:
        start_quiz(vk, peer_id, user_id)
        return

    if subject in QUIZ_DATA or text in QUIZ_DATA:
        start_quiz(vk, peer_id, user_id, subject or text)
        return

    # Проверка ответа на активный вопрос.
    if user_id in user_state:
        state = user_state.pop(user_id)
        answer = button_answer or text

        if answer == state["correct"]:
            user_scores[user_id] = user_scores.get(user_id, 0) + 10
            send(
                vk,
                peer_id,
                "🔥 Верно! +10 очков к твоему рейтингу! 🎉",
                main_menu(),
            )
        else:
            send(
                vk,
                peer_id,
                f"❌ Неверно. Правильный ответ: {state['correct']}",
                main_menu(),
            )
        return

    send(
        vk,
        peer_id,
        "Не понял команду. Нажми «⚡️ Быстрый Квиз» или выбери предмет.",
        main_menu(),
    )


def main():
    if TOKEN == "ВСТАВЬ_НОВЫЙ_ТОКЕН":
        raise SystemExit("Сначала вставь токен сообщества в переменную TOKEN.")

    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    print("Бот запущен. Для остановки нажми Ctrl+C.")

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.message
            handle_message(vk, message)


if __name__ == "__main__":
    main()
