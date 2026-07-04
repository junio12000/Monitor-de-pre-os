import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

# Puxa o token criptografado diretamente da nuvem do GitHub
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = "1509552195"  # O ID do chat pode ficar normal, pois não é uma senha
produtos = [
    {"nome": "Zoom - Ryzen 7 5700X", "url": "https://www.zoom.com.br/search?q=processador%20ryzen%207%205700x", "preco_alvo": 1050, "preco_min": 750, "preco_max": 1600},
    {"nome": "Buscapé - Ryzen 7 5700X", "url": "https://www.buscape.com.br/search?q=processador%20ryzen%207%205700x", "preco_alvo": 1050, "preco_min": 750, "preco_max": 1600},
    {"nome": "Zoom - RX 9060 XT", "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20rx%209060%20xt", "preco_alvo": 2200, "preco_min": 1600, "preco_max": 5000}
]

def enviar_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def extrair_preco(html, min_p, max_p):
    precos = re.findall(r'R\$\s?([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})', html)
    for p in precos:
        val = float(p.replace('.', '').replace(',', '.'))
        if min_p <= val <= max_p: return val
    return None

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        for item in produtos:
            page = context.new_page()
            try:
                page.goto(item["url"], timeout=60000)
                page.wait_for_timeout(5000)
                preco = extrair_preco(page.content(), item["preco_min"], item["preco_max"])
                if preco and preco <= item["preco_alvo"]:
                    enviar_telegram(f"🚨 PROMOÇÃO: {item['nome']} por R$ {preco:.2f}\n{item['url']}")
            except Exception as e:
                print(f"Erro em {item['nome']}: {e}")
            finally:
                page.close()
        browser.close()

if __name__ == "__main__":
    main()
