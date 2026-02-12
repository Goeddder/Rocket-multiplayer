const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

let game = {
    phase: "wait", 
    timer: 6.0,
    curX: 1.0,
    crashX: 2.0,
    history: []
};

// Цикл гри
setInterval(() => {
    if (game.phase === "wait") {
        game.timer -= 0.1;
        if (game.timer <= 0) {
            game.phase = "fly";
            game.curX = 1.0;
            game.crashX = (Math.random() * 3.5) + 1.1; 
        }
    } else if (game.phase === "fly") {
        game.curX += 0.015; 
        if (game.curX >= game.crashX) {
            game.phase = "boom";
            game.history.unshift(game.crashX.toFixed(2));
            if(game.history.length > 10) game.history.pop();
            setTimeout(() => { game.phase = "wait"; game.timer = 6.0; }, 3000); 
        }
    }
    // Відправка всім гравцям
    io.emit("gameUpdate", {
        phase: game.phase,
        timer: game.timer.toFixed(1),
        currentX: game.curX.toFixed(2),
        online: io.engine.clientsCount,
        history: game.history
    });
}, 100);

io.on("connection", (socket) => {
    socket.on("placeBet", (data) => socket.broadcast.emit("newBet", data));
});

const PORT = process.env.PORT || 10000;
server.listen(PORT, () => console.log(`Server on port ${PORT}`));
