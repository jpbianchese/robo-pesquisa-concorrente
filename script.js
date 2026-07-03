async function iniciar() {
    const campoEan = document.getElementById('listaEan');
    const eans = campoEan.value.split('\n').map(x => x.trim()).filter(x => x);
    const lojas = [];
    if(document.getElementById('raia').checked) lojas.push('raia');
    if(document.getElementById('pacheco').checked) lojas.push('pacheco');
    
    const corpo = document.getElementById('corpo');
    corpo.innerHTML = "";

    if (eans.length === 0) {
        alert("Cole os EANs primeiro!");
        return;
    }

    for(let ean of eans) {
        const novaLinha = document.createElement('tr');
        novaLinha.innerHTML = `<td>${ean}</td><td id="raia-${ean}">...</td><td id="pacheco-${ean}">...</td>`;
        corpo.appendChild(novaLinha);

        try {
            const response = await fetch('http://127.0.0.1:5000/pesquisar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ ean, lojas })
            });
            
            const res = await response.json();
            
            document.getElementById(`raia-${ean}`).innerText = res.raia;
            document.getElementById(`pacheco-${ean}`).innerText = res.pacheco;
        } catch (err) {
            document.getElementById(`raia-${ean}`).innerText = "Erro Conexão";
            document.getElementById(`pacheco-${ean}`).innerText = "Erro Conexão";
            console.error("Erro ao falar com o Python:", err);
        }
    }
}