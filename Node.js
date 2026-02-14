const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { 
    cors: { origin: "*" } 
});

let gameState = "wait";
let multiplier = 1.0;
let timer = 5;
let crashAt = 2.0;

function startRound() {
    gameState = "wait";
    timer = 5;
    multiplier = 1.0;
    // Логіка генерації крашу (рандомна)
    crashAt = (Math.random() < 0.1 ? 1.00 : (Math.random() < 0.7 ? (Math.random() * 1.5 + 1.1) : (Math.random() * 8 + 2))).toFixed(2);
    
    let waitInterval = setInterval(() => {
        timer--;
        io.emit('gameUpdate', { s: gameState, t: timer, m: multiplier });
        if (timer <= 0) {
            clearInterval(waitInterval);
            runFlight();
        }
    }, 1000);
}

function runFlight() {
    gameState = "fly";
    let start = Date.now();
    let flightInterval = setInterval(() => {
        multiplier = Math.pow(1.08, (Date.now() - start) / 1000);
        
        if (multiplier >= crashAt) {
            multiplier = parseFloat(crashAt);
            gameState = "crash";
            io.emit('gameUpdate', { s: gameState, m: multiplier });
            clearInterval(flightInterval);
            setTimeout(startRound, 4000); // Пауза між раундами
        } else {
            io.emit('gameUpdate', { s: gameState, m: multiplier });
        }
    }, 100);
}

startRound();
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
