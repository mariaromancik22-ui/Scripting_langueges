import asyncio
import json
import logging
import csv
import io
import os
from aiogram import Bot, Dispatcher, F # бот, маршрутизатор, инструмент для фильтрации
from aiogram.filters import Command # команды со слэша
from aiogram.fsm.context import FSMContext # объект управления паматью текущего пользователя
from aiogram.fsm.state import State, StatesGroup # машина состояний
from aiogram.types import Message, CallbackQuery # сообщение, инлайн-кнопка
from aiogram.exceptions import TelegramBadRequest # для исключений

from config import BOT_TOKEN, LOG_PATH, MAP_PATH, SESSION_DIR
from keyboards import main_menu, back_menu
from analytics import parse_log, get_leaderboard, get_player_stats, get_achievements
from sessions import load_session, save_session

# логирование 
logging.basicConfig(
    filename="bot_flight.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# состояния
class BotStates(StatesGroup):
    MENU = State()
    WAIT_NAME = State()
    WAIT_CSV = State()

# безопасное редактирование сообщения бота
async def safe_edit(message, text, keyboard):
    try:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

# ФУНКЦИИ ИСПОЛЬЗУЮЩИЕ АНАЛИТИКУ
# топ 5
async def _get_top_text():
    records = parse_log(LOG_PATH)
    if not records:
        return "Файл radar_log.txt не найден или пуст."
    top = get_leaderboard(records, limit=5)
    text = "🏆 **Топ-5 эхолокаторов:**\n\n"
    for i, r in enumerate(top, 1):
        text += f"{i}. {r['name']} — {r['time']} сек. (импульсов: {r['pulses']})\n"
    return text
# достижения
async def _get_achievements_text():
    records = parse_log(LOG_PATH)
    if not records:
        return "Лог-файл не найден."
    achievements = get_achievements(records)
    if not achievements:
        return "Нет достижений."
    return "🎖 **Достижения:**\n\n" + "\n".join(achievements)
# информация о карте
async def _get_map_info():
    try:
        with open(MAP_PATH, "r", encoding="utf-8") as f:
            map_data = json.load(f)
        speed = map_data.get("fade_speed", "Неизвестно")
        return f"🗺 **Инфо о карте:**\n\nСкорость затухания: {speed}\nМатрица загружена успешно."
    except Exception:
        return "Не удалось прочитать radar_map.json"

# сообщение принять файл от пользователя
async def _start_upload(state: FSMContext, edit_message=None, answer_message=None):
    await state.set_state(BotStates.WAIT_CSV)
    text = "📤 Отправьте CSV-файл с результатами (Игрок, Импульсы, Время)."
    if edit_message:
        await safe_edit(edit_message, text, back_menu())
    if answer_message:
        await answer_message.answer(text, reply_markup=back_menu())
       
# уведомление. переключает флаг подписки в сессии и возвращает текстовый статус.
def _toggle_watch(user_id: int) -> str:
    session = load_session(user_id)
    session["watch_enabled"] = not session.get("watch_enabled", False)
    save_session(user_id, session)
    return "включены" if session["watch_enabled"] else "выключены"

# команды
# @ - декоратор. Он «прикрепляет» функцию к диспетчеру и говорит: “Вызывай эту функцию, когда произойдёт вот такое событие”
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(BotStates.MENU) # переход в состояние меню
    logging.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer(
        "Привет! Я бот-аналитик игры «Эхо-Локатор».\nВыбери действие:", 
        reply_markup=main_menu()# прикрепляет к сообщению клавиатуру
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    logging.info(f"Пользователь {message.from_user.id} запросил помощь")
    text = (
        "📋 **Доступные команды:**\n"
        "/start — запуск бота\n"
        "/help — эта справка\n"
        "/top — топ-5 игроков\n"
        "/stats — статистика игрока\n"
        "/achievements — награды\n"
        "/upload — загрузить CSV с результатами\n"
        "/watch — включить/выключить уведомления"
    )
    await message.answer(text, reply_markup=main_menu())

@dp.message(Command("top"))
async def cmd_top(message: Message, state: FSMContext):
    await state.set_state(BotStates.MENU)
    text = await _get_top_text()
    await message.answer(text, reply_markup=back_menu(), parse_mode="Markdown")

@dp.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext):
    await state.set_state(BotStates.WAIT_NAME)
    await message.answer("Введите ваше имя игрока:")

@dp.message(Command("achievements"))
async def cmd_achievements(message: Message, state: FSMContext):
    await state.set_state(BotStates.MENU)
    text = await _get_achievements_text()
    await message.answer(text, reply_markup=back_menu(), parse_mode="Markdown")

@dp.message(Command("upload"))
async def cmd_upload(message: Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} инициировал загрузку файла")
    await _start_upload(state, answer_message=message)

@dp.message(Command("watch"))
async def cmd_watch(message: Message, state: FSMContext):
    user_id = message.from_user.id
    status = _toggle_watch(user_id)
    logging.info(f"Пользователь {user_id} изменил статус уведомлений на {status}")
    await message.answer(f"🔔 Уведомления о новых записях {status}.")


# хендлеры кнопок
@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.MENU)
    await safe_edit(callback.message, "Главное меню:", main_menu())
    await callback.answer()

