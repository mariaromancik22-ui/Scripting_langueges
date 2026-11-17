export function createScenarios(game) {
    return {
        //выпустить волну в указанной точке (по умолчанию у игрока)
        spawnWave(x, y) {
            const wx = x ?? game.player.rect.centerx;
            const wy = y ?? game.player.rect.centery;
            game.waves.push(new game.SoundWave(wx, wy));
            game.shotsFired++;
        },

        teleportPlayer(x, y) {
            game.player.rect.x = x;
            game.player.rect.y = y;
        },

        restart() {
            game.player = new game.Player(60, 60);
            game.waves = [];
            game.shotsFired = 0;
            game.gameOver = false;
            game.win = false;
            game.finalTime = 0;
            game.startTime = performance.now();
            game.paused = false;
        }
    };
}