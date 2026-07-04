import re
import time
import requests
from playwright.sync_api import sync_playwright

# ==========================================
# 1. CONFIGURAÇÕES DO TELEGRAM
# ==========================================
TOKEN_TELEGRAM = "8964615665:AAF76uQUDYXrzCabd6uxkAHdtpsi2ZXONgM"
CHAT_ID = "1509552195"

# ==========================================
# 2. LISTA DE HARDWARE
# ==========================================
produtos = [
    {
        "nome": "Zoom - Ryzen 7 5700X",
        "url": "https://www.zoom.com.br/search?q=processador%20ryzen%207%205700x",
        "preco_alvo": 1050,
        "preco_min": 750,
        "preco_max": 1600,
        "seletor": ""
    },
    {
        "nome": "Buscapé - Ryzen 7 5700X",
        "url": "https://www.buscape.com.br/search?q=processador%20ryzen%207%205700x",
        "preco_alvo": 1050,
        "preco_min": 750,
        "preco_max": 1600,
        "seletor": ""
    },
    {
        "nome": "Zoom - Placa Mãe AM4 (B550)",
        "url": "https://www.zoom.com.br/search?q=placa%20mae%20b550m%20am4",
        "preco_alvo": 600,
        "preco_min": 400,
        "preco_max": 1400,
        "seletor": ""
    },
    {
        "nome": "Buscapé - Placa Mãe AM4 (B550)",
        "url": "https://www.buscape.com.br/search?q=placa%20mae%20b550m%20am4",
        "preco_alvo": 600,
        "preco_min": 400,
        "preco_max": 1400,
        "seletor": ""
    },
    {
        "nome": "Zoom - Memória RAM 8GB DDR4 Desktop",
        "url": "https://www.zoom.com.br/search?q=memoria%20ram%208gb%20ddr4%20desktop",
        "preco_alvo": 120,
        "preco_min": 70,
        "preco_max": 250,
        "seletor": ""
    },
    {
        "nome": "Zoom - Memória RAM 16GB DDR4 Desktop",
        "url": "https://www.zoom.com.br/search?q=memoria%20ram%2016gb%20ddr4%20desktop",
        "preco_alvo": 210,
        "preco_min": 130,
        "preco_max": 450,
        "seletor": ""
    },
    {
        "nome": "Buscapé - Memória RAM 16GB DDR4 Desktop",
        "url": "https://www.buscape.com.br/search?q=memoria%20ram%2016gb%20ddr4%20desktop",
        "preco_alvo": 210,
        "preco_min": 130,
        "preco_max": 450,
        "seletor": ""
    },
    {
        "nome": "Zoom - AMD Radeon RX 7600",
        "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20rx%207600",
        "preco_alvo": 1500,
        "preco_min": 1200,
        "preco_max": 2300,
        "seletor": ""
    },
    {
        "nome": "Zoom - Intel Arc B580",
        "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20intel%20arc%20b580",
        "preco_alvo": 1700,
        "preco_min": 1300,
        "preco_max": 2600,
        "seletor": ""
    },
    {
        "nome": "Zoom - AMD Radeon RX 9060 XT",
        "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20rx%209060%20xt",
        "preco_alvo": 2200,
        "preco_min": 1600,
        "preco_max": 5000,
        "seletor": ""
    },
    {
        "nome": "Buscapé - AMD Radeon RX 9060 XT",
        "url": "https://www.buscape.com.br/search?q=placa%20de%20video%20rx%209060%20xt",
        "preco_alvo": 2200,
        "preco_min": 1600,
        "preco_max": 5000,
        "seletor": ""
    },
    {
        "nome": "Zoom - AMD Radeon RX 9070 XT",
        "url": "https://www.zoom.com.br/search?q=placa%20de%20video%20rx%209070%20xt",
        "preco_alvo": 4300,
        "preco_min": 3200,
        "preco_max": 8500,
        "seletor": ""
    }
]

# ==========================================
# 3. FUNÇÕES AUXILIARES
# ==========================================
def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
        dados = {"chat_id": CHAT_ID, "text": mensagem}
        requests.post(url, data=dados, timeout=10)
    except Exception as erro:
        print(f"❌ Erro ao enviar mensagem no Telegram: {erro}")

def extrair_preco_regex(texto_html, minimo, maximo):
    padroes = re.findall(r'R\$\s?([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})', texto_html)
    precos_encontrados = []
    
    for p in padroes:
        try:
            valor = float(p.replace('.', '').replace(',', '.'))
            if minimo <= valor <= maximo:
                precos_encontrados.append(valor)
        except ValueError:
            continue
            
    if precos_encontrados:
        return min(precos_encontrados)
    return None

def bloquear_recursos_desnecessarios(rota):
    if rota.request.resource_type in ["image", "media", "font"]:
        rota.abort()
    else:
        rota.continue_()

# ==========================================
# 4. MOTOR PRINCIPAL
# ==========================================
def checar_produtos_playwright():
    with sync_playwright() as p:
        navegador = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox"
            ]
        )
        
        contexto = navegador.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        pagina = contexto.new_page()
        pagina.route("**/*", bloquear_recursos_desnecessarios)

        for item in produtos:
            print(f"\n[{time.strftime('%H:%M:%S')}] Verificando: {item['nome']}...")
            try:
                pagina.goto(item["url"], timeout=30000)
                
                try:
                    pagina.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                
                pagina.mouse.wheel(0, 800)
                pagina.wait_for_timeout(2500)

                preco_atual = None

                if item["seletor"]:
                    try:
                        if pagina.locator(item["seletor"]).count() > 0:
                            texto = pagina.locator(item["seletor"]).first.inner_text()
                            texto_limpo = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
                            preco_atual = float(texto_limpo)
                    except Exception:
                        pass

                if not preco_atual:
                    conteudo_html = pagina.content()
                    preco_atual = extrair_preco_regex(
                        conteudo_html, 
                        item.get("preco_min", 50), 
                        item.get("preco_max", 15000)
                    )

                if preco_atual:
                    print(f"💰 Menor preço detectado: R$ {preco_atual:.2f}")
                    if preco_atual <= item['preco_alvo']:
                        print("🚨 PROMOÇÃO DETECTADA! Enviando Telegram...")
                        enviar_telegram(
                            f"🚨 ALERTA DE QUEDA DE PREÇO!\n\n"
                            f"📦 Item: {item['nome']}\n"
                            f"💰 Preço Atual: R$ {preco_atual:.2f}\n"
                            f"🎯 Seu Alvo era: R$ {item['preco_alvo']:.2f}\n\n"
                            f"🔗 Compre aqui: {item['url']}"
                        )
                else:
                    print(f"⚠️ Nenhum preço na faixa (R$ {item['preco_min']} - R$ {item['preco_max']}) foi capturado.")

            except Exception as e:
                print(f"❌ Erro em {item['nome']}: {e}")
            
            time.sleep(10)

        navegador.close()

if __name__ == "__main__":
    print("🤖 Robô acionado via GitHub Actions!")
    checar_produtos_playwright()