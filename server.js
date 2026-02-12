const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

app.use(express.static(__dirname));

let activeBets = [];
let onlineCount = 0;

io.on('connection', (socket) => {
    onlineCount++;
    io.emit('update_online', onlineCount);
    socket.emit('update_bets', activeBets);

    socket.on('place_bet', (betData) => {
        activeBets.push(betData);
        io.emit('update_bets', activeBets);
    });

    // Нова функція: сервер очищає список для всіх
    socket.on('reset_all_bets', () => {
        activeBets = [];
        io.emit('update_bets', activeBets);
    });

    socket.on('disconnect', () => {
        onlineCount--;
        io.emit('update_online', onlineCount);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server live on ${PORT}`));
