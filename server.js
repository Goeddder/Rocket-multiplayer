const http = require('http');
const server = http.createServer();
const io = require('socket.io')(server, {
    cors: { origin: "*" }
});

let game = {
    phase: "wait", 
    timer: 6.0,
    curX: 1.0,
    crashX: 0,
    online: 0
};

// Ігровий цикл: працює кожні 100мс
setInterval(() => {
    if (game.phase === "wait") {
        game.timer -= 0.1;
        if (game.timer <= 0) {
            game.phase = "fly";
            game.curX = 1.0;
            game.crashX = (Math.random() * 3.5) + 1.1; 
        }
    } else if (game.phase === "fly") {
        game.curX += 0.012; 
        if (game.curX >= game.crashX) {
            game.phase = "boom";
            setTimeout(() => {
                game.phase = "wait";
                game.timer = 6.0;
            }, 3000); 
        }
    }

    // Відправка даних усім клієнтам
    io.emit("gameUpdate", {
        phase: game.phase,
        timer: game.timer.toFixed(1),
        currentX: game.curX.toFixed(2),
        online: io.engine.clientsCount
    });
}, 100);

io.on("connection", (socket) => {
    socket.on("placeBet", (data) => {
        io.emit("newBet", data); // Трансляція ставки іншим
    });
});

const PORT = process.env.PORT || 10000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
