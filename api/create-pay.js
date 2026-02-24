import fetch from 'node-fetch';

export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');
    
    try {
        // Парсим тело запроса
        const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
        const { amount, user } = body; 
        
        const CRYPTO_PAY_TOKEN = '338748:AAcBI08cRpvDBk6mb9V2hPo3zRX0miDxdyc';

        const response = await fetch('https://pay.crypton.sh/api/createInvoice', {
            method: 'POST',
            headers: {
                'Crypto-Pay-API-Token': CRYPTO_PAY_TOKEN,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                asset: 'USDT',
                amount: (amount * 0.028).toFixed(2),
                description: `Покупка ${amount} звезд для ${user}`,
                payload: JSON.stringify({ username: user, stars: amount }),
                paid_btn_name: 'openBot',
                paid_btn_url: 'https://t.me/RocketMultiplayerBot'
            })
        });

        const data = await response.json();
        
        if (data.ok) {
            res.status(200).json({ pay_url: data.result.pay_url });
        } else {
            console.error('CryptoBot Error:', data);
            res.status(500).json({ error: 'Failed to create invoice' });
        }
    } catch (e) {
        console.error('Server Error:', e);
        res.status(500).json({ error: e.message });
    }
}
