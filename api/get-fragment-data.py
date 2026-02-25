from http.server import BaseHTTPRequestHandler
import json
import httpx
import asyncio

# Твои актуальные данные, которые ты прислал
DATA = {
    'stel_ssid': '0a791baaefc2da4f7e_17021482322052895780',
    'stel_dt': '-120',
    'stel_ton_token': 'TXCMUcx3By2LsEHL5sPhz0c8blblgPTiLA5Pz6g88_PoL09Dq4DWjP35rjnElv79TBrMCxyIiTSnlay9sQoqeZOXBg3FxfYjLZ8At16S7lrNQJArm8JVCODO_nZXSC0bJeFXEzLI00F0rkS19dv0Ric0xyudXCz9Sq9JWs_aCS9nueKCrQSw9gR46GAbShRc3_ucCFj-',
    'stel_token': 'e9f5c227d3bdf60f806ac6634b6ba4bde9f5c23ce9f5c9fd14f43059def026b1eb6b6',
}
FRAGMENT_HASH = '747c09519b10e540aa'

# Данные твоего кошелька (из оригинального конфига)
FRAGMENT_ADDRES = 'UQATIzX89EOOTqfsr8KE64MXvVSa4CGybjwmkPv3-yHbI3ZE'
FRAGMENT_PUBLICKEY = '4f14d23cd839899bc7372134f58d95e990c87b262f05f9912'
# walletStateInit из твоего Buy Stars/config.py
FRAGMENT_WALLETS = '+PKDCNcYINMf0x/THwL4I7vyZO1E0NMf0x/T//QE0VFDuvKhUVG68qIF+QFUEGT5EPKj+AAkpMjLH1JAyx9SMMv/UhD0AMntVPgPAdMHIcAAn2xRkyDXSpbTB9QC+wDoMOAhwAHjACHAAuMAAcADkTDjDQOkyMsfEssfy/8HBgUEAAr0AMntVABsgQEI1xj6ANM/MFIkgQEI9Fnyp4IQZHN0cnB0gBjIywXLAlAFzxZQA/oCE8tqyx8Syz/Jc/sAAHCBAQjXGPoA0z/IVCBHgQEI9FHyp4IQbm90ZXB0gBjIywXLAlAGzxZQBPoCFMtqEssfyz/Jc/sAAgBu0gf6ANTUIvkABcjKBxXL/8nQd3SAGMjLBcsCIs8WUAX6AhTLaxLMzMlz+wDIQBSBAQj0UfKnAgBRAAAAACmpoxdPFNI82DmJm8c3IexTJTeZwqMDT1jZXpkMh7Ji8F+ZEkACAUgNCgIBIAwLAFm9JCtvaiaECAoGuQ+gIYRw1AgIR6STfSmRDOaQPp/5g3gSgBt4EBSJhxWfMYQCASAREALm0AHQ0wMhcbCSXwTgItdJwSCSXwTgAtMfIYIQcGx1Z70ighBkc3RyvbCSXwXgA/pAMCD6RAHIygfL/8nQ7UTQgQFA1yH0BDBcgQEI9ApvoTGzkl8H4AXTP8glghBwbHVnupI4MOMNA4IQZHN0crqSXwbjDQ8OAIpQBIEBCPRZMO1E0IEBQNcgyAHPFvQAye1UAXKwjiOCEGRzdHKDHrFwgBhQBcsFUAPPFiP6AhPLassfyz/JgED7AJJfA+IAeAH6APQEMPgnbyIwUAqhIb7y4FCCEHBsdWeDHrFwgBhQBMsFJs8WWPoCGfQAy2kXyx9SYMs/IMmAQPsABgARuMl+1E0NcLH4AgFYFRICASAUEwAZrx32omhAEGuQ64WPwAAZrc52omhAIGuQ64X/wAA9sp37UTQgQFA1yH0BDACyMoHy//J0AGBAQj0Cm+hMYHyTjyk='

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        
        async def get_data():
            async with httpx.AsyncClient() as client:
                url = f"https://fragment.com/api?hash={FRAGMENT_HASH}"
                
                # 1. Поиск получателя (как в client.py)
                r_recipient = await client.post(url, cookies=DATA, data={
                    "query": post_data['user'], 
                    "method": "searchStarsRecipient"
                })
                recipient = r_recipient.json().get("found", {}).get("recipient")
                if not recipient: return {"ok": False, "error": "Recipient not found"}

                # 2. Создание запроса
                r_req = await client.post(url, cookies=DATA, data={
                    "recipient": recipient, 
                    "quantity": post_data['amount'], 
                    "method": "initBuyStarsRequest"
                })
                req_id = r_req.json().get("req_id")
                if not req_id: return {"ok": False, "error": "Init request failed"}

                # 3. Получение финальных данных (Payload и сумма)
                r_final = await client.post(url, cookies=DATA, data={
                    "address": FRAGMENT_ADDRES,
                    "chain": "-239",
                    "walletStateInit": FRAGMENT_WALLETS,
                    "publicKey": FRAGMENT_PUBLICKEY,
                    "transaction": "1",
                    "id": req_id,
                    "method": "getBuyStarsLink"
                })
                
                res = r_final.json()
                if res.get("ok"):
                    msg = res["transaction"]["messages"][0]
                    return {
                        "ok": True,
                        "amount_ton": float(msg["amount"]) / 1_000_000_000,
                        "payload": msg["payload"],
                        "recipient": msg["address"]
                    }
                return {"ok": False, "error": "Final data failed"}

        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(get_data())
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
