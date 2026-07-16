"""
Scraper para Super Nosso.
Responsável pela consulta de preços no site da Super Nosso.
"""

import time
import random
from selenium.webdriver.common.by import By


def tratar_valor_super_nosso(texto):
    """
    Extrai e converte o valor de preço da Super Nosso para float.
    Remove formatações, espaços e caracteres especiais.
    """
    try:
        if not texto: return None
        limpo = texto.lower().replace('r$', '').replace('\n', '').replace(' ', '').replace('\xa0', '').strip()
        limpo = limpo.replace('.', '')
        return float(limpo.replace(',', '.'))
    except Exception:
        return None


def _pegar_link_produto_supernosso(driver):
    """
    Extrai o link do primeiro produto nos resultados de busca Super Nosso.
    Usa JavaScript para buscar em links e estrutura de artigos.
    """
    js_pegar_link_sn = """
    var links = document.querySelectorAll('a[href$="/p"]');
    for(var i=0; i < links.length; i++) {
        if(links[i].href && links[i].href.includes('supernosso.com')) {
            return links[i].href;
        }
    }
    var article = document.querySelector('article.vtex-product-summary-2-x-element');
    if(article) {
        var link = article.querySelector('a');
        if(link && link.href) return link.href;
    }
    return null;
    """
    return driver.execute_script(js_pegar_link_sn)


def _extrair_preco_supernosso(driver):
    """
    Extrai o preço do produto na página de detalhes Super Nosso.
    Tenta extrair através de JavaScript primeiro, depois CSS como fallback.
    """
    js_pegar_preco = """
    var caixaPreco = document.querySelector('[class*="sellingPrice"]');
    if(caixaPreco) {
        var intElem = caixaPreco.querySelector('[class*="currencyInteger"]');
        var fracElem = caixaPreco.querySelector('[class*="currencyFraction"]');
        
        if(intElem && fracElem) {
            return intElem.innerText.trim() + ',' + fracElem.innerText.trim();
        }
        return caixaPreco.innerText;
    }
    return null;
    """
    texto_preco = driver.execute_script(js_pegar_preco)
    
    if not texto_preco:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, '[class*="sellingPriceValue"]')
            texto_preco = elem.text
        except:
            pass

    return texto_preco


def consultar_super_nosso(driver, ean):
    """
    Consulta preço no site da Super Nosso.
    
    Args:
        driver: WebDriver Selenium
        ean: Código EAN do produto
        
    Returns:
        tuple: (preço: float ou None, vendedor: sempre "PROPRIO")
    """
    try:
        driver.get(f"https://www.supernosso.com/{ean}")
        time.sleep(random.uniform(6, 8))

        texto_pesquisa = driver.find_element(By.TAG_NAME, 'body').text.lower()
        if "não encontramos" in texto_pesquisa or "nenhum resultado" in texto_pesquisa:
            return None, None

        link_produto = _pegar_link_produto_supernosso(driver)

        if link_produto:
            print(f"🔗 [Super Nosso] Entrando no produto: {link_produto}")
            driver.get(link_produto)
            time.sleep(random.uniform(5, 7))
        else:
            print("❌ [Super Nosso] Produto não encontrado na busca.")
            return None, None

        texto_preco = _extrair_preco_supernosso(driver)

        if texto_preco:
            preco_final = tratar_valor_super_nosso(texto_preco)
            if preco_final:
                print(f"💰 [Super Nosso] Preço capturado: R$ {preco_final}")
                return preco_final, "PROPRIO"
                
        return None, None

    except Exception as e:
        return None, None
