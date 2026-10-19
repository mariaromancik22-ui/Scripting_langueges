"""
Класс звуковой волны, создаваемой при импульсе игрока.

Волна расширяется от точки игрока и подсвечивает стены и врагов,
находящихся в диапазоне R±WAVE_THICKNESS.
После деактивации волна продолжает «дотлевать» ещё несколько кадров,
чтобы все подсвеченные объекты успели полностью погаснуть.
"""

import math
import pygame

from constants import (
    WAVE_SPEED,
    WAVE_MAX_RADIUS,
    WAVE_THICKNESS,
    COLORS,
)


class SoundWave:
    """
    Круговая звуковая волна.
        x, y         — центр волны
        radius       — текущий радиус
        active       — волна ещё расширяется (True) или уже мертва (False)
        dead_frames  — сколько кадров волна уже неактивна (нужно, чтобы дать время затуханию завершиться)
    """

    def __init__(self, x, y, fade_speed):
        self.x = x
        self.y = y
        self.radius = 0.0
        self.active = True
        self.dead_frames = 0
        self.fade_speed = fade_speed #лаб 2 скорость из файла json. заменила этой переменной ALPHA_DECAY из модуля констант

    def update(self, walls, enemies):
        """
        Обновляет состояние волны:
            1. Пока волна активна — расширяется и подсвечивает объекты.
            2. Затухание яркости выполняется ВСЕГДА (даже после смерти волны).
            3. Счётчик dead_frames растёт после деактивации.

        Параметры:
            walls   — список [rect, alpha]
            enemies — список объектов Enemy (у каждого есть .rect и .alpha)
        """
        if self.active: # расширяется только пока жива
            self.radius += WAVE_SPEED
            if self.radius >= WAVE_MAX_RADIUS: # ограничение расширения в виде максимального радиуса
                self.active = False
            else:
                for w in walls:
                    dist = self._distance_to_rect(w[0])
                    if self.radius - WAVE_THICKNESS <= dist <= self.radius + WAVE_THICKNESS:#R +-5
                        w[1] = 255

                for enemy in enemies:
                    dist = math.hypot( # теорема пифагора. Расстояние от игрока (центра звуковой волны) до врага
                        self.x - enemy.rect.centerx,
                        self.y - enemy.rect.centery,
                    )
                    if self.radius - WAVE_THICKNESS <= dist <= self.radius + WAVE_THICKNESS:
                        enemy.alpha = 255

        # постоянное затухание, чтобы после смерти волны стены и враги не продолжали подсвечиваться
        for w in walls:
            w[1] = max(0, w[1] - self.fade_speed) #max чтобы не было отрицательных значений
        for enemy in enemies:
            enemy.alpha = max(0, enemy.alpha - self.fade_speed)

        # когда волна перестала расширяться, начинаем считать. В game.py волна удалится, когда dead_frames >= 40.
        if not self.active:
            self.dead_frames += 1

    def _distance_to_rect(self, rect):
        """
        Минимальное расстояние от центра волны до прямоугольника.
        Нужно, чтобы корректно проверять попадание стены в кольцо волны.
        Координаты ближайшей точки прямоугольника к центу волны.
        """
        closest_x = max(rect.left, min(self.x, rect.right))
        closest_y = max(rect.top, min(self.y, rect.bottom))
        return math.hypot(self.x - closest_x, self.y - closest_y)

    def draw(self, surface):
        """
        Отрисовывает волну как полупрозрачный круг.
        Яркость убывает с ростом радиуса.
        """
        if not self.active:
            return
        alpha = max(0, 255 - int((self.radius / WAVE_MAX_RADIUS) * 255)) # чем больше радиус, тем прозрачнее круг
        if alpha <= 0:
            return
        diameter = int(self.radius * 2)
        if diameter <= 0:
            return
        wave_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        color = COLORS["wave"]
        pygame.draw.circle(
            wave_surf,
            (color[0], color[1], color[2], alpha),
            (int(self.radius), int(self.radius)),
            int(self.radius),
            2,
        )
        surface.blit(wave_surf, (int(self.x - self.radius), int(self.y - self.radius)))