import { Rect } from './rect.js';
import { TILE_SIZE } from './constants.js';

export function buildWalls(matrix) {
    const walls = [];
    const rows = matrix.length;
    const cols = matrix[0].length;

    for (let gy = 0; gy < rows; gy++) {
        for (let gx = 0; gx < cols; gx++) {
            if (matrix[gy][gx] === 1) { // если стена
                const rect = new Rect(
                    gx * TILE_SIZE,
                    gy * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                );
                walls.push([rect, 0]);
            }
        }
    }
    return walls;
}
export function loadMapFromJSON(text) {
    let data;
    try {
        data = JSON.parse(text);
    } catch (e) {
        throw new Error(`Ошибка парсинга JSON: ${e.message}`);
    }

    if (!data.level || !Array.isArray(data.level)) {
        throw new Error("В JSON отсутствует поле 'level' или оно не является массивом");
    }
    if (data.level.length === 0 || !Array.isArray(data.level[0])) {
        throw new Error("Поле 'level' должно быть двумерным массивом (матрицей)");
    }

    return {
        level: data.level,
        fadeSpeed: data.fade_speed ?? 8 // если нет fade_speed, берём 8 по умолчанию
    };
}