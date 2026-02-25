import httpx
import json
import urllib.parse
from Buy_start.config import DATA, FRAGMENT_HASH

class FragmentClient:
    URL = f"https://fragment.com/api?hash={FRAGMENT_HASH}"

    async def fetch_recipient(self, query):
        payload = {
            "query": query.replace('@', ''),
            "method": "searchStarsRecipient"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.URL, cookies=DATA, data=payload)
            return response.json().get("found", {}).get("recipient")

    async def fetch_req_id(self, recipient, amount):
        payload = {
            "recipient": json.dumps(recipient),
            "amount": int(amount),
            "method": "initStarsGift"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.URL, cookies=DATA, data=payload)
            return response.json().get("req_id")

    async def fetch_buy_link(self, recipient, req_id, amount):
        payload = {
            "req_id": req_id,
            "method": "getStarsGiftLink"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.URL, cookies=DATA, data=payload)
            link = response.json().get("link", "")
            if not link: return None, None, None

            # Разбираем ссылку для транзакции
            clean_link = link.replace('ton://transfer/', 'http://f.c/')
            parsed = urllib.parse.urlparse(clean_link)
            address = parsed.path.replace('/', '')
            params = urllib.parse.parse_qs(parsed.query)
            
            return address, params.get('amount', ['0'])[0], params.get('bin', [''])[0]
