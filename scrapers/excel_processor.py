"""
Processador de planilhas Excel.
Responsável pela leitura, processamento e escrita de dados em arquivos .xlsm.
"""

import openpyxl
from scrapers.droga_raia import consultar_droga_raia
from scrapers.drogarias_pacheco import consultar_pacheco
from scrapers.super_nosso import consultar_super_nosso
from scrapers.lojas_rede import consultar_lojas_rede


def processar_excel_com_scraping(driver, caminho_entrada, caminho_saida, flags, callback_progresso=None):
    wb = openpyxl.load_workbook(caminho_entrada, keep_vba=True)
    ws = wb.active

    linhas_validas = [
        r for r in range(5, ws.max_row + 1) if ws[f'A{r}'].value is not None
    ]
    total_linhas = len(linhas_validas)

    for index, row in enumerate(linhas_validas, start=1):
        ean_val = ws[f'A{row}'].value
        ean = str(ean_val).split('.')[0].strip()

        porcentagem = int((index / total_linhas) * 100) if total_linhas > 0 else 0
        mensagem = f"Linha {index}/{total_linhas}"
        
        print(f"🔎 [{porcentagem}%] {mensagem}")

        if callback_progresso:
            callback_progresso(porcentagem, mensagem)

        if flags.get('raia'):
            valor, vendedor = consultar_droga_raia(driver, ean)
            if valor:
                if vendedor == "PROPRIO":
                    ws[f'D{row}'] = valor
                    ws[f'D{row}'].number_format = '#,##0.00'
                else:
                    ws[f'R{row}'] = valor
                    ws[f'R{row}'].number_format = '#,##0.00'
                    ws[f'S{row}'] = vendedor

        if flags.get('pacheco'):
            valor, seller = consultar_pacheco(driver, ean)
            if valor:
                if seller == "PROPRIO":
                    ws[f'E{row}'] = valor
                    ws[f'E{row}'].number_format = '#,##0.00'
                else:
                    if not ws[f'R{row}'].value:
                        ws[f'R{row}'] = valor
                        ws[f'R{row}'].number_format = '#,##0.00'
                        ws[f'S{row}'] = f"{seller} (Pacheco)"

        if flags.get('supernosso'):
            valor, seller = consultar_super_nosso(driver, ean)
            if valor:
                ws[f'F{row}'] = valor
                ws[f'F{row}'].number_format = '#,##0.00'

        if flags.get('lojasrede'):
            valor, seller = consultar_lojas_rede(driver, ean)
            if valor:
                if seller == "PROPRIO":
                    ws[f'G{row}'] = valor  
                    ws[f'G{row}'].number_format = '#,##0.00'
                else:
                    if not ws[f'R{row}'].value:
                        ws[f'R{row}'] = valor
                        ws[f'R{row}'].number_format = '#,##0.00'
                        ws[f'S{row}'] = f"{seller} (Lojas Rede)"

        wb.save(caminho_saida)

    if callback_progresso:
        callback_progresso(100, "Concluído com sucesso!")