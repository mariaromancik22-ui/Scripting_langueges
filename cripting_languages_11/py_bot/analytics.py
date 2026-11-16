import re # извлекать слова из строк
def parse_log(log_path): # ивзлекать инфу из лога
    records = []# пустой список
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r"Игрок:\s*([^|]+)\s*\|\s*Импульсов:\s*(\d+)\s*\|\s*Время:\s*([\d.]+)", line) # шаблон записи понятный для человека
                if match:
                    name = match.group(1).strip()
                    pulses = int(match.group(2))
                    time_sec = float(match.group(3))
                    
                    if pulses < 0 or time_sec <= 0:
                        continue  # пропускает некорректные строки
                    records.append({"name": name, "pulses": pulses, "time": time_sec}) # переделывает запись, понятную человеком в понятную для компьтера
    except FileNotFoundError:
        return None
    return records

def get_leaderboard(records, limit=5):
    # рейтинг по времени (меньше = лучше)
    sorted_recs = sorted(records, key=lambda r: (r["time"], r["pulses"]))# сортировка по времени, если одинаковое то по импульсам
    return sorted_recs[:limit]

def get_player_stats(records, player_name):
    # личная статистика
    player_recs = [r for r in records if r["name"] == player_name] # найти по имени. войдут все записи с совпадающим именем
    if not player_recs:
        return None
    best_time = min(r["time"] for r in player_recs)
    total_runs = len(player_recs)
    avg_pulses = sum(r["pulses"] for r in player_recs) / total_runs
    return {"best_time": best_time, "total_runs": total_runs, "avg_pulses": round(avg_pulses, 1)}

def get_achievements(records):
    # возвращает список достижений
    if not records:
        return []
    
    fastest = min(records, key=lambda r: r["time"])
    quietest = min(records, key=lambda r: r["pulses"]) 
    
    return [
        f"⚡ Скороход: {fastest['name']} ({fastest['time']} сек.)",
        f"🤫 Тихий шаг (минимум импульсов): {quietest['name']} ({quietest['pulses']} шт.)"
    ]