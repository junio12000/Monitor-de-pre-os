import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

# Puxa o token criptografado diretamente da nuvem do GitHub
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = "1509552195"

produtos = [
    {"nome": "Zoom - Ryzen 7 5700X", "url": "https://www.zoom.com.br/search?q=processador%20ryzen%207%205700x", "preco_alvo": 1050, "preco_min": 750, "preco_max": 1600},
    {"nome": "Buscapé - Ryzen 7 5700X", "url": "https://www.buscape.com.br/search?q=processador%20ryzen%207%205700x", "preco_alvo": 1050, "preco_min": 750, "preco_max": 1600},
    {"nome": "Zoom - Placa Mãe AM4 (B550)", "url": "https://www.zoom.com.br/search?q=placa%20mae%20b550m%20am4", "preco_alvo": 600, "preco_min": 400, "preco_max": 1400},
    {"nome": "Buscapé - Placa Mãe AM4 (B550)", "url": "https://www.buscape.com.br/search?q=placa%20mae%20b550m%20am4", "preco_alvo": 600, "preco_min": 400, "preco_max": 1400},
    {"nome": "Zoom - Memória RAM 8GB DDR4 Desktop", "url": "https://www.zoom.com.br/search?q=memoria%20ram%208gb%20ddr4%20desktop", "preco_alvo": 120, "preco_min": 70, "preco_max": 250},
    {"nome": "Zoom - Memória RAM 16GB DDR4 Desktop", "url": "https://www.zoom.com.br/search?q=memoria%20ram%2016gb%20ddr4%20desktop", "preco_alvo": 210, "preco_min": 130, "preco_max": 450},
    {"nome": "Buscapé - Memória RAM 16GB DDR4 Desktop", "url": "https://www.buscape.com.br/search?q=memoria%20ram%2016gb%20ddr4%20desktop", "preco_alvo": 210, "preco_min": 130, "preco_max": 450},
    {"nome": "Zoom - AMD Radeon RX 7600", "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20rx%207600", "preco_alvo": 1500, "preco_min": 1200, "preco_max": 2300},
    {"nome": "Zoom - Intel Arc B580", "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20intel%20arc%20b580", "preco_alvo": 1700, "preco_min": 1300, "preco_max": 2600},
    {"nome": "Zoom - AMD Radeon RX 9060 XT", "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20rx%209060%20xt", "preco_alvo": 2200, "preco_min": 1600, "preco_max": 5000},
    {"nome": "Buscapé - AMD Radeon RX 9060 XT", "url": "https://www.buscape.com.br/search?q=placa%20de%20video%20rx%209060%20xt", "preco_alvo": 2200, "preco_min": 1600, "preco_max": 5000},
    {"nome": "Zoom - AMD Radeon RX 9070 XT", "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20rx%209070%20xt", "preco_alvo": 4300, "preco_min": 3200, "preco_max": 8500}
]

def enviar_telegram(msg):
    if not TOKEN_TELEGRAM:
        print("❌ ERRO GRAVE: A variável TOKEN_TELEGRAM não foi encontrada no servidor!")
        return
    try:
        resposta = requests.post(
            f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage", 
            data={"chat_id": CHAT_ID, "text": msg}, 
            timeout=10
        )
        if resposta.status_code != 200:
            print(f"⚠️ Erro ao enviar para o Telegram: {resposta.text}")
        else:
            print("📲 Mensagem enviada ao Telegram com sucesso!")
    except Exception as e:
        print(f"❌ Erro de conexão com o Telegram: {e}")

def extrair_preco(html, min_p, max_p):
    precos = re.findall(r'R\$\s?([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})', html)
    for p in precos:
        try:
            val = float(p.replace('.', '').replace(',', '.'))
            if min_p <= val <= max_p: return val
        except ValueError: continue
    return None

def bloquear_recursos_desnecessarios(rota):
    if rota.request.resource_type in ["image", "media", "font"]: rota.abort()
    else: rota.continue_()

def main():
    print("🤖 Iniciando script...")
    # TESTE DE CONEXÃO: Envia mensagem logo no início!
    enviar_telegram("🤖 Robô do GitHub Actions iniciou uma nova varredura de preços!")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        for item in produtos:
            print(f"Verificando: {item['nome']}...")
            page = context.new_page()
            page.route("**/*", bloquear_recursos_desnecessarios)
            try:
                page.goto(item["url"], timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(4000)
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(2000)
                
                preco = extrair_preco(page.content(), item["preco_min"], item["preco_max"])
                if preco:
                    print(f"💰 Preço detectado: R$ {preco:.2f}")
                    if preco <= item["preco_alvo"]:
                        enviar_telegram(f"🚨 PROMOÇÃO DETECTADA!\n📦 {item['nome']}\n💰 R$ {preco:.2f}\n🎯 Meta: R$ {item['preco_alvo']:.2f}\n🔗 {item['url']}")
                else:
                    print("⚠️ Nenhum preço válido capturado.")
            except Exception as e:
                print(f"❌ Erro em {item['nome']}: {e}")
            finally:
                page.close()
        browser.close()

if __name__ == "__main__":
    main()
