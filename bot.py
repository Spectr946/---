# -*- coding: utf-8 -*-
"""
Учебный бот для MAX: тесты, монеты, магазин сертификатов.
Запуск:
  1) pip install requests
  2) вставь токен в переменную TOKEN ниже
  3) python max_study_bot.py
"""

import json
import time
from datetime import date
from pathlib import Path

import requests

# ======================= НАСТРОЙКИ =======================
# ↓↓↓ ВСТАВЬ СЮДА ТОКЕН БОТА ИЗ КАБИНЕТА MAX (внутри кавычек) ↓↓↓
TOKEN = "f9LHodD0cOIu7xC-8uskgAZ_hnwea-FCZGeFvGMgrjiXVl9xBc3t8tczD6iEAaW7rLaM3_lzEkQbrD7eo8jE"
# ↑↑↑ больше токен нигде указывать не нужно ↑↑↑

BASE_URL = "https://botapi.max.ru"
DATA_FILE = Path("max_bot_data.json")
TEACHER_IDS = set()  # user_id учителей, например {123456789}
# ========================================================

TESTS = {
    "Биология|Строение клетки": [
        ("Какая органелла отвечает за синтез АТФ?",
         ["Митохондрия", "Рибосома", "Лизосома", "Ядро"], 1),
        ("Где хранится основная наследственная информация клетки?",
         ["Рибосома", "Ядро", "Вакуоль", "Мембрана"], 2),
        ("Какая структура синтезирует белок?",
         ["Рибосома", "Лизосома", "Хлоропласт", "Ядрышко"], 1),
        ("Какой органоид выполняет фотосинтез?",
         ["Митохондрия", "Хлоропласт", "Вакуоль", "Комплекс Гольджи"], 2),
        ("Как называется полужидкое содержимое клетки?",
         ["Цитоплазма", "Кариоплазма", "Строма", "Матрикс"], 1),
        ("Какую функцию выполняет клеточная мембрана?",
         ["Регулирует обмен веществ с окружающей средой",
          "Синтезирует белки", "Хранит ДНК", "Производит энергию"], 1),
        ("Как называется деление, дающее две одинаковые клетки?",
         ["Мейоз", "Митоз", "Оплодотворение", "Почкование"], 2),
        ("Что содержит клеточный сок?",
         ["Вакуоль", "Рибосома", "Ядрышко", "Мембрана"], 1),
        ("Какая структура есть у растительной клетки, но отсутствует у животной?",
         ["Клеточная стенка", "Ядро", "Митохондрия", "Рибосома"], 1),
        ("Какой органоид содержит пищеварительные ферменты?",
         ["Лизосома", "Митохондрия", "Хлоропласт", "Ядро"], 1),
    ],
    "История|Древняя Русь": [
        ("В каком году произошло Крещение Руси?",
         ["988", "862", "1054", "1147"], 1),
        ("Кто был первым князем Древнерусского государства?",
         ["Рюрик", "Игорь", "Святослав", "Владимир"], 1),
        ("Какое событие связано с 1242 годом?",
         ["Куликовская битва", "Ледовое побоище",
          "Стояние на Угре", "Взятие Казани"], 2),
        ("Кто написал «Повесть временных лет»?",
         ["Нестор", "Иларион", "Кирилл", "Даниил"], 1),
        ("В каком году состоялась Куликовская битва?",
         ["1240", "1380", "1480", "1497"], 2),
        ("Кто возглавил русское войско в 1380 году?",
         ["Александр Невский", "Дмитрий Донской", "Иван III", "Владимир Мономах"], 2),
        ("Что такое «Русская Правда»?",
         ["Свод законов", "Летопись", "Устав церкви", "Сборник былин"], 1),
        ("При каком князе Русь приняла христианство?",
         ["Олег", "Игорь", "Владимир Святославич", "Ярослав Мудрый"], 3),
        ("Какой город был столицей Древней Руси?",
         ["Киев", "Москва", "Новгород", "Владимир"], 1),
        ("Кто в 1480 году положил конец ордынской зависимости?",
         ["Иван Калита", "Дмитрий Донской", "Иван III", "Василий II"], 3),
    ],
}

SHOP = {
    "grade5": {"title": "Сертификат на оценку «5»", "price": 100, "stock": 1},
    "plus1": {"title": "Сертификат на +1 балл (кроме контрольных)", "price": 75, "stock": 2},
    "retake": {"title": "Сертификат на пересдачу / переписывание", "price": 50, "stock": 2},
    "homework": {"title": "Освобождение от домашнего задания", "price": 30, "stock": 2},
}

# ======================= ДАННЫЕ =======================

