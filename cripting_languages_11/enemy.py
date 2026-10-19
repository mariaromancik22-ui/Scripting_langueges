import pygame
from constants import ENEMY_SIZE, COLORS

class Enemy:
    def __init__(self, x, y): #конструктор, который вызывается при создании объекта
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.alpha = 0

    def draw(self, surface):
        if self.alpha <= 0:
            return
        enemy_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        color = COLORS["enemy"]
        pygame.draw.rect(
            enemy_surf,
            (color[0], color[1], color[2], self.alpha),
            (0, 0, self.rect.width, self.rect.height),
            2,
        )
        surface.blit(enemy_surf, (self.rect.x, self.rect.y))