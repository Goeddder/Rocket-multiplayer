const http = require('http');
const server = http.createServer();
const io = require('socket.io')(server, {
    cors: { origin: "*" }
});

let game = {
    phase: "wait", // wait, fly, boom
    timer: 6.0,
    curX: 1.0,
    crashX: 0,
    history: []
};

// Головний ігровий цикл (10 разів на секунду)
setInterval(() => {
    if (game.phase === "wait") {
        game.timer -= 0.1;
        if (game.timer <= 0) {
            game.phase = "fly";
            game.curX = 1.0;
            game.crashX = (Math.random() * 3.4) + 1.1; // Випадковий краш
        }
    } else if (game.phase === "fly") {
        game.curX += 0.012; // Швидкість росту ікса
        if (game.curX >= game.crashX) {
            game.phase = "boom";
            game.history.unshift(game.curX.toFixed(2));
            if(game.history.length > 10) game.history.pop();
            
            setTimeout(() => {
                game.phase = "wait";
                game.timer = 6.0;
            }, 3000); // Пауза після вибуху
        }
    }

    // Надсилаємо дані всім підключеним гравцям
    io.emit("gameUpdate", {
        phase: game.phase,
        timer: game.timer.toFixed(1),
        currentX: game.curX.toFixed(2),
        online: io.engine.clientsCount,
        history: game.history
    });
}, 100);

io.on("connection", (socket) => {
    console.log("Новий гравець підключився");
    
    socket.on("placeBet", (data) => {
        // Розсилаємо всім повідомлення про нову ставку
        io.emit("newBet", data);
    });
});

const PORT = process.env.PORT || 10000;
server.listen(PORT, () => {
    console.log(`Сервер працює на порту ${PORT}`);
});
