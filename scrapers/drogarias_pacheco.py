"""
Scraper para Drogarias Pacheco.
Responsável pela consulta de preços e informações de vendedores no site da Drogarias Pacheco.
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def exterminar_modais_pacheco(driver):
    """
    Remove múltiplos modais e popups que podem aparecer no site da Pacheco.
    Usa JavaScript para eliminar cookies, modais de PBM e VTEX.
    """
    js_ninja = """
    var btnCookie = document.querySelector('div.dp-bar-dismiss');
    if(btnCookie) { btnCookie.click(); }
    var btnCookieAlt = document.getElementById('onetrust-accept-btn-handler');
    if(btnCookieAlt) { btnCookieAlt.click(); }
    var btnPbm = document.querySelector('button.btn-close[data-bs-dismiss="modal"]');
    if(btnPbm) { btnPbm.click(); }
    var btnVtex = document.querySelector('.vtex-modal-layout-0-x-closeButton');
    if(btnVtex) { btnVtex.click(); }
    """
    try:
        driver.execute_script(js_ninja)
    except Exception:
        pass


def tratar_valor_pacheco(texto):
    """
    Extrai e converte o valor de preço da Pacheco para float.
    Remove formatações, espaços e textos adicionais como 'cada', 'un', 'por'.
    """
    try:
        if not texto: return None
        limpo = texto.lower().split('cada')[0].split('un')[0].split('por')[-1].strip()
        return float(limpo.replace('r$', '').replace('\xa0', '').replace('.', '').replace(',', '.'))
    except Exception:
        return None


def _pegar_link_produto_pacheco(driver):
    """
    Extrai o link do primeiro produto visível nos resultados da busca Pacheco.
    Prioriza links na viewport visível.
    """
    js_pegar_link = """
    var links = document.querySelectorAll('a[href$="/p"]');
    for(var i=0; i < links.length; i++) {
        var rect = links[i].getBoundingClientRect();
        if(rect.top > 0 && rect.top < window.innerHeight && rect.width > 50 && rect.height > 50) {
            if(window.getComputedStyle(links[i]).visibility !== 'hidden') {
                return links[i].href;
            }
        }
    }
    var galeria = document.querySelector('div[id^="gallery"], div[class*="search-result"]');
    if(galeria) {
        var linkGaleria = galeria.querySelector('a[href$="/p"]');
        if(linkGaleria) return linkGaleria.href;
    }
    return null;
    """
    return driver.execute_script(js_pegar_link)


def _extrair_preco_pacheco(driver):
    """
    Extrai o preço do produto na página de detalhes da Pacheco.
    Tenta múltiplos seletores CSS para compatibilidade.
    """
    seletores_preco = [
        '[class*="sellingPriceValue"]',
        '.vtex-store-components-3-x-sellingPriceValue',
        '.vtex-product-price-1-x-sellingPriceValue',
        '[class*="sellingPrice"]',
        '.valor-por',
        'strong.skuBestPrice'
    ]

    preco_final = None
    for sel_p in seletores_preco:
        try:
            preco_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel_p))
            )
            texto_preco = preco_elem.text.strip()
            if texto_preco:  
                preco_final = tratar_valor_pacheco(texto_preco)
                if preco_final: 
                    break
        except Exception:
            continue
    
    return preco_final


def _extrair_vendedor_pacheco(driver):
    """
    Extrai o nome do vendedor da página de detalhes Pacheco.
    Tenta múltiplas abordagens e padrões de texto.
    """
    try:
        try:
            vendedor_mkt = driver.find_element(By.CSS_SELECTOR, 'a[data-bs-target="#rnk-comp-modal-seller"]')
            nome_vendedor = vendedor_mkt.text.strip()
            if nome_vendedor and "pacheco" not in nome_vendedor.lower():
                return nome_vendedor
        except Exception:
            pass 
        
        try:
            vendedor_elem = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.vtex-store-components-3-x-sellerName, [class*="sellerName"]'))
            )
            nome_vendedor = vendedor_elem.text.strip()
            if "pacheco" in nome_vendedor.lower():
                return "PROPRIO"
            elif nome_vendedor != "":
                return nome_vendedor
        except Exception:
            pass
            
        texto_pagina = driver.find_element(By.TAG_NAME, 'body').text.lower()
        if "vendido e entregue por" in texto_pagina:
            trecho = texto_pagina.split("vendido e entregue por")[1].split('\n')[0].strip()
            if "pacheco" in trecho:
                return "PROPRIO"
            else:
                return trecho.title()
                
        if "entregue por drogaria pacheco" in texto_pagina or "vendido por drogaria pacheco" in texto_pagina:
             return "PROPRIO"
             
        return "PROPRIO"
    except Exception:
        return "PROPRIO"


def consultar_pacheco(driver, ean):
    """
    Consulta preço e vendedor no site da Drogarias Pacheco.
    
    Args:
        driver: WebDriver Selenium
        ean: Código EAN do produto
        
    Returns:
        tuple: (preço: float ou None, vendedor: str ou None)
    """
    try:
        driver.get(f"https://www.drogariaspacheco.com.br/pesquisa?q={ean}")
        time.sleep(random.uniform(6, 8))
        exterminar_modais_pacheco(driver)

        texto_pesquisa = driver.find_element(By.TAG_NAME, 'body').text.lower()
        if "não encontramos" in texto_pesquisa or "ops!" in texto_pesquisa:
            return None, None

        link_produto = _pegar_link_produto_pacheco(driver)

        if link_produto:
            driver.get(link_produto) 
            time.sleep(random.uniform(5, 7)) 
            exterminar_modais_pacheco(driver)
        else:
            return None, None

        preco_final = _extrair_preco_pacheco(driver)

        if not preco_final:
            return None, None
            
        vendedor = _extrair_vendedor_pacheco(driver)
        return preco_final, vendedor

    except Exception:
        return None, None
