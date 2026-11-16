import { Rect } from './rect.js';
import { ENEMY_SIZE, MIN_ALPHA } from './constants.js';
export class Enemy {
    constructor(x, y) {
        this.rect = new Rect(x, y, ENEMY_SIZE, ENEMY_SIZE);
        this.alpha = MIN_ALPHA;
    }
}