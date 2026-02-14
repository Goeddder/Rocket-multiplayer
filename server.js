const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

let gameState = "wait";
let multiplier = 1.00;
let timer = 10;
let crashAt = 0;
let allBets = []; // Масив для всіх ставок

function startNewRound() {
    gameState = "wait";
    multiplier = 1.00;
    timer = 10;
    allBets = []; // Очищаємо список ставок для нового раунду
    crashAt = (Math.random() * 5 + 1.1).toFixed(2); // Рандомний вибух

    const waitInterval = setInterval(() => {
        timer--;
        io.emit('gameUpdate', { s: gameState, m: multiplier, t: timer, bets: allBets });
        if (timer <= 0) {
            clearInterval(waitInterval);
            startFlight();
        }
    }, 1000);
}

function startFlight() {
    gameState = "fly";
    let start = Date.now();
    const flyInterval = setInterval(() => {
        const elapsed = (Date.now() - start) / 1000;
        multiplier = Math.pow(1.08, elapsed);
        if (multiplier >= crashAt) {
            multiplier = parseFloat(crashAt);
            gameState = "crash";
            io.emit('gameUpdate', { s: gameState, m: multiplier, bets: allBets });
            clearInterval(flyInterval);
            setTimeout(startNewRound, 4000);
        } else {
            io.emit('gameUpdate', { s: gameState, m: multiplier, bets: allBets });
        }
    }, 100);
}

io.on('connection', (socket) => {
    socket.on('placeBet', (data) => {
        if (gameState === "wait") {
            allBets.push(data); // Додаємо ставку в загальний список
            io.emit('updateBets', allBets);
        }
    });
});

server.listen(process.env.PORT || 3000, () => startNewRound());
