"""
Scraper para Lojas Rede.
Regra: Pesquisa EAN -> Entra no Produto -> Pega o Preço Principal.
"""

import time
import random
from selenium.webdriver.common.by import By


def fechar_cookies_rede(driver):
    seletores = [
        "//button[contains(text(), 'Aceitar')]",
        "//button[contains(text(), 'Entendi')]",
        "//button[contains(text(), 'Concordar')]"
    ]
    for s in seletores:
        try:
            botao = driver.find_element(By.XPATH, s)
            driver.execute_script("arguments[0].click();", botao)
            time.sleep(0.5)
            break
        except Exception:
            continue


def tratar_valor_rede(texto):
    if not texto:
        return None
    try:
        limpo = texto.lower().replace('r$', '').replace('\xa0', '').replace('&nbsp;', '').strip()
        limpo = limpo.split('cada')[0].split('un')[0].strip()
        limpo = limpo.replace('.', '').replace(',', '.')
        return float(limpo)
    except Exception:
        return None

def consultar_lojas_rede(driver, ean):
    try:
        url_busca = f"https://www.lojasrede.com.br/pesquisa?query={ean}"
        driver.get(url_busca)
        time.sleep(random.uniform(4, 5))
        fechar_cookies_rede(driver)

        html = driver.page_source.lower()
        if "não encontramos resultados" in html or "nenhum produto encontrado" in html:
            return None, None

        seletores_link = [
            'a[class*="product"]',
            'div[class*="productCard"] a',
            'a.vtex-product-summary-2-x-clearLink',
            'section[class*="product"] a'
        ]

        url_produto = None
        for sel in seletores_link:
            try:
                elem_link = driver.find_element(By.CSS_SELECTOR, sel)
                url_produto = elem_link.get_attribute('href')
                if url_produto:
                    break
            except Exception:
                continue

        if not url_produto:
            return None, None

        driver.get(url_produto)
        time.sleep(random.uniform(4, 5))
        fechar_cookies_rede(driver)

        seletores_preco_pdp = [
            '.lojasrede-cashback-0-x-price',                            
            'div[class*="lojasrede-cashback"] div[class*="price"]',     
            'span[class*="vtex-product-price-1-x-sellingPriceValue"]',   
            'span[class*="sellingPrice"]',
            'span[class*="spotPrice"]'
        ]

        preco_final = None
        for sel in seletores_preco_pdp:
            try:
                elementos = driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elementos:
                    txt = elem.text.strip()
                    if txt and ('r$' in txt.lower() or ',' in txt):
                        val = tratar_valor_rede(txt)
                        if val and val > 0:
                            preco_final = val
                            break
                if preco_final:
                    break
            except Exception:
                continue

        if not preco_final:
            return None, None

        vendedor = "PROPRIO"
        try:
            texto_pagina = driver.find_element(By.TAG_NAME, 'body').text.lower()
            if "vendido por" in texto_pagina or "entregue por" in texto_pagina:
                try:
                    vendedor = driver.find_element(By.CSS_SELECTOR, 'span[class*="sellerName"]').text.strip()
                except Exception:
                    vendedor = "Marketplace Lojas Rede"
        except Exception:
            pass

        return preco_final, vendedor

    except Exception:
        return None, None