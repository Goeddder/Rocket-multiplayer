import fetch from 'node-fetch';

export default async function handler(req, res) {
    let { username } = req.query;
    const BOT_TOKEN = '8617323759:AAGtVEQ16R8lHU9x8jZ4I5MDiEvc6d1HZGE';

    if (!username) return res.status(400).json({ ok: false });

    // Очищаем ник от @ и пробелов
    username = username.replace('@', '').trim();

    try {
        // Мы используем getChat, но добавляем проверку типа
        const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getChat?chat_id=@${username}`);
        const data = await response.json();

        if (data.ok && data.result.type === 'private') {
            res.status(200).json({
                ok: true,
                name: data.result.first_name + (data.result.last_name ? ' ' + data.result.last_name : ''),
                photo: `https://t.me/i/userpic/320/${username}.jpg`,
                id: data.result.id
            });
        } else {
            // Если это канал или группа, или пользователь не найден
            res.status(404).json({ ok: false, error: "Пользователь не найден" });
        }
    } catch (e) {
        res.status(500).json({ ok: false });
    }
}
