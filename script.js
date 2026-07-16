const baseUrl = 'http://127.0.0.1:5000';

const fileInput = document.getElementById('fileInput');
const status = document.getElementById('status');
const btnIniciar = document.getElementById('btnIniciar');
const btnDownload = document.getElementById('btnDownload');
const fileNameLabel = document.getElementById('fileName');
const dropArea = document.querySelector('.file-drop');

let hideTimeout;

function showStatus(message, color) {
    if (!status) return;
    status.innerText = message;
    status.style.color = color;
    status.classList.add('running');
    status.classList.remove('hidden');
    clearTimeout(hideTimeout);
}

function hideStatus(delay = 3000) {
    if (!status) return;
    clearTimeout(hideTimeout);
    hideTimeout = setTimeout(() => {
        status.classList.add('hidden');
        status.classList.remove('running');
    }, delay);
}

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

    const downloadName = sanitizeDownloadName(document.getElementById('finalName').value || 'pesquisa robo');
    formData.append('download_name', downloadName);

    btnIniciar.disabled = true;
    btnDownload.classList.add('hidden');
    showStatus('O robô está trabalhando... Não feche esta janela.', '#FFFFFF');

    try {
        const response = await fetch(`${baseUrl}/processar-excel`, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (!response.ok) {
            showStatus('Erro ao iniciar processamento. Verifique o terminal do Python.', '#ff6b6b');
            hideStatus(5000);
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

                    if (st.status === 'done') {
                        clearInterval(poll);
                        finishSuccess(st.download_name || downloadName);
                    } else if (st.status === 'error') {
                        clearInterval(poll);
                        showStatus('Erro no processamento: ' + (st.error || ''), '#ff6b6b');
                        hideStatus(7000);
                        btnIniciar.disabled = false;
                    }

                    polls += 1;
                    if (polls > maxPolls) {
                        clearInterval(poll);
                        showStatus('Tempo de espera excedido. Verifique o servidor.', '#ff6b6b');
                        hideStatus(7000);
                        btnIniciar.disabled = false;
                    }
                } catch (err) {
                    console.error('Polling error', err);
                }
            }, pollInterval);
        } else if (result.status === 'concluido') {
            finishSuccess(result.download_name || downloadName);
        } else {
            showStatus('Resposta inesperada do servidor.', '#ff6b6b');
            hideStatus(5000);
            btnIniciar.disabled = false;
        }
    } catch (e) {
        console.error(e);
        showStatus('Erro de conexão. O Python está rodando?', '#ff6b6b');
        hideStatus(5000);
        btnIniciar.disabled = false;
    }
}

function finishSuccess(finalName) {
    if (!btnDownload || !btnIniciar) return;
    showStatus('Processamento concluído.', '#4caf50');
    btnDownload.href = `${baseUrl}/download?filename=${encodeURIComponent(finalName)}`;
    btnDownload.download = finalName;
    btnDownload.classList.remove('hidden');

    const tempLink = document.createElement('a');
    tempLink.href = btnDownload.href;
    tempLink.download = finalName;
    tempLink.style.display = 'none';
    document.body.appendChild(tempLink);
    tempLink.click();
    document.body.removeChild(tempLink);

    hideStatus(3800);
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
