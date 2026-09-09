"""
Processador de planilhas Excel.
Responsável pela leitura, processamento e escrita de dados em arquivos .xlsm.
"""

import openpyxl
import os
import shutil
from scrapers.droga_raia import consultar_droga_raia
from scrapers.drogarias_pacheco import consultar_pacheco
from scrapers.super_nosso import consultar_super_nosso
from scrapers.lojas_rede import consultar_lojas_rede


def processar_excel_com_scraping(
    driver,
    caminho_entrada,
    caminho_saida,
    flags,
    callback_progresso=None,
    callback_concorrente=None,
):
    wb = openpyxl.load_workbook(caminho_entrada, keep_vba=True)
    ws = wb.active

    linhas_validas = [
        r for r in range(5, ws.max_row + 1) if ws[f'A{r}'].value is not None
    ]
    total_linhas = len(linhas_validas)
    concorrentes = [
        ('raia', 'Raia', consultar_droga_raia),
        ('pacheco', 'Pacheco', consultar_pacheco),
        ('supernosso', 'Super Nosso', consultar_super_nosso),
        ('lojasrede', 'Lojas Rede', consultar_lojas_rede),
    ]
    concorrentes = [concorrente for concorrente in concorrentes if flags.get(concorrente[0])]
    total_etapas = len(concorrentes) * total_linhas
    etapa_atual = 0

    for concorrente_index, (chave, nome, consultar) in enumerate(concorrentes):
        for row in linhas_validas:
            ean_val = ws[f'A{row}'].value
            ean = str(ean_val).split('.')[0].strip()
            etapa_atual += 1
            porcentagem = int((etapa_atual / total_etapas) * 100) if total_etapas > 0 else 0
            produto_index = etapa_atual - (concorrente_index * total_linhas)
            mensagem = f"{nome}: produto {produto_index}/{total_linhas}"

            print(f"🔎 [{porcentagem}%] {mensagem}")
            if callback_progresso:
                callback_progresso(porcentagem, mensagem)

            valor, seller = consultar(driver, ean)
            if not valor:
                continue

            if chave == 'raia':
                if seller == "PROPRIO":
                    ws[f'D{row}'] = valor
                    ws[f'D{row}'].number_format = '#,##0.00'
                else:
                    ws[f'R{row}'] = valor
                    ws[f'R{row}'].number_format = '#,##0.00'
                    ws[f'S{row}'] = seller
            elif chave == 'pacheco':
                if seller == "PROPRIO":
                    ws[f'E{row}'] = valor
                    ws[f'E{row}'].number_format = '#,##0.00'
                elif not ws[f'R{row}'].value:
                    ws[f'R{row}'] = valor
                    ws[f'R{row}'].number_format = '#,##0.00'
                    ws[f'S{row}'] = f"{seller} (Pacheco)"
            elif chave == 'supernosso':
                ws[f'F{row}'] = valor
                ws[f'F{row}'].number_format = '#,##0.00'
            elif chave == 'lojasrede':
                if seller == "PROPRIO":
                    ws[f'G{row}'] = valor
                    ws[f'G{row}'].number_format = '#,##0.00'
                elif not ws[f'R{row}'].value:
                    ws[f'R{row}'] = valor
                    ws[f'R{row}'].number_format = '#,##0.00'
                    ws[f'S{row}'] = f"{seller} (Lojas Rede)"

        wb.save(caminho_saida)
        snapshot_path = os.path.splitext(caminho_saida)[0] + f"_{chave}.xlsm"
        shutil.copyfile(caminho_saida, snapshot_path)
        if callback_concorrente:
            callback_concorrente(chave, nome, snapshot_path)

    if callback_progresso:
        callback_progresso(100, "Concluído com sucesso!")