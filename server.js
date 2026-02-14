const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

let gameState = "wait"; // wait, fly, crash
let multiplier = 1.00;
let timer = 10; // час до старту
let crashAt = 0;

function startNewRound() {
    gameState = "wait";
    multiplier = 1.00;
    timer = 10;
    
    // Генерація моменту вибуху (чесний алгоритм)
    const random = Math.random();
    if (random < 0.05) crashAt = 1.00; // 5% шанс миттєвого вибуху
    else crashAt = (100 / (Math.floor(Math.random() * 100) + 1)).toFixed(2);
    
    // Якщо ікс занадто великий, трохи обмежуємо для стабільності
    if (crashAt > 50) crashAt = (Math.random() * 10 + 5).toFixed(2);

    console.log(`Новий раунд! Вибухне на: ${crashAt}x`);

    const waitInterval = setInterval(() => {
        timer--;
        broadcast();
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
        multiplier = Math.pow(1.08, elapsed); // Формула росту ікса

        if (multiplier >= crashAt) {
            multiplier = parseFloat(crashAt);
            gameState = "crash";
            broadcast();
            clearInterval(flyInterval);
            
            // Пауза після крашу і новий раунд
            setTimeout(startNewRound, 4000);
        } else {
            broadcast();
        }
    }, 100);
}

function broadcast() {
    io.emit('gameUpdate', {
        s: gameState,
        m: multiplier,
        t: timer
    });
}

io.on('connection', (socket) => {
    console.log('Гравець підключився');
    socket.emit('gameUpdate', { s: gameState, m: multiplier, t: timer });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Сервер працює на порту ${PORT}`);
    startNewRound();
});
