import pygame
from constants import PLAYER_SIZE, PLAYER_SPEED, COLORS

class Player:

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE) #прямоугольник для работы с колллихиями
        self.speed = PLAYER_SPEED

    def move(self, dx, dy, walls):
        new_rect = self.rect.move(dx * self.speed, dy * self.speed)# пробный прямоугольник, чтобы избежать проникновения в стены игроком
        for wall_rect, _ in walls:
            if new_rect.colliderect(wall_rect):# проверяет пересечение со стеной
                return False # не двигаемся если столкнулись
        self.rect = new_rect # если не сталкиваемся, присваем пробный и двигаемся
        return True

  