import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # считать .env
BOT_TOKEN = os.getenv("BOT_TOKEN")# читает токен

BASE_DIR = Path(__file__).resolve().parent.parent# где лежит сама игра

LOG_PATH = BASE_DIR / "radar_log.txt" # игроки
MAP_PATH = BASE_DIR / "radar_map.json" # карта

SESSION_DIR = Path(__file__).resolve().parent / "sessions" # пользователи в тг
SESSION_DIR.mkdir(exist_ok=True) # безопасное создание