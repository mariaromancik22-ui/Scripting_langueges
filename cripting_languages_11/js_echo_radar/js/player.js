import { Rect } from './rect.js';
import { PLAYER_SIZE, PLAYER_SPEED } from './constants.js';
export class Player {
    constructor(x, y) {
        this.rect = new Rect(x, y, PLAYER_SIZE, PLAYER_SIZE);
        this.speed = PLAYER_SPEED;
    }

    move(dx, dy, walls) {
        const newRect = this.rect.move(dx * this.speed, dy * this.speed);

        // проверяет пересечение со всеми стенами
        for (const wall of walls) {
            const wallRect = wall[0]; // в массиве стены первый элемент - это прямоугльник
            if (newRect.colliderect(wallRect)) {
                return false; // упёрлись в стену - не двигаемся
            }
        }
        // если столкновений нет — подтверждает движение
        this.rect = newRect;
        return true;
    }
}