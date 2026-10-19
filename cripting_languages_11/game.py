"""
Основной игровой цикл. Здесь связываются модули воедино.
"""

import pygame
import sys

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    COLORS,
    GAME_MESSAGES,
    PLAYER_START,
    ENEMY_POSITIONS,
)
from level import build_walls, draw_walls
from player import Player
from enemy import Enemy
from sound_wave import SoundWave
from ui import draw_menu, draw_game_over

from map_loader import load_map #лаб 2
from logger import log_result


def main():
    pygame.init() # запуск всех подсистем Pygame
    pygame.font.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # создаёт окно
    pygame.display.set_caption("Echo Radar — Эхо-Локатор") # заголовок окна

    clock = pygame.time.Clock() # контроль FPS
    font = pygame.font.Font(None, 28)
    big_font = pygame.font.Font(None, 64)

    # cостояния игры
    STATE_MENU = "MENU"
    STATE_PLAY = "PLAY"
    STATE_OVER = "OVER"
    STATE_ENTER_NAME = "ENTER_NAME"  #НОВОЕ СОСТОЯНИЕ
    state = STATE_MENU
    win = False

    # игровые объекты
    walls = []
    player = None
    enemies = []
    waves = []

    # переменные для ЛР 2 (счётчик и время)
    waves_fired = 0
    start_time = 0

    # НОВЫЕ переменные для ввода имени
    player_name = ""
    final_time = 0

    # загрузить карту
    level_matrix, fade_speed = load_map()

    running = True
    while running:
        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == STATE_MENU and event.key == pygame.K_SPACE:
                    # инициализация игры
                    walls = build_walls(level_matrix)
                    player = Player(*PLAYER_START)
                    enemies = [Enemy(x, y) for x, y in ENEMY_POSITIONS]
                    waves = []
                    win = False
                   

                    waves_fired = 0 # Счётчик импульсов
                    start_time = pygame.time.get_ticks() # Засекаем время старта
                    state = STATE_PLAY

                elif state == STATE_OVER and event.key == pygame.K_r: # рестарт
                    state = STATE_MENU

                elif state == STATE_PLAY and event.key == pygame.K_SPACE: # запуск звуковой волны от игрока
                   waves.append(SoundWave(player.rect.centerx, player.rect.centery, fade_speed=fade_speed))
                   waves_fired += 1


                # Ввод имени после победы
                elif state == STATE_ENTER_NAME and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER: 
                        # Нажат Enter — сохраняем результат и переходим на финальный экран
                        log_result(player_name, waves_fired, final_time)
                        state = STATE_OVER
                    elif event.key == pygame.K_BACKSPACE: 
                        # Нажат Backspace — удаляем последний символ
                        player_name = player_name[:-1]
                    else:
                        # Добавляем введённый символ (ограничим длину 15 символами)
                        if event.unicode.isprintable() and len(player_name) < 15:
                            player_name += event.unicode

        # обновление и отрисовка
        if state == STATE_MENU:
            draw_menu(screen, font, big_font)

        elif state == STATE_PLAY:
            # управление
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            if dx != 0 or dy != 0: # если хоть какое-то движение
                player.move(dx, dy, walls)

            # обновление волн
            for wave in waves:
                wave.update(walls, enemies)
            # волна удаляется только через 40 кадров после деактивации, чтобы затухание успело погасить все подсвеченные объекты
            waves = [w for w in waves if w.active or w.dead_frames < 40]

            # проверка столкновения с врагами
            for enemy in enemies:
                if player.rect.colliderect(enemy.rect):
                    win = False
                    state = STATE_OVER

            
            #если хитбокс игрока вышел за пределы экрана - вышел из лабиринта
            if (player.rect.left < 0 
                or player.rect.right > WINDOW_WIDTH 
                or player.rect.top < 0 
                or player.rect.bottom > WINDOW_HEIGHT):
                if state == STATE_PLAY: # защита от повторного срабатывания
                    win = True
                    final_time = (pygame.time.get_ticks() - start_time) / 1000
                    player_name = "" # очищаем поле ввода
                    state = STATE_ENTER_NAME # <-- переходим на экран ввода имени

            # отрисовка
            screen.fill(COLORS["bg"])
            draw_walls(screen, walls)
            for enemy in enemies:
                enemy.draw(screen)
            for wave in waves:
                wave.draw(screen)
        
        elif state == STATE_ENTER_NAME:
            # Отрисовка экрана ввода имени
            screen.fill(COLORS["bg"])
            
            # Заголовок
            win_text = big_font.render(GAME_MESSAGES["win"], True, (0, 255, 100))
            screen.blit(win_text, (WINDOW_WIDTH // 2 - win_text.get_width() // 2, 150))
            
            # Подсказка
            prompt = font.render("Введите имя и нажмите Enter:", True, COLORS["text"])
            screen.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 250))
            
            # Прямоугольник поля ввода
            input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 300, 300, 40)
            pygame.draw.rect(screen, (40, 40, 40), input_rect) # Фон поля
            pygame.draw.rect(screen, COLORS["wave"], input_rect, 2) # Рамка поля
            
            # Введённый текст + мигающий курсор (просто черта)
            name_text = font.render(player_name + "|", True, COLORS["text"])
            screen.blit(name_text, (input_rect.x + 10, input_rect.y + 10))
            
            # Показываем статистику
            time_text = font.render(f"Время: {final_time:.1f} сек. | Импульсов: {waves_fired}", True, COLORS["text"])
            screen.blit(time_text, (WINDOW_WIDTH // 2 - time_text.get_width() // 2, 370))

        elif state == STATE_OVER:
            draw_game_over(screen, win, font, big_font)
        
            
      

        elif state == STATE_OVER:
            draw_game_over(screen, win, font, big_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()