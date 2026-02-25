from http.server import BaseHTTPRequestHandler
import json
import httpx
import asyncio

# --- ТВОИ ДАННЫЕ ИЗ CONFIG.PY ---
DATA = {
    'stel_ssid': '00fe1e1452e5088',
    'stel_dt': '-300',
    'stel_ton_token': '-3LybhBTGAYaLzAgNZpMPpTlcqX8Blc9JlT9V6xb2WpSPqH92f4WKNvw4JME0TrIG_S4jQM03hmC_OcPtLtar9d_u6o1ifYqzRZYCwYGMRDmwD-9bFzyu0rfJPYjaxeuCGNji3mlE0ytRWSV_LgsuWFPtevP9cqXi_AuALN6hf07szpv4Z',
    'stel_token': 'd32974e2f7ecd3b772d32974f9d3297d3a8f4021dadb2fe1a0782ce',
}
FRAGMENT_HASH = '4d28250d832b'
FRAGMENT_ADDRES = 'UQATIzX89EOOTqfsr8KE64MXvVSa4CGybjwmkPv3-yHbI3ZE' # Твой адрес
FRAGMENT_PUBLICKEY = '4f14d23cd839899bc7372134f58d95e990c87b262f05f9912'
FRAGMENT_WALLETS = '+PKDCNcYINMf0x/THwL4I7vyZO1E0NMf0x/T//QE0VFDuvKhUVG68qIF+QFUEGT5EPKj+AAkpMjLH1JAyx9SMMv/UhD0AMntVPgPAdMHIcAAn2xRkyDXSpbTB9QC+wDoMOAhwAHjACHAAuMAAcADkTDjDQOkyMsfEssfy/8HBgUEAAr0AMntVABsgQEI1xj6ANM/MFIkgQEI9Fnyp4IQZHN0cnB0gBjIywXLAlAFzxZQA/oCE8tqyx8Syz/Jc/sAAHCBAQjXGPoA0z/IVCBHgQEI9FHyp4IQbm90ZXB0gBjIywXLAlAGzxZQBPoCFMtqEssfyz/Jc/sAAgBu0gf6ANTUIvkABcjKBxXL/8nQd3SAGMjLBcsCIs8WUAX6AhTLaxLMzMlz+wDIQBSBAQj0UfKnAgBRAAAAACmpoxdPFNI82DmJm8c3IexTJTeZwqMDT1jZXpkMh7Ji8F+ZEkACAUgNCgIBIAwLAFm9JCtvaiaECAoGuQ+gIYRw1AgIR6STfSmRDOaQPp/5g3gSgBt4EBSJhxWfMYQCASAREALm0AHQ0wMhcbCSXwTgItdJwSCSXwTgAtMfIYIQcGx1Z70ighBkc3RyvbCSXwXgA/pAMCD6RAHIygfL/8nQ7UTQgQFA1yH0BDBcgQEI9ApvoTGzkl8H4AXTP8glghBwbHVnupI4MOMNA4IQZHN0crqSXwbjDQ8OAIpQBIEBCPRZMO1E0IEBQNcgyAHPFvQAye1UAXKwjiOCEGRzdHKDHrFwgBhQBcsFUAPPFiP6AhPLassfyz/JgED7AJJfA+IAeAH6APQEMPgnbyIwUAqhIb7y4FCCEHBsdWeDHrFwgBhQBMsFJs8WWPoCGfQAy2kXyx9SYMs/IMmAQPsABgARuMl+1E0NcLH4AgFYFRICASAUEwAZrx32omhAEGuQ64WPwAAZrc52omhAIGuQ64X/wAA9sp37UTQgQFA1yH0BDACyMoHy//J0AGBAQj0Cm+hMYHyTjyk='

def get_cookies():
    return DATA

class FragmentAPI:
    URL = f"https://fragment.com/api?hash={FRAGMENT_HASH}"

    async def get_data(self, query, quantity):
        async with httpx.AsyncClient() as client:
            # 1. Ищем получателя
            r_resp = await client.post(self.URL, cookies=get_cookies(), data={"query": query, "method": "searchStarsRecipient"})
            recipient = r_resp.json().get("found", {}).get("recipient")
            if not recipient: return None
            
            # 2. Инициализируем запрос
            i_resp = await client.post(self.URL, cookies=get_cookies(), data={"recipient": recipient, "quantity": quantity, "method": "initBuyStarsRequest"})
            req_id = i_resp.json().get("req_id")
            if not req_id: return None

            # 3. Получаем данные транзакции
            data = {
                "address": FRAGMENT_ADDRES, "chain": "-239", "walletStateInit": FRAGMENT_WALLETS,
                "publicKey": FRAGMENT_PUBLICKEY, "transaction": "1", "id": req_id, "method": "getBuyStarsLink"
            }
            l_resp = await client.post(self.URL, cookies=get_cookies(), data=data)
            json_data = l_resp.json()
            
            if json_data.get("ok") and "transaction" in json_data:
                msg = json_data["transaction"]["messages"][0]
                return {
                    "amount_ton": float(msg["amount"]) / 1_000_000_000,
                    "payload": msg["payload"],
                    "recipient": msg["address"]
                }
        return None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        
        api = FragmentAPI()
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(api.get_data(post_data['user'], post_data['amount']))
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