def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            print("Файл данных повреждён, создаю новый.")
    return {
        "users": {},
        "shop_stock": {key: item["stock"] for key, item in SHOP.items()},
        "requests": [],
        "daily": {},
    }


data = load_data()


def save_data():
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_user(user_id):
    user_id = str(user_id)
    data["users"].setdefault(
        user_id, {"coins": 0, "state": None, "results": []}
    )
    return data["users"][user_id]


# ======================= АДАПТЕР MAX API =======================

def api(method, params=None, payload=None, http_method="GET"):
    """Один запрос к Bot API. Токен подставляется здесь."""
    params = dict(params or {})
    params["access_token"] = TOKEN
    url = f"{BASE_URL}/{method}"
    if http_method == "GET":
        response = requests.get(url, params=params, timeout=60)
    else:
        response = requests.post(url, params=params, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def get_updates(marker=None, timeout=30):
    params = {"timeout": timeout, "limit": 100}
    if marker:
        params["marker"] = marker
    return api("updates", params)


def send_message(chat_id, text, buttons=None):
    message = {"text": text}
    if buttons:
        message["attachments"] = [
            {"type": "inline_keyboard", "payload": {"buttons": buttons}}
        ]
    return api("messages", {"chat_id": chat_id}, message, "POST")


def answer_callback(callback_id, notification, buttons=None, text=None):
    payload = {"notification": notification}
    if text:
        message = {"text": text}
        if buttons:
            message["attachments"] = [
                {"type": "inline_keyboard", "payload": {"buttons": buttons}}
            ]
        payload["message"] = message
    return api("answers", {"callback_id": callback_id}, payload, "POST")


# ======================= КЛАВИАТУРЫ =======================

def button(text, payload):
    return {"type": "callback", "text": text, "payload": payload}


def main_menu():
    return [
        [button("Пройти мини-тест", "test"), button("Мой баланс", "balance")],
        [button("Магазин", "shop"), button("Мои заявки", "requests")],
    ]


def tests_menu():
    rows = [[button(key.split("|")[1], f"topic:{key}")] for key in TESTS]
    rows.append([button("Назад", "menu")])
    return rows


def shop_menu():
    rows = []
    for key, item in SHOP.items():
        stock = data["shop_stock"].get(key, 0)
        rows.append([button(f"{item['title']} — {item['price']} монет (ост. {stock})", f"buy:{key}")])
    rows.append([button("Назад", "menu")])
    return rows


# ======================= ЛОГИКА =======================

def show_question(chat_id, user_id):
    user = get_user(user_id)
    state = user["state"]
    key, index = state["test"], state["index"]
    question, options, _ = TESTS[key][index]

    rows = [
        [button(options[0], "ans:1"), button(options[1], "ans:2")],
        [button(options[2], "ans:3"), button(options[3], "ans:4")],
    ]
    send_message(
        chat_id,
        f"Вопрос {index + 1}/10\n\n{question}",
        rows,
    )


def start_test(chat_id, user_id, key):
    today = date.today().isoformat()
    daily_key = f"{user_id}:{today}"
    if data["daily"].get(daily_key):
        send_message(chat_id, "Сегодняшний мини-тест уже пройден. Возвращайся завтра!", main_menu())
        return

    user = get_user(user_id)
    user["state"] = {"test": key, "index": 0, "score": 0}
    save_data()
    show_question(chat_id, user_id)


def handle_answer(chat_id, user_id, option_number):
    user = get_user(user_id)
    if not user["state"]:
        send_message(chat_id, "Сейчас нет активного вопроса.", main_menu())
        return

    state = user["state"]
    question, options, correct = TESTS[state["test"]][state["index"]]

    if option_number == correct:
        state["score"] += 1
        feedback = "Верно!"
    else:
        feedback = f"Неверно. Правильный ответ: {options[correct - 1]}."

    state["index"] += 1

    if state["index"] < 10:
        save_data()
        send_message(chat_id, feedback)
        show_question(chat_id, user_id)
        return

    test_key = state["test"]
    score = state["score"]
    subject, topic = test_key.split("|")

    user["coins"] += score
    user["results"].append(
        {"subject": subject, "topic": topic, "score": score, "date": date.today().isoformat()}
    )
    user["state"] = None
    data["daily"][f"{user_id}:{date.today().isoformat()}"] = True
    save_data()

    send_message(
        chat_id,
        f"{feedback}\n\nТест завершён: {score}/10 правильных.\n"
        f"Начислено монет: {score}.\nБаланс: {user['coins']} монет.",
        main_menu(),
    )


def show_balance(chat_id, user_id):
    user = get_user(user_id)
    send_message(chat_id, f"Баланс: {user['coins']} монет.", main_menu())


def buy_item(chat_id, user_id, item_key):
    item = SHOP.get(item_key)
    if not item:
        send_message(chat_id, "Такого сертификата нет.", main_menu())
        return

    stock = data["shop_stock"].get(item_key, 0)
    if stock <= 0:
        send_message(chat_id, "Этих сертификатов сейчас нет в наличии.", main_menu())
        return

    user = get_user(user_id)
    if user["coins"] < item["price"]:
        send_message(
            chat_id,
            f"Не хватает монет. Нужно {item['price']}, у тебя {user['coins']}.",
            main_menu(),
        )
        return

    user["coins"] -= item["price"]
    data["shop_stock"][item_key] = stock - 1
    request_id = len(data["requests"]) + 1
    data["requests"].append(
        {
            "id": request_id,
            "user_id": str(user_id),
            "item": item["title"],
            "status": "ожидает подтверждения учителя",
        }
    )
    save_data()

    send_message(
        chat_id,
        f"Заявка оформлена: {item['title']}.\n"
        f"Списано {item['price']} монет. Остаток: {user['coins']}.\n"
        "Награда выдаётся после подтверждения учителем.",
        main_menu(),
    )


def show_requests(chat_id, user_id):
    my_requests = [r for r in data["requests"] if r["user_id"] == str(user_id)]
    if not my_requests:
        send_message(chat_id, "Заявок пока нет.", main_menu())
        return

    lines = [f"№{r['id']} — {r['item']} — {r['status']}" for r in my_requests]
    send_message(chat_id, "Твои заявки:\n" + "\n".join(lines), main_menu())


def handle_command(chat_id, user_id, name):
    if name in {"menu", "start"}:
        get_user(user_id)
        send_message(
            chat_id,
            "Учебный бот: проверочные тесты, монеты и магазин наград.\n"
            "Выбери действие кнопкой ниже.",
            main_menu(),
        )
    elif name == "test":
        send_message(chat_id, "Выбери тему теста:", tests_menu())
    elif name.startswith("topic:"):
        start_test(chat_id, user_id, name.split(":", 1)[1])
    elif name.startswith("ans:"):
        handle_answer(chat_id, user_id, int(name.split(":", 1)[1]))
    elif name == "balance":
        show_balance(chat_id, user_id)
    elif name == "shop":
        send_message(
            chat_id,
            "Магазин сертификатов. Ассортимент ограничен и обновляется раз в триместр.",
            shop_menu(),
        )
    elif name.startswith("buy:"):
        buy_item(chat_id, user_id, name.split(":", 1)[1])
    elif name == "requests":
        show_requests(chat_id, user_id)
    elif name.startswith("confirm:") and user_id in TEACHER_IDS:
        request_id = int(name.split(":", 1)[1])
        for request in data["requests"]:
            if request["id"] == request_id:
                request["status"] = "подтверждено учителем"
                save_data()
        send_message(chat_id, "Заявка подтверждена.", main_menu())
    else:
        send_message(chat_id, "Не понял команду. Открой меню.", main_menu())


def handle_update(update):
    update_type = update.get("update_type")

    if update_type in {"bot_started", "message_created"}:
        message = update.get("message", {})
        chat_id = message.get("recipient", {}).get("chat_id")
        user_id = message.get("sender", {}).get("user_id")
        if chat_id is None or user_id is None:
            return
        text = (message.get("body", {}).get("text") or "").strip().lower()
        if not text or text in {"/start", "начать", "старт", "привет"}:
            handle_command(chat_id, user_id, "menu")
        else:
            handle_command(chat_id, user_id, text)

    elif update_type == "message_callback":
        callback = update.get("callback", {})
        chat_id = update.get("message", {}).get("recipient", {}).get("chat_id")
        user_id = callback.get("user", {}).get("user_id")
        payload = callback.get("payload")
        callback_id = callback.get("callback_id")
        if not (chat_id and user_id and payload):
            return
        answer_callback(callback_id, "Принято")
        handle_command(chat_id, user_id, payload)


def main():
    if not TOKEN or "ВСТАВЬ" in TOKEN:
        raise SystemExit("Сначала вставь токен бота в переменную TOKEN.")

    print("Бот запущен. Остановка — Ctrl+C.")
    marker = None

    while True:
        try:
            response = get_updates(marker)
        except requests.RequestException as error:
            print("Ошибка сети:", error)
            time.sleep(5)
            continue

        marker = response.get("marker", marker)
        for update in response.get("updates", []):
            try:
                handle_update(update)
            except Exception as error:  # чтобы одна ошибка не роняла бота
                print("Ошибка обработки обновления:", error)


if __name__ == "__main__":
    main()
