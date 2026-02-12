const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { 
    cors: { origin: "*" } 
});

// Роздаємо статичні файли (наш index.html)
app.use(express.static(__dirname));

let activeBets = [];

io.on('connection', (socket) => {
    console.log('Новий гравець підключився');

    // Відправляємо список ставок новому гравцю
    socket.emit('update_bets', activeBets);

    // Коли хтось робить ставку
    socket.on('place_bet', (betData) => {
        activeBets.push(betData);
        // Розсилаємо всім реальним гравцям нову ставку
        io.emit('update_bets', activeBets);
    });

    // Очищення ставок при новому раунді
    socket.on('clear_round', () => {
        activeBets = [];
        io.emit('update_bets', activeBets);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Сервер працює на порту ${PORT}`);
});
