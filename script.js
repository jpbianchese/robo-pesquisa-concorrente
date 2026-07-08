// ==========================================
// FUNÇÃO 1: PESQUISA DIRETO NA TELA (TABELA)
// ==========================================
async function iniciar() {
    const campoEan = document.getElementById('listaEan');
    const eans = campoEan.value.split('\n').map(x => x.trim()).filter(x => x);
    const lojas = [];
    
    // Lendo os checkboxes com os IDs corretos
    if(document.getElementById('checkRaia') && document.getElementById('checkRaia').checked) lojas.push('raia');
    if(document.getElementById('checkPacheco') && document.getElementById('checkPacheco').checked) lojas.push('pacheco');
    if(document.getElementById('checkSuperNosso') && document.getElementById('checkSuperNosso').checked) lojas.push('supernosso');
    
    const corpo = document.getElementById('corpo');
    corpo.innerHTML = "";

    if (eans.length === 0) {
        alert("Cole os EANs primeiro!");
        return;
    }

    for(let ean of eans) {
        const novaLinha = document.createElement('tr');
        novaLinha.innerHTML = `
            <td>${ean}</td>
            <td id="raia-${ean}">...</td>
            <td id="pacheco-${ean}">...</td>
            <td id="supernosso-${ean}">...</td>
        `;
        corpo.appendChild(novaLinha);

        try {
            const response = await fetch('http://127.0.0.1:5000/pesquisar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ ean, lojas })
            });
            
            const res = await response.json();
            
            document.getElementById(`raia-${ean}`).innerText = res.raia || '-';
            document.getElementById(`pacheco-${ean}`).innerText = res.pacheco || '-';
            document.getElementById(`supernosso-${ean}`).innerText = res.supernosso || '-';
        } catch (err) {
            document.getElementById(`raia-${ean}`).innerText = "Erro Conexão";
            document.getElementById(`pacheco-${ean}`).innerText = "Erro Conexão";
            document.getElementById(`supernosso-${ean}`).innerText = "Erro Conexão";
            console.error("Erro ao falar com o Python:", err);
        }
    }
}


// ==========================================
// FUNÇÃO 2: PROCESSAMENTO VIA PLANILHA EXCEL
// ==========================================
// NOTA: Certifique-se de que no seu HTML o botão de processar o Excel chame essa função 
// ou adapte o ID do botão ('btnProcessarExcel' é um exemplo)
document.addEventListener("DOMContentLoaded", function() {
    const btnExcel = document.getElementById('btnProcessar'); // Troque pelo ID do seu botão de subir arquivo, se for diferente
    
    if(btnExcel) {
        btnExcel.addEventListener('click', async function() {
            // Se o seu input file tiver outro ID, mude aqui:
            const inputFile = document.getElementById('arquivoExcel'); 
            
            if (!inputFile || inputFile.files.length === 0) {
                alert('Por favor, selecione um arquivo Excel primeiro!');
                return;
            }

            const chkRaia = document.getElementById('checkRaia') ? document.getElementById('checkRaia').checked : false;
            const chkPacheco = document.getElementById('checkPacheco') ? document.getElementById('checkPacheco').checked : false;
            const chkSuperNosso = document.getElementById('checkSuperNosso') ? document.getElementById('checkSuperNosso').checked : false;

            if (!chkRaia && !chkPacheco && !chkSuperNosso) {
                alert('Selecione pelo menos um concorrente para pesquisar!');
                return;
            }

            const formData = new FormData();
            formData.append('file', inputFile.files[0]);
            
            // É aqui que garantimos que o Excel saiba que o Super Nosso foi marcado!
            formData.append('raia', chkRaia);
            formData.append('pacheco', chkPacheco);
            formData.append('supernosso', chkSuperNosso); 

            try {
                // Altera botão visualmente se houver id status
                const divStatus = document.getElementById('status');
                if(divStatus) {
                    divStatus.innerText = "⏳ O robô está processando. Por favor, aguarde...";
                    divStatus.style.color = "#d39e00";
                }
                btnExcel.disabled = true;

                const resposta = await fetch('http://127.0.0.1:5000/processar-excel', {
                    method: 'POST',
                    body: formData
                });

                const resultado = await resposta.json();

                if (resultado.status === 'concluido') {
                    if(divStatus) {
                        divStatus.innerText = "✅ Finalizado! Baixando o arquivo...";
                        divStatus.style.color = "#28a745";
                    }
                    window.location.href = 'http://127.0.0.1:5000/download';
                }
            } catch (erro) {
                console.error(erro);
                alert("Erro ao processar o arquivo. Verifique o terminal.");
            } finally {
                btnExcel.disabled = false;
            }
        });
    }
});