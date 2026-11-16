import { distance } from './math.js';
import {
    WAVE_SPEED,
    WAVE_MAX_RADIUS,
    WAVE_THICKNESS,
    MAX_ALPHA,
    MIN_ALPHA,
    DEFAULT_FADE_SPEED
} from './constants.js';
export class SoundWave {
   
    // x и y - координаты центра волны
    //fadeSpeed - шаг затухания яркости (по умолчанию из констант)
    constructor(x, y, fadeSpeed = DEFAULT_FADE_SPEED) {
        this.x = x;
        this.y = y;
        this.radius = 0.0;
        this.active = true;
        this.deadFrames = 0;
        this.fadeSpeed = fadeSpeed;
    }

    /*
    Обновляет состояние волны:
            1. Пока волна активна — расширяется и подсвечивает объекты.
            2. Затухание яркости выполняется ВСЕГДА (даже после смерти волны).
            3. Счётчик dead_frames растёт после деактивации.

        Параметры:
            walls   — список [rect, alpha]
            enemies — список объектов Enemy (у каждого есть .rect и .alpha)
     */
    update(walls, enemies) {
        // расширение и подсветка (только пока волна жива)
        if (this.active) {
            this.radius += WAVE_SPEED;
            if (this.radius >= WAVE_MAX_RADIUS) {
                this.active = false;
            } else {
                // подсветка стен
                for (const w of walls) {
                    const dist = this._distanceToRect(w[0]);
                    // R+-5
                    if (this.radius - WAVE_THICKNESS <= dist && dist <= this.radius + WAVE_THICKNESS) {
                        w[1] = MAX_ALPHA;
                    }
                }

                // подсветка врагов
                for (const enemy of enemies) {
                    const dist = distance(
                        this.x, this.y,
                        enemy.rect.centerx, enemy.rect.centery
                    );
                    if (this.radius - WAVE_THICKNESS <= dist && dist <= this.radius + WAVE_THICKNESS) {
                        enemy.alpha = MAX_ALPHA;
                    }
                }
            }
        }

        // постоянное затухание
        for (const w of walls) {
            w[1] = Math.max(MIN_ALPHA, w[1] - this.fadeSpeed);
        }
        for (const enemy of enemies) {
            enemy.alpha = Math.max(MIN_ALPHA, enemy.alpha - this.fadeSpeed);
        }

        // счётчик кадров после деактивации
        if (!this.active) {
            this.deadFrames += 1;
        }
    }

    /*
        Минимальное расстояние от центра волны до прямоугольника.
        Нужно, чтобы корректно проверять попадание стены в кольцо волны.
        Координаты ближайшей точки прямоугольника к центу волны.
     */
    _distanceToRect(rect) {
        // Находим ближайшую к центру волны точку прямоугольника
        const closestX = Math.max(rect.left, Math.min(this.x, rect.right));
        const closestY = Math.max(rect.top, Math.min(this.y, rect.bottom));

        return distance(this.x, this.y, closestX, closestY);
    }
}