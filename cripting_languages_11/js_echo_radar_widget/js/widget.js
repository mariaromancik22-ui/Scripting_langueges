import { Player } from '../../js_echo_radar/js/player.js';
import { SoundWave } from '../../js_echo_radar/js/wave.js';
import { buildWalls } from '../../js_echo_radar/js/level.js';
import { Enemy } from '../../js_echo_radar/js/enemy.js';
import { WAVE_MAX_RADIUS } from '../../js_echo_radar/js/constants.js';
import { createScenarios } from './scenarios.js';

const canvas = document.querySelector('#game');
const ctx = canvas.getContext('2d');
canvas.focus();

const testMatrix = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1]
];

const walls = buildWalls(testMatrix);

const enemyPositions = [[360, 200], [600, 440], [240, 440], [680, 120]];
const enemies = enemyPositions.map(([x, y]) => new Enemy(x, y));


const game = {
    player: new Player(60, 60),
    waves: [],
    enemies: enemies,
    shotsFired: 0,
    gameOver: false,
    win: false,
    finalTime: 0,
    startTime: performance.now(),
    paused: false,
    SoundWave,
    Player
};

const scenarios = createScenarios(game);
window.Game = { game, scenarios };

const keys = {};

window.addEventListener('keydown', (e) => {
    keys[e.code] = true;

    if (e.code === 'Space' && !e.repeat && !game.gameOver) {
        game.waves.push(new SoundWave(game.player.rect.centerx, game.player.rect.centery));
        game.shotsFired++;
    }

    if (e.code === 'KeyR') {
        scenarios.restart();
        for (const wall of walls) wall[1] = 0;
        for (const enemy of game.enemies) enemy.alpha = 0;
    }
});

window.addEventListener('keyup', (e) => {
    keys[e.code] = false;
});

canvas.addEventListener('click', (e) => {
    if (game.gameOver) return;
    game.waves.push(new SoundWave(game.player.rect.centerx, game.player.rect.centery));
    game.shotsFired++;
});

const spawnBtn = document.querySelector('[data-scenario="spawnWave"]');
if (spawnBtn) {
    spawnBtn.addEventListener('click', () => {
        if (!game.gameOver) scenarios.spawnWave();
    });
}

let lastTime = performance.now();
let accumulator = 0;
const FRAME_MS = 1000 / 60;
function step() {
    if (game.gameOver) return;

    let dx = 0, dy = 0;
    if (keys['KeyW'] || keys['ArrowUp']) dy = -1;
    else if (keys['KeyS'] || keys['ArrowDown']) dy = 1;
    else if (keys['KeyA'] || keys['ArrowLeft']) dx = -1;
    else if (keys['KeyD'] || keys['ArrowRight']) dx = 1;

    if (dx !== 0 || dy !== 0) {
        game.player.move(dx, dy, walls);
    }

    for (const wave of game.waves) {
        wave.update(walls, game.enemies);
    }

    for (let i = game.waves.length - 1; i >= 0; i--) {
        if (!game.waves[i].active && game.waves[i].deadFrames >= 40) {
            game.waves.splice(i, 1);
        }
    }

    for (const enemy of game.enemies) {
        if (game.player.rect.colliderect(enemy.rect)) {
            game.gameOver = true;
            game.win = false;
            game.finalTime = (performance.now() - game.startTime) / 1000;
            return;
        }
    }

    if (game.player.rect.x < 0 || game.player.rect.x + game.player.rect.w > canvas.width ||
        game.player.rect.y < 0 || game.player.rect.y + game.player.rect.h > canvas.height) {
        game.gameOver = true;
        game.win = true;
        game.finalTime = (performance.now() - game.startTime) / 1000;
    }
}
function render() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (const [rect, alpha] of walls) {
        if (alpha <= 0) continue;
        ctx.fillStyle = `rgba(0, 255, 0, ${alpha / 255})`;
        ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
    }

    for (const enemy of game.enemies) {
        if (enemy.alpha > 0) {
            // враг
            ctx.fillStyle = `rgba(255, 60, 60, ${enemy.alpha / 255})`;
            ctx.fillRect(enemy.rect.x, enemy.rect.y, enemy.rect.w, enemy.rect.h);

            // индикатор над врагом (жёлтая мигающая точка)
            if (enemy.alpha > 150) {
                ctx.fillStyle = '#ffff00';
                ctx.beginPath();
                ctx.arc(enemy.rect.centerx, enemy.rect.y - 8, 4, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    // игрок
    ctx.fillStyle = '#000';
    //ctx.fillStyle = '#288CFF';
    ctx.fillRect(game.player.rect.x, game.player.rect.y, game.player.rect.w, game.player.rect.h);

    // волны
    ctx.lineWidth = 2;
    for (const wave of game.waves) {
        if (!wave.active) continue;
        const alpha = 1 - (wave.radius / WAVE_MAX_RADIUS);
        ctx.strokeStyle = `rgba(0, 255, 180, ${alpha})`;
        ctx.beginPath();
        ctx.arc(wave.x, wave.y, wave.radius, 0, Math.PI * 2);
        ctx.stroke();
    }

    // ЭКРАН РЕЗУЛЬТАТА
    if (game.gameOver) {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        if (game.win) {
            ctx.fillStyle = '#00ff88';
            ctx.font = 'bold 48px Arial';
            ctx.fillText('ВЫ ВЫБРАЛИСЬ!', canvas.width / 2, canvas.height / 2 - 80);
        } else {
            ctx.fillStyle = '#ff4444';
            ctx.font = 'bold 48px Arial';
            ctx.fillText('ВАС ОБНАРУЖИЛИ!', canvas.width / 2, canvas.height / 2 - 80);
        }

        ctx.fillStyle = '#ffffff';
        ctx.font = '24px Arial';
        ctx.fillText(`Время: ${game.finalTime.toFixed(1)} сек.`, canvas.width / 2, canvas.height / 2);
        ctx.fillText(`Импульсов: ${game.shotsFired}`, canvas.width / 2, canvas.height / 2 + 40);

        ctx.fillStyle = '#aaaaaa';
        ctx.font = '20px Arial';
        ctx.fillText('Нажмите R для рестарта', canvas.width / 2, canvas.height / 2 + 100);

        ctx.textAlign = 'left';
        ctx.textBaseline = 'alphabetic';
    }

    // HUD
    if (!game.gameOver) {
        const elapsed = ((performance.now() - game.startTime) / 1000).toFixed(1);
        document.querySelector('#time').textContent = elapsed;
    } 

    else {
        document.querySelector('#time').textContent = game.finalTime.toFixed(1);
    }
    document.querySelector('#wave-count').textContent = game.waves.length;
    document.querySelector('#shots').textContent = game.shotsFired;
}

// ЦИКЛ
function loop(now) {
    let deltaMs = now - lastTime;
    lastTime = now;
    if (deltaMs > 100) deltaMs = 100;
    accumulator += deltaMs;
    while (accumulator >= FRAME_MS) {
        step();
        accumulator -= FRAME_MS;
    }
    render();
    requestAnimationFrame(loop);
}

requestAnimationFrame(loop);