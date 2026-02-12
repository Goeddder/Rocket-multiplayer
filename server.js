const express = require('express');
const http = require('http');
const path = require('path');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, { cors: { origin: "*" } });

// --- ЛОГІКА ГРИ (СЕРВЕР) ---
let game = {
    phase: "wait", 
    timer: 6.0,
    curX: 1.0,
    crashX: 2.0,
    history: [],
    online: 0
};

setInterval(() => {
    if (game.phase === "wait") {
        game.timer -= 0.1;
        if (game.timer <= 0) {
            game.phase = "fly";
            game.curX = 1.0;
            game.crashX = (Math.random() * 3.8) + 1.1; 
        }
    } else if (game.phase === "fly") {
        game.curX += 0.015; 
        if (game.curX >= game.crashX) {
            game.phase = "boom";
            game.history.unshift(game.crashX.toFixed(2));
            if(game.history.length > 10) game.history.pop();
            
            setTimeout(() => {
                game.phase = "wait";
                game.timer = 6.0;
            }, 3000); 
        }
    }
    io.emit("gameUpdate", {
        phase: game.phase,
        timer: game.timer.toFixed(1),
        currentX: game.curX.toFixed(2),
        online: io.engine.clientsCount,
        history: game.history
    });
}, 100);

io.on("connection", (socket) => {
    socket.on("placeBet", (data) => {
        socket.broadcast.emit("newBet", data);
    });
});

// --- ВІДОБРАЖЕННЯ ГРИ (ФРОНТЕНД) ---
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Rocket Ultra</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        :root { --blue: #007aff; --green: #34c759; --red: #ff3b30; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { background: #000; color: #fff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; overflow: hidden; height: 100vh; }
        .bg-video { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.3; z-index: 0; pointer-events: none; }
        
        .screen { display: none; height: calc(100vh - 65px); width: 100%; position: relative; z-index: 1; }
        .screen.active { display: flex; flex-direction: column; }
        #game-screen { height: 100vh; position: fixed; top: 0; left: 0; z-index: 200; background: #000; display: none; }
