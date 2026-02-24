import fetch from 'node-fetch';

export default async function handler(req, res) {
    const { username } = req.query;
    const BOT_TOKEN = '8617323759:AAGtVEQ16R8lHU9x8jZ4I5MDiEvc6d1HZGE';

    if (!username) return res.status(400).json({ ok: false });

    try {
        const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getChat?chat_id=@${username.replace('@', '')}`);
        const data = await response.json();

        if (data.ok) {
            res.status(200).json({
                ok: true,
                name: data.result.first_name || username,
                photo: `https://t.me/i/userpic/320/${username.replace('@', '')}.jpg`
            });
        } else {
            res.status(404).json({ ok: false });
        }
    } catch (e) {
        res.status(500).json({ ok: false, error: e.message });
    }
}
