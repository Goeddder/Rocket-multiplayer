const http = require('http');
const server = http.createServer((req, res) => {
    res.writeHead(200);
    res.end("Server is running");
});

const io = require('socket.io')(server, {
    cors: { origin: "*" }
});

let game = {
    phase: "wait", 
    timer: 6.0,
    curX: 1.0,
    crashX: 2.0,
    history: []
};

// ГОЛОВНИЙ ЦИКЛ (Працює завжди)
setInterval(() => {
    if (game.phase === "wait") {
        game.timer -= 0.1;
        if (game.timer <= 0) {
            game.phase = "fly";
            game.curX = 1.0;
            game.crashX = (Math.random() * 3.5) + 1.1; 
            console.log("Раунд почався! Краш на:", game.crashX);
        }
    } else if (game.phase === "fly") {
        game.curX += 0.015; 
        if (game.curX >= game.crashX) {
            game.phase = "boom";
            game.history.unshift(game.crashX.toFixed(2));
            if(game.history.length > 12) game.history.pop();
            
            setTimeout(() => {
                game.phase = "wait";
                game.timer = 6.0;
            }, 3000); 
        }
    }

    // Відправка даних абсолютно всім кожні 100мс
    io.emit("gameUpdate", {
        phase: game.phase,
        timer: game.timer.toFixed(1),
        currentX: game.curX.toFixed(2),
        online: io.engine.clientsCount,
        history: game.history
    });
}, 100);

io.on("connection", (socket) => {
    console.log("Гравець зайшов, онлайн:", io.engine.clientsCount);
    socket.on("placeBet", (data) => {
        socket.broadcast.emit("newBet", data);
    });
});

const PORT = process.env.PORT || 10000;
server.listen(PORT, () => {
    console.log(`Сервер запущено на порту ${PORT}`);
});
