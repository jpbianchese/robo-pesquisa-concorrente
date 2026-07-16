"""
Módulo scrapers - Contém toda a lógica de web scraping e processamento de dados.

Estrutura:
- selenium_setup: Inicialização e configuração do WebDriver Chrome
- droga_raia: Scraper para o site Droga Raia
- drogarias_pacheco: Scraper para o site Drogarias Pacheco
- super_nosso: Scraper para o site Super Nosso
- excel_processor: Processamento e automação de planilhas Excel
"""

from .selenium_setup import iniciar_driver
from .droga_raia import consultar_droga_raia
from .drogarias_pacheco import consultar_pacheco
from .super_nosso import consultar_super_nosso
from .excel_processor import processar_excel_com_scraping

__all__ = [
    'iniciar_driver',
    'consultar_droga_raia',
    'consultar_pacheco',
    'consultar_super_nosso',
    'processar_excel_com_scraping',
]
