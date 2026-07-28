const baseUrl = 'http://127.0.0.1:5000';

const fileInput = document.getElementById('fileInput');
const btnIniciar = document.getElementById('btnIniciar');
const btnDownload = document.getElementById('btnDownload');
const fileNameLabel = document.getElementById('fileName');
const dropArea = document.querySelector('.file-drop');

const progressContainer = document.getElementById('progressContainer');
const statusText = document.getElementById('statusText');
const progressPercent = document.getElementById('progressPercent');
const progressBar = document.getElementById('progressBar');

function updateFileDisplay() {
    if (!fileInput || !fileNameLabel || !dropArea) return;
    if (!fileInput.files.length) {
        fileNameLabel.textContent = 'Nenhum arquivo selecionado';
        dropArea.classList.remove('has-file', 'attached');
        return;
    }

    fileNameLabel.textContent = fileInput.files[0].name;
    dropArea.classList.add('has-file', 'attached');
    setTimeout(() => dropArea.classList.remove('attached'), 1200);
}

function sanitizeDownloadName(value) {
    let desiredName = value && value.trim() ? value.trim() : 'pesquisa robo';
    desiredName = desiredName.replace(/[\\/:*?"<>|]+/g, '').trim();
    if (!desiredName.toLowerCase().endsWith('.xlsm')) {
        desiredName += '.xlsm';
    }
    return desiredName;
}

function resetProgressUI() {
    progressContainer.classList.remove('hidden');
    btnDownload.classList.add('hidden');
    statusText.innerText = 'Iniciando o robô... Não feche a janela.';
    statusText.style.color = 'var(--accent)';
    progressPercent.innerText = '0%';
    progressBar.style.width = '0%';
}

async function upload() {
    if (!fileInput || !btnIniciar || !btnDownload) return;
    if (fileInput.files.length === 0) {
        alert('Selecione um arquivo!');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('raia', document.getElementById('checkRaia').checked);
    formData.append('pacheco', document.getElementById('checkPacheco').checked);
    formData.append('supernosso', document.getElementById('checkSuperNosso').checked);
    
    const checkLojasRede = document.getElementById('checkLojasRede');
    formData.append('lojasrede', checkLojasRede ? checkLojasRede.checked : false);

    const downloadName = sanitizeDownloadName(document.getElementById('finalName').value || 'pesquisa robo');
    formData.append('download_name', downloadName);

    // Desabilita o botão e prepara a UI
    btnIniciar.disabled = true;
    resetProgressUI();

    try {
        const response = await fetch(`${baseUrl}/processar-excel`, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (!response.ok) {
            statusText.innerText = 'Erro ao iniciar processamento. Verifique o terminal do Python.';
            statusText.style.color = 'var(--danger)';
            btnIniciar.disabled = false;
            return;
        }

        if (result.status === 'started') {
            let polls = 0;
            const pollInterval = 1200;
            const maxPolls = 3600;
            
            const poll = setInterval(async () => {
                try {
                    const sres = await fetch(`${baseUrl}/status`);
                    if (!sres.ok) return;
                    const st = await sres.json();

                    // Atualiza a interface com os dados em tempo real
                    if (st.status === 'processing') {
                        const percent = st.progresso || 0;
                        const msg = st.mensagem || 'Processando...';
                        
                        progressPercent.innerText = percent + '%';
                        progressBar.style.width = percent + '%';
                        statusText.innerText = msg;
                    } 
                    else if (st.status === 'done') {
                        clearInterval(poll);
                        progressPercent.innerText = '100%';
                        progressBar.style.width = '100%';
                        statusText.innerText = 'Processamento concluído com sucesso!';
                        statusText.style.color = 'var(--success)';
                        finishSuccess(st.download_name || downloadName);
                    } 
                    else if (st.status === 'error') {
                        clearInterval(poll);
                        statusText.innerText = 'Erro no processamento: ' + (st.error || '');
                        statusText.style.color = 'var(--danger)';
                        btnIniciar.disabled = false;
                    }

                    polls += 1;
                    if (polls > maxPolls) {
                        clearInterval(poll);
                        statusText.innerText = 'Tempo de espera excedido. Verifique o servidor.';
                        statusText.style.color = 'var(--danger)';
                        btnIniciar.disabled = false;
                    }
                } catch (err) {
                    console.error('Polling error', err);
                }
            }, pollInterval);
            
        } else if (result.status === 'concluido') {
            finishSuccess(result.download_name || downloadName);
        } else {
            statusText.innerText = 'Resposta inesperada do servidor.';
            statusText.style.color = 'var(--danger)';
            btnIniciar.disabled = false;
        }
    } catch (e) {
        console.error(e);
        statusText.innerText = 'Erro de conexão. O Python está rodando?';
        statusText.style.color = 'var(--danger)';
        btnIniciar.disabled = false;
    }
}

function finishSuccess(finalName) {
    if (!btnDownload || !btnIniciar) return;
    
    // Mostra o botão de download
    btnDownload.href = `${baseUrl}/download?filename=${encodeURIComponent(finalName)}`;
    btnDownload.download = finalName;
    btnDownload.classList.remove('hidden');

    // Força o download automático (mantendo sua lógica original)
    const tempLink = document.createElement('a');
    tempLink.href = btnDownload.href;
    tempLink.download = finalName;
    tempLink.style.display = 'none';
    document.body.appendChild(tempLink);
    tempLink.click();
    document.body.removeChild(tempLink);

    btnIniciar.disabled = false;
}

function handleFileChange() {
    updateFileDisplay();
}

window.addEventListener('DOMContentLoaded', () => {
    if (fileInput) {
        fileInput.addEventListener('change', handleFileChange);
    }
    if (btnIniciar) {
        btnIniciar.addEventListener('click', upload);
    }
    updateFileDisplay();
});