@dp.callback_query(F.data == "top")
async def show_top(callback: CallbackQuery):
    text = await _get_top_text()
    await safe_edit(callback.message, text, back_menu())
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def ask_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.WAIT_NAME)
    await safe_edit(callback.message, "Введите ваше имя игрока:", back_menu())
    await callback.answer()

# не кнопка, а обработчик текстового сообщения
@dp.message(BotStates.WAIT_NAME)
async def show_stats(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text.strip()
    
    session = load_session(user_id)
    session["name"] = name
    save_session(user_id, session) #сохраняем имя что ввёл пользователь
    
    records = parse_log(LOG_PATH)
    if not records:
        await message.answer("Лог-файл не найден.")
        await state.set_state(BotStates.MENU)
        return
    
    stats = get_player_stats(records, name)
    if not stats:
        await message.answer(f"Игрок '{name}' не найден.", reply_markup=back_menu())
    else:
        text = (
            f"📊 **Статистика {name}:**\n\n"
            f"🏃 Всего забегов: {stats['total_runs']}\n"
            f"⏱ Лучшее время: {stats['best_time']} сек.\n"
            f"📡 В среднем импульсов: {stats['avg_pulses']}"
        )
        await message.answer(text, reply_markup=back_menu(), parse_mode="Markdown")
        
    await state.set_state(BotStates.MENU)

@dp.callback_query(F.data == "achievements")
async def show_achievements(callback: CallbackQuery):
    text = await _get_achievements_text()
    await safe_edit(callback.message, text, back_menu())
    await callback.answer()

@dp.callback_query(F.data == "map_info")
async def show_map_info(callback: CallbackQuery):
    text = await _get_map_info()
    await safe_edit(callback.message, text, back_menu())
    await callback.answer()

@dp.callback_query(F.data == "upload")
async def cb_upload(callback: CallbackQuery, state: FSMContext):
    logging.info(f"Пользователь {callback.from_user.id} нажал кнопку загрузки")
    await _start_upload(state, edit_message=callback.message)
    await callback.answer()

@dp.callback_query(F.data == "watch_toggle")
async def cb_watch_toggle(callback: CallbackQuery):
    user_id = callback.from_user.id
    status = _toggle_watch(user_id)
    logging.info(f"Пользователь {user_id} изменил статус уведомлений на {status}")
    
    await callback.message.answer(
        f"🔔 Уведомления о новых записях {status}.\n\nВыбери действие:",
        reply_markup=main_menu()
    )
    await callback.answer()


# загрузка файла
@dp.message(BotStates.WAIT_CSV, F.document) 
async def process_csv(message: Message, state: FSMContext):
    file_name = message.document.file_name
    logging.info(f"Пользователь {message.from_user.id} отправил файл {file_name}")
    
    file = await bot.get_file(message.document.file_id)
    file_io = io.BytesIO() #виртуальный файл в памяти, не на диске
    await bot.download_file(file.file_path, destination=file_io)
    file_io.seek(0)
    
    try:
        content = file_io.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))# читает содержимое. первая строка - заголовки
        valid_records = []
        
        for row in reader:
            try:
                name = row.get('Игрок') or row.get('Имя') or row.get('name') # достать имя по ключу. если разные названия колонок
                pulses = int(row.get('Импульсы') or row.get('pulses'))
                time_sec = float(row.get('Время') or row.get('time') or row.get('Время (сек)'))
                
                if pulses >= 0 and time_sec > 0:
                    valid_records.append({"name": name, "pulses": pulses, "time": time_sec})
            except (ValueError, TypeError):
                continue
        
        if not valid_records:
            await message.answer("❌ Не удалось распознать корректные данные в CSV.")
        else:
            csv_path = LOG_PATH.parent / "radar_records.csv"
            file_exists = csv_path.exists() and csv_path.stat().st_size > 0
            
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Имя", "Время (сек)", "Импульсов"])
                for rec in valid_records:
                    writer.writerow([rec["name"], round(rec["time"], 1), rec["pulses"]])
            
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                for rec in valid_records:
                    f.write(f"Игрок: {rec['name']} | Импульсов: {rec['pulses']} | Время: {rec['time']:.1f} сек.\n")
            
            await message.answer(f"✅ Успешно обработано и сохранено {len(valid_records)} записей.")
            logging.info(f"Сохранено {len(valid_records)} записей из файла {file_name}")
            
            # уведомление подписчиков
            for file in os.listdir(SESSION_DIR):
                if file.endswith(".json"):
                    try:
                        sub_id = int(file.replace(".json", ""))
                        sub_session = load_session(sub_id)
                        if sub_session.get("watch_enabled"):
                            await bot.send_message(sub_id, f"🔔 Загружено {len(valid_records)} записей.")
                    except Exception:
                        pass
            
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
        await message.answer("❌ Ошибка при чтении файла. Убедитесь, что это корректный текстовый CSV.")
    
    await state.set_state(BotStates.MENU)


# обработчик ошибок
@dp.errors()
async def error_handler(event, exception):
    logging.error(f"Необработанная ошибка: {exception}", exc_info=True)
    return True


# запуск 
async def main():
    logging.info("Оператор Радара запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())