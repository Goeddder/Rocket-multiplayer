const fetch = require('node-fetch');

export default async function handler(req, res) {
    // Важно: CryptoBot присылает данные в теле POST запроса
    if (req.method !== 'POST') return res.status(200).send('OK');

    const body = req.body;
    
    // !!! ЗАМЕНИ ЭТИ ЦИФРЫ НА СВОЙ ID ИЗ @userinfobot !!!
    const MY_ID = '1471307057'; 
    const BOT_TOKEN = '8617323759:AAGtVEQ16R8lHU9x8jZ4I5MDiEvc6d1HZGE';

    // Если оплата прошла успешно
    if (body.update_type === 'invoice_paid') {
        const invoice = body.payload;
        // Достаем ник и кол-во звезд, которые мы спрятали в payload
        const info = JSON.parse(invoice.payload);

        const message = `
💰 **ПОЛУЧЕНА ОПЛАТА!**
--------------------------
🌟 **Количество:** ${info.stars} звёзд
👤 **Кому:** @${info.username.replace('@', '')}
💵 **Сумма:** ${invoice.amount} ${invoice.asset}
--------------------------
🚀 *Зайди на Fragment и отправь подарок этому пользователю!*
        `;

        // Отправляем уведомление тебе
        await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage?chat_id=${MY_ID}&text=${encodeURIComponent(message)}&parse_mode=Markdown`);
    }

    // Всегда отвечаем 200 OK, чтобы CryptoBot не слал повторов
    res.status(200).send('OK');
}
