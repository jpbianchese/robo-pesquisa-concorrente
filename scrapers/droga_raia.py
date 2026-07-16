"""
Scraper para Droga Raia.
Responsável pela consulta de preços e informações de vendedores no site da Droga Raia.
"""

import time
import random
from selenium.webdriver.common.by import By


def fechar_cookies_raia(driver):
    """
    Fecha modais de cookies da Droga Raia.
    Tenta múltiplos seletores para garantir compatibilidade.
    """
    seletores = ["onetrust-accept-btn-handler", "//button[contains(text(), 'Aceitar')]"]
    for s in seletores:
        try:
            botao = driver.find_element(By.XPATH, s) if s.startswith("//") else driver.find_element(By.ID, s)
            driver.execute_script("arguments[0].click();", botao)
            time.sleep(1)
            break
        except Exception:
            continue


def tratar_valor_raia(texto):
    """
    Extrai e converte o valor de preço da Droga Raia para float.
    Remove formatações e textos adicionais como 'cada', 'un'.
    """
    try:
        limpo = texto.lower().split('cada')[0].split('un')[0].strip()
        return float(limpo.replace('r$', '').replace('\xa0', '').replace('.', '').replace(',', '.'))
    except Exception:
        return None


def consultar_droga_raia(driver, ean):
    """
    Consulta preço e vendedor no site da Droga Raia.
    
    Args:
        driver: WebDriver Selenium
        ean: Código EAN do produto
        
    Returns:
        tuple: (preço: float ou None, vendedor: str ou None)
    """
    try:
        driver.get(f"https://www.drogaraia.com.br/search?w={ean}")
        time.sleep(random.uniform(9, 11)) 
        fechar_cookies_raia(driver)

        if "não encontramos resultados" in driver.page_source.lower():
            return None, None

        seletores_imagem = [
            'img[data-testid="product-image"]',
            'a[data-qa="product-card-link"] img',
            'a[data-qa="product-card-link"]'
        ]
        
        for sel in seletores_imagem:
            try:
                elemento = driver.find_element(By.CSS_SELECTOR, sel)
                driver.execute_script("arguments[0].click();", elemento)
                time.sleep(10)
                break
            except Exception:
                continue
        else:
            return None, None 

        try:
            preco_elem = driver.find_element(By.CSS_SELECTOR, 'span[class*="price-pdp-content"], span.eVpKuL')
            preco_final = tratar_valor_raia(preco_elem.text)
            
            texto_pagina = driver.find_element(By.TAG_NAME, 'body').text.lower()
            termos_raia = ["vendido e entregue por raia", "vendido por droga raia", "entregue por droga raia", "por raia"]
            
            if any(termo in texto_pagina for termo in termos_raia):
                return preco_final, "PROPRIO"
            
            vendedor = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="seller-button"]').text.strip()
            return preco_final, vendedor
            
        except Exception:
            return preco_final if 'preco_final' in locals() else None, "Marketplace Raia" if 'preco_final' in locals() else None

    except Exception:
        return None, None
