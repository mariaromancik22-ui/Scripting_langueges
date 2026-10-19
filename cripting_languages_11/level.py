import pygame
from constants import TILE_SIZE, COLORS


def build_walls(level_matrix): # добавили аргумент
    walls = []
    rows = len(level_matrix)       # вычисляем строки из матрицы
    cols = len(level_matrix[0])    #вычисляем колонки из матрицы
    
    for gy in range(rows):
        for gx in range(cols):
            if level_matrix[gy][gx] == 1: # если стена
                rect = pygame.Rect(
                    gx * TILE_SIZE,
                    gy * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                walls.append([rect, 0])
    return walls


def draw_walls(surface, walls):
    for rect, alpha in walls:
        if alpha <= 0: #если стена невидимая, то не отрисовывает
            continue
        
        wall_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        color = COLORS["wall"]
        
        pygame.draw.rect(
            wall_surf,
            (color[0], color[1], color[2], alpha),
            (0, 0, rect.width, rect.height),
            2,
        )
        surface.blit(wall_surf, (rect.x, rect.y))





















"""
import pygame
from constants import (
    LEVEL_MATRIX,
    GRID_ROWS,
    GRID_COLUMNS,
    TILE_SIZE,
    COLORS,
)


def build_walls():
    walls = []
    for gy in range(GRID_ROWS):
        for gx in range(GRID_COLUMNS):
            if LEVEL_MATRIX[gy][gx] == 1: # если стена
                rect = pygame.Rect( # класс для работы с прямоугольниками, хранит координаты и размеры
                    gx * TILE_SIZE,# координата верхнего левого угла
                    gy * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                walls.append([rect, 0]) # добавляет стену в список. координаты и размер стены, яркость (невидимая)
    return walls


def draw_walls(surface, walls):

    Отрисовывает контуры стен с текущей яркостью.
    Использует полупрозрачную поверхность для alpha-канала.

    for rect, alpha in walls:
        if alpha <= 0: #если стена невидимая, то не отрисовывает
            continue
        # создаётся виртуальный холст. не на экране, потому что нужна прозрачность
        wall_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)# размер поверхности и флаг который включает поддержку alpha-канала
        color = COLORS["wall"]
        pygame.draw.rect(
            wall_surf, # поверхность
            (color[0], color[1], color[2], alpha), #RGB и прозрачность
            (0, 0, rect.width, rect.height),# где рисовать
            2,# толщина контура
        )
        surface.blit(wall_surf, (rect.x, rect.y)) #налаживание холста на экран
        """
