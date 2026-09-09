from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import threading
import logging
from scrapers import (
    iniciar_driver,
    consultar_droga_raia,
    consultar_pacheco,
    consultar_super_nosso,
    consultar_lojas_rede,
    processar_excel_com_scraping
)

app = Flask(__name__)
CORS(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

UPLOAD_FOLDER = 'processamento'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

driver = None

process_state = {
    'status': 'idle',
    'download_name': None,
    'concorrentes_concluidos': [],
    'error': None,
    'progresso': 0,
    'mensagem': 'Aguardando início...'
}

def sanitize_download_name(value):
    if not value:
        return 'pesquisa robo.xlsm'
    name = os.path.basename(value).strip()
    for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(char, '')
    if not name:
        return 'pesquisa robo.xlsm'
    if not name.lower().endswith('.xlsm'):
        name += '.xlsm'
    return name

def atualizar_progresso(porcentagem, mensagem):
    process_state['progresso'] = porcentagem
    process_state['mensagem'] = mensagem

def registrar_concorrente_concluido(chave, nome, caminho):
    process_state['concorrentes_concluidos'].append({
        'chave': chave,
        'nome': nome,
        'arquivo': os.path.basename(caminho),
    })
    process_state['mensagem'] = f'{nome} concluído. Resultado disponível para download.'

@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    global driver
    dados = request.json
    ean = dados.get('ean')
    lojas = dados.get('lojas', [])
    
    if not driver: 
        driver = iniciar_driver()
        
    resultados = {'raia': '-', 'pacheco': '-', 'supernosso': '-', 'lojasrede': '-'}
    
    if 'raia' in lojas:
        valor, vend = consultar_droga_raia(driver, ean)
        resultados['raia'] = f"R$ {valor:.2f}" if valor else "Não enc."
        
    if 'pacheco' in lojas:
        valor, vend = consultar_pacheco(driver, ean)
        resultados['pacheco'] = f"R$ {valor:.2f}" if valor else "Não enc."
        
    if 'supernosso' in lojas:
        valor, vend = consultar_super_nosso(driver, ean)
        resultados['supernosso'] = f"R$ {valor:.2f}" if valor else "Não enc."

    if 'lojasrede' in lojas:
        valor, vend = consultar_lojas_rede(driver, ean)
        resultados['lojasrede'] = f"R$ {valor:.2f}" if valor else "Não enc."
        
    return jsonify(resultados)

@app.route('/processar-excel', methods=['POST'])
def processar_excel():
    global driver
    file = request.files['file']

    fleg_raia = str(request.form.get('raia')).lower() in ['true', 'on', '1', 'yes']
    fleg_pacheco = str(request.form.get('pacheco')).lower() in ['true', 'on', '1', 'yes']
    fleg_supernosso = str(request.form.get('supernosso', request.form.get('checkSuperNosso'))).lower() in ['true', 'on', '1', 'yes']
    fleg_lojasrede = str(request.form.get('lojasrede', request.form.get('checkLojasRede'))).lower() in ['true', 'on', '1', 'yes']
    
    download_name = request.form.get('download_name', 'pesquisa robo')

    print(f"\n🚀 Flags de Ativação -> Raia: {fleg_raia} | Pacheco: {fleg_pacheco} | Super Nosso: {fleg_supernosso} | Lojas Rede: {fleg_lojasrede}")

    caminho_entrada = os.path.join(UPLOAD_FOLDER, "entrada.xlsm")
    caminho_saida = os.path.join(UPLOAD_FOLDER, "RESULTADO_FINAL.xlsm")
    file.save(caminho_entrada)

    final_name = sanitize_download_name(download_name)
    
    process_state['status'] = 'processing'
    process_state['download_name'] = final_name
    process_state['concorrentes_concluidos'] = []
    process_state['error'] = None
    process_state['progresso'] = 0
    process_state['mensagem'] = 'Iniciando a leitura da planilha...'

    def worker():
        global driver
        try:
            if not driver:
                driver = iniciar_driver()

            flags = {
                'raia': fleg_raia,
                'pacheco': fleg_pacheco,
                'supernosso': fleg_supernosso,
                'lojasrede': fleg_lojasrede
            }
            
            processar_excel_com_scraping(
                driver, 
                caminho_entrada, 
                caminho_saida, 
                flags, 
                callback_progresso=atualizar_progresso,
                callback_concorrente=registrar_concorrente_concluido,
            )

            process_state['status'] = 'done'
            process_state['download_name'] = final_name
            process_state['error'] = None
            process_state['progresso'] = 100
            process_state['mensagem'] = 'Concluído com sucesso!'
        except Exception as e:
            process_state['status'] = 'error'
            process_state['error'] = str(e)
            process_state['mensagem'] = f'Erro no processamento: {str(e)}'
            print('Erro no worker:', e)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    return jsonify({"status": "started"})

@app.route('/status')
def status():
    return jsonify(process_state)

@app.route('/download')
def download():
    download_name = request.args.get('filename', process_state.get('download_name', 'RESULTADO_FINAL.xlsm'))
    download_name = os.path.basename(download_name)
    if not download_name.lower().endswith('.xlsm'):
        download_name += '.xlsm'
    try:
        return send_file(os.path.join(UPLOAD_FOLDER, "RESULTADO_FINAL.xlsm"), as_attachment=True, download_name=download_name)
    except TypeError:
        return send_file(os.path.join(UPLOAD_FOLDER, "RESULTADO_FINAL.xlsm"), as_attachment=True, attachment_filename=download_name)

@app.route('/download/<concorrente>')
def download_concorrente(concorrente):
    concorrentes_validos = {'raia', 'pacheco', 'supernosso', 'lojasrede'}
    if concorrente not in concorrentes_validos:
        return jsonify({'error': 'Concorrente inválido'}), 404

    caminho = os.path.join(UPLOAD_FOLDER, f'RESULTADO_FINAL_{concorrente}.xlsm')
    if not os.path.exists(caminho):
        return jsonify({'error': 'Resultado ainda não disponível'}), 404

    nomes = {
        'raia': 'resultado_raia.xlsm',
        'pacheco': 'resultado_pacheco.xlsm',
        'supernosso': 'resultado_super_nosso.xlsm',
        'lojasrede': 'resultado_lojas_rede.xlsm',
    }
    try:
        return send_file(caminho, as_attachment=True, download_name=nomes[concorrente])
    except TypeError:
        return send_file(caminho, as_attachment=True, attachment_filename=nomes[concorrente])

if __name__ == '__main__':
    app.run(port=5000)