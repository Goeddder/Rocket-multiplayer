import httpx
import logging
from  config import DATA, FRAGMENT_HASH, FRAGMENT_ADDRES,FRAGMENT_PUBLICKEY,FRAGMENT_WALLETS

def get_cookies(DATA):
    return {
        'stel_ssid': DATA.get('stel_ssid', '0a791baaefc2da4f7e_17021482322052895780'),
        'stel_dt': DATA.get('stel_dt', '-120'),
        'stel_ton_token': DATA.get('stel_ton_token', 'TXCMUcx3By2LsEHL5sPhz0c8blblgPTiLA5Pz6g88_PoL09Dq4DWjP35rjnElv79TBrMCxyIiTSnlay9sQoqeZOXBg3FxfYjLZ8At16S7lrNQJArm8JVCODO_nZXSC0bJeFXEzLI00F0rkS19dv0Ric0xyudXCz9Sq9JWs_aCS9nueKCrQSw9gR46GAbShRc3_ucCFj-'),
        'stel_token': DATA.get('stel_token', 'e9f5c227d3bdf60f806ac6634b6ba4bde9f5c23ce9f5c9fd14f43059def026b1eb6b6'),
    }

class FragmentClient:
    URL = "https://fragment.com/api?hash=747c09519b10e540aa"
    # ... дальше твой остальной код без изменений

    async def fetch_recipient(self, query):
        data = {"query": query, "method": "searchStarsRecipient"}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.URL, cookies=get_cookies(DATA), data=data)
            print(response.json())
            return response.json().get("found", {}).get("recipient")

    async def fetch_req_id(self, recipient, quantity):
        data = {"recipient": recipient, "quantity": quantity, "method": "initBuyStarsRequest"}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.URL, cookies=get_cookies(DATA), data=data)
            print(response.json())
            return response.json().get("req_id")

    async def fetch_buy_link(self, recipient, req_id, quantity):
        data = {
            "address": f"{FRAGMENT_ADDRES}", "chain": "-239",
            "walletStateInit": f"{FRAGMENT_WALLETS}",
            "publicKey": f"{FRAGMENT_PUBLICKEY}",
            "features": ["SendTransaction", {"name": "SendTransaction", "maxMessages": 255}], "maxProtocolVersion": 2,
            "platform": "iphone", "appName": "Tonkeeper", "appVersion": "5.0.14",
            "transaction": "1",
            "id": req_id,
            "show_sender": "0",
            "method": "getBuyStarsLink"
        }
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://fragment.com",
            "referer": f"https://fragment.com/stars/buy?recipient={recipient}&quantity={quantity}",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "x-requested-with": "XMLHttpRequest"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.URL, headers=headers, cookies=get_cookies(DATA), data=data)
            json_data = response.json()
            print(response.json())
            if json_data.get("ok") and "transaction" in json_data:
                transaction = json_data["transaction"]
                return transaction["messages"][0]["address"], transaction["messages"][0]["amount"], transaction["messages"][0]["payload"]
        return None, None, None