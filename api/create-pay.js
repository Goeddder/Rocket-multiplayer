import fetch from 'node-fetch';

export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');
    
    try {
        const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
        const { amount, user } = body; 
        const CRYPTO_PAY_TOKEN = '338748:AAcBI08cRpvDBk6mb9V2hPo3zRX0miDxdyc';

        // 1. Получаем актуальный курс TON к доллару (опционально, если хочешь точность)
        // Но для звезд проще использовать фиксированный коэффициент, который чуть выше рынка
        // На Fragment 50 звезд стоят примерно 1.30 - 1.50$
        
        const pricePerStar = 0.0275; // Базовая цена звезды в USDT
        const finalAmount = (amount * pricePerStar).toFixed(2);

        const response = await fetch('https://pay.crypton.sh/api/createInvoice', {
            method: 'POST',
            headers: {
                'Crypto-Pay-API-Token': CRYPTO_PAY_TOKEN,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                asset: 'USDT', // Используем USDT, так как он стабильнее
                amount: finalAmount,
                description: `Покупка ${amount} звезд для @${user.replace('@', '')}`,
                payload: JSON.stringify({ username: user, stars: amount }),
                paid_btn_name: 'openBot',
                paid_btn_url: 'https://t.me/RocketMultiplayerBot'
            })
        });

        const data = await response.json();
        if (data.ok) {
            res.status(200).json({ pay_url: data.result.pay_url });
        } else {
            res.status(500).json({ error: 'Ошибка CryptoBot API' });
        }
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
}
