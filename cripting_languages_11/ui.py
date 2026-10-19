import pygame
from constants import COLORS, GAME_MESSAGES


def draw_text_centered(surface, text, y, font, color=(200, 200, 200)):
    """Рисует текст по центру экрана по горизонтали."""
    rendered = font.render(text, True, color) # превращает строку в поверхность (картинку) True - включить сглаживание
    x = surface.get_width() // 2 - rendered.get_width() // 2 # центр экрана по x
    surface.blit(rendered, (x, y))


def draw_menu(surface, font, big_font):
    """Стартовый экран."""
    surface.fill(COLORS["bg"])
    draw_text_centered(surface, GAME_MESSAGES["title"], 120, big_font, COLORS["menu_title"])
    draw_text_centered(surface, GAME_MESSAGES["subtitle"], 180, font, COLORS["text"])
    draw_text_centered(surface, GAME_MESSAGES["controls"], 300, font, COLORS["text"])
    draw_text_centered(surface, GAME_MESSAGES["menu_hint"], 400, font, COLORS["menu_title"])


def draw_game_over(surface, win, font, big_font):
    """Экран завершения игры."""
    surface.fill(COLORS["bg"])
    if win:
        msg = GAME_MESSAGES["win"]
        color = COLORS["wave"]
    else:
        msg = GAME_MESSAGES["lose"]
        color = COLORS["enemy"]
    draw_text_centered(surface, msg, 220, big_font, color)
    draw_text_centered(surface, GAME_MESSAGES["restart"], 300, font, COLORS["text"])


