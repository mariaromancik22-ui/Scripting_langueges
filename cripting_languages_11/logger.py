import csv
import os
from pathlib import Path

# пути к файлам (создаются в той же папке, где лежит скрипт)
LOG_PATH = Path(__file__).with_name("radar_log.txt")
CSV_PATH = Path(__file__).with_name("radar_records.csv")


def log_result(name, wave_count, time_sec):
    """
    1. Записывает результат в текстовый лог (radar_log.txt).
    2. Дописывает результат в таблицу рекордов (radar_records.csv).
    """
    # запись в текстовый файл
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"Игрок: {name} | Импульсов: {wave_count} | Время: {time_sec:.1f} сек.\n")
    
    # запись в CSV 
    # проверяем существует ли файл и не пустой ли он
    file_exists = CSV_PATH.exists() and CSV_PATH.stat().st_size > 0
    
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # если файла нет (первый запуск) - пишем заголовки
        if not file_exists:
            writer.writerow(["Имя", "Время (сек)", "Импульсов"])
        # записываем данные игрока
        writer.writerow([name, round(time_sec, 1), wave_count])
        
    print(f"Результат сохранён в {LOG_PATH} и {CSV_PATH}")