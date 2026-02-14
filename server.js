const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

let gameState = "wait"; // wait, fly, crash
let multiplier = 1.00;
let timer = 10;
let currentBets = [];
let history = [];

function gameLoop() {
    if (gameState === "wait") {
        timer -= 0.1;
        if (timer <= 0) {
            gameState = "fly";
            multiplier = 1.00;
        }
    } else if (gameState === "fly") {
        multiplier += 0.01 * (multiplier / 2); // Ракета прискорюється
        
        // Шанс крашу (випадковий)
        if (Math.random() < 0.005 * (multiplier / 5)) {
            gameState = "crash";
            history.push(multiplier.toFixed(2));
            timer = 5; // Пауза після крашу
        }
    } else if (gameState === "crash") {
        timer -= 0.1;
        if (timer <= 0) {
            gameState = "wait";
            timer = 10;
            currentBets = []; // Очищаємо ставки для нового раунду
        }
    }
    
    io.emit('gameUpdate', {
        s: gameState,
        m: multiplier,
        t: Math.ceil(timer),
        bets: currentBets,
        h: history.slice(-10)
    });
}

setInterval(gameLoop, 100);

io.on('connection', (socket) => {
    // Коли гравець ставить
    socket.on('placeBet', (data) => {
        if (gameState === "wait") {
            currentBets.push({
                nick: data.nick,
                ava: data.ava,
                amount: data.amount,
                cashedOut: false,
                winX: 0
            });
        }
    });

    // КОЛИ ГРАВЕЦЬ НАДИСКАЄ "ЗАБРАТИ"
    socket.on('cashOut', (data) => {
        let bet = currentBets.find(b => b.nick === data.nick && !b.cashedOut);
        if (bet && gameState === "fly") {
            bet.cashedOut = true;
            bet.winX = data.winX; // Фіксуємо ікс виграшу на сервері
            console.log(`${data.nick} забрав на ${data.winX}x`);
        }
    });
});

server.listen(process.env.PORT || 3000, () => {
    console.log('Server running...');
});
