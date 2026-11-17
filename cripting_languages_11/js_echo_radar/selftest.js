import { distance } from './js/math.js';
import { Rect } from './js/rect.js';
import { SoundWave } from './js/wave.js';
import { Player } from './js/player.js';
import { Enemy } from './js/enemy.js';
import { buildWalls, loadMapFromJSON } from './js/level.js';
import { WAVE_SPEED, WAVE_MAX_RADIUS, MAX_ALPHA, TILE_SIZE } from './js/constants.js';

let passed = 0;
let failed = 0;


// вспомогательная функция для проверок
function check(name, actual, expected) {
    const ok = actual === expected;
    if (ok) {
        console.log(`[OK] ${name}`);
        passed++;
    } else {
        console.log(`[ERROR] ${name} — ожидалось ${expected}, получено ${actual}`);
        failed++;
    }
}

function checkApprox(name, actual, expected, epsilon = 0.001) {
    const ok = Math.abs(actual - expected) < epsilon;
    if (ok) {
        console.log(`[OK] ${name}`);
        passed++;
    } else {
        console.log(`[ERROR] ${name} — ожидалось ~${expected}, получено ${actual}`);
        failed++;
    }
}

// МАТЕМАТИКА (расстояния)
console.log("Математика");
check("Расстояние (0,0)-(3,4) = 5", distance(0, 0, 3, 4), 5);
check("Расстояние между одинаковыми точками = 0", distance(10, 10, 10, 10), 0);
checkApprox("Расстояние (0,0)-(1,1) ≈ 1.414", distance(0, 0, 1, 1), Math.SQRT2);

// КЛАСС RECT (геометрия)
console.log("\nКласс Rect");
const r1 = new Rect(0, 0, 10, 10);
check("Rect.left = 0", r1.left, 0);
check("Rect.right = 10", r1.right, 10);
check("Rect.centerx = 5", r1.centerx, 5);

const r2 = new Rect(5, 5, 10, 10);
check("Пересечение Rect (0,0,10,10) и (5,5,10,10) = true", r1.colliderect(r2), true);

const r3 = new Rect(20, 20, 10, 10);
check("Пересечение Rect (0,0,10,10) и (20,20,10,10) = false", r1.colliderect(r3), false);

check("Точка (5,5) внутри Rect (0,0,10,10) = true", r1.collidepoint(5, 5), true);
check("Точка (15,15) внутри Rect (0,0,10,10) = false", r1.collidepoint(15, 15), false);

const rMoved = r1.move(5, 0);
check("Rect.move(5,0) возвращает новый объект", rMoved !== r1, true);
check("После move оригинал не изменился (x=0)", r1.x, 0);
check("После move новый x=5", rMoved.x, 5);

// ВОЛНА
console.log("\nSoundWave");
const wave = new SoundWave(0, 0);

check("Волна создаётся с радиусом 0", wave.radius, 0);
check("Волна активна при создании", wave.active, true);

wave.update([], []);
check(`После update радиус = ${WAVE_SPEED}`, wave.radius, WAVE_SPEED);

// прогоняем волну до деактивации, чтобы проверить жизненный цикл
let steps = 0;
while (wave.active && steps < 1000) {
    wave.update([], []); // без стен и врагов, чтобы быстрее
    steps++;
}
check("Волна деактивируется при достижении максимума", wave.active, false);
check("Радиус при деактивации >= WAVE_MAX_RADIUS", wave.radius >= WAVE_MAX_RADIUS, true);

// проверка затухания
const walls2 = [[new Rect(0, 0, 10, 10), MAX_ALPHA]];
const wave2 = new SoundWave(0, 0);
wave2.update(walls2, []);
check("Затухание уменьшает яркость стены", walls2[0][1] < MAX_ALPHA, true);

// проверка счётчика deadFrames
const wave3 = new SoundWave(0, 0);
wave3.active = false; // принудительно
wave3.update([], []);
check("deadFrames растёт после деактивации", wave3.deadFrames, 1);

// ИГРОК И СТЕНЫ (коллизии)
console.log("\nPlayer и коллизии");
const wallForPlayer = [[new Rect(10, 0, 10, 10), 0]];
const player = new Player(0, 0);

check("Player.move(1,0) в пустоте возвращает true", player.move(1, 0, []), true);
check("Player.move(1,0) в стену возвращает false", player.move(1, 0, wallForPlayer), false);

// УРОВЕНЬ И ВАЛИДАЦИЯ
console.log("\nУровень и JSON");
const matrix = [
    [1, 0],
    [0, 1]
];
const builtWalls = buildWalls(matrix);
check("buildWalls из матрицы 2x2 создаёт 2 стены", builtWalls.length, 2);
check("Первая стена имеет размер TILE_SIZE", builtWalls[0][0].w, TILE_SIZE);

const goodJson = '{"level": [[1, 0], [0, 1]], "fade_speed": 5}';
const loaded = loadMapFromJSON(goodJson);
check("loadMapFromJSON возвращает level", loaded.level.length, 2);
check("loadMapFromJSON возвращает fadeSpeed", loaded.fadeSpeed, 5);

// проверка ошибок валидации
try {
    loadMapFromJSON('{"level": "not an array"}');
    check("loadMapFromJSON с плохим level выбрасывает ошибку", false, true);
} catch (e) {
    check("loadMapFromJSON с плохим level выбрасывает ошибку", true, true);
}

try {
    loadMapFromJSON('не json');
    check("loadMapFromJSON с битым JSON выбрасывает ошибку", false, true);
} catch (e) {
    check("loadMapFromJSON с битым JSON выбрасывает ошибку", true, true);
}

// ИТОГИ
console.log(`\nИТОГ: ${passed} пройдено, ${failed} провалено`);
if (failed > 0) {
    process.exit(1);
}