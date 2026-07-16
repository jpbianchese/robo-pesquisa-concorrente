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
    'error': None
}


def sanitize_download_name(value):
    if not value:
        return 'pesquisa robo.xlsm'
    name = os.path.basename(value).strip()
    name = name.replace('\\', '').replace('/', '')
    name = name.replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
    if not name:
        return 'pesquisa robo.xlsm'
    if not name.lower().endswith('.xlsm'):
        name += '.xlsm'
    return name


@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    global driver
    dados = request.json
    ean = dados.get('ean')
    lojas = dados.get('lojas', [])
    
    if not driver: 
        driver = iniciar_driver()
        
    resultados = {'raia': '-', 'pacheco': '-', 'supernosso': '-'}
    
    if 'raia' in lojas:
        valor, vend = consultar_droga_raia(driver, ean)
        resultados['raia'] = f"R$ {valor:.2f}" if valor else "Não enc."
        
    if 'pacheco' in lojas:
        valor, vend = consultar_pacheco(driver, ean)
        resultados['pacheco'] = f"R$ {valor:.2f}" if valor else "Não enc."
        
    if 'supernosso' in lojas:
        valor, vend = consultar_super_nosso(driver, ean)
        resultados['supernosso'] = f"R$ {valor:.2f}" if valor else "Não enc."
        
    return jsonify(resultados)


@app.route('/processar-excel', methods=['POST'])
def processar_excel():
    global driver
    file = request.files['file']

    fleg_raia = str(request.form.get('raia')).lower() in ['true', 'on', '1', 'yes']
    fleg_pacheco = str(request.form.get('pacheco')).lower() in ['true', 'on', '1', 'yes']
    fleg_supernosso = str(request.form.get('supernosso', request.form.get('checkSuperNosso'))).lower() in ['true', 'on', '1', 'yes']
    download_name = request.form.get('download_name', 'pesquisa robo')

    print(f"\n🚀 Flags de Ativação -> Raia: {fleg_raia} | Pacheco: {fleg_pacheco} | Super Nosso: {fleg_supernosso}")

    caminho_entrada = os.path.join(UPLOAD_FOLDER, "entrada.xlsm")
    caminho_saida = os.path.join(UPLOAD_FOLDER, "RESULTADO_FINAL.xlsm")
    file.save(caminho_entrada)

    final_name = sanitize_download_name(download_name)
    process_state['status'] = 'running'
    process_state['download_name'] = final_name
    process_state['error'] = None

    def worker():
        global driver
        try:
            if not driver:
                driver = iniciar_driver()

            flags = {
                'raia': fleg_raia,
                'pacheco': fleg_pacheco,
                'supernosso': fleg_supernosso
            }
            
            processar_excel_com_scraping(driver, caminho_entrada, caminho_saida, flags)

            process_state['status'] = 'done'
            process_state['download_name'] = final_name
            process_state['error'] = None
        except Exception as e:
            process_state['status'] = 'error'
            process_state['error'] = str(e)
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


if __name__ == '__main__':
    app.run(port=5000)