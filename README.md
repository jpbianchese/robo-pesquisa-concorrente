>Robô de Pesquisa de Concorrentes

Este robô automatiza a pesquisa de preços de produtos nos sites concorrentes e gera uma planilha comparativa atualizada.

---

## 🛠️ Pré-requisitos (O que você precisa instalar)

Antes de começar, você precisa ter instalado no seu computador:

1. **Python** (Linguagem de programação que roda o robô):
   * 👉 [Baixar Python (Site Oficial)](https://www.python.org/downloads/)
   * *Atenção na instalação:* Lembre-se de marcar a caixinha **"Add Python to PATH"** logo na primeira tela do instalador!

2. **Git** (Ferramenta para baixar e atualizar o código):
   * 👉 [Baixar Git (Site Oficial)](https://git-scm.com/downloads)

---

## ⬇️ Como instalar o projeto (Primeira vez)

Com os dois programas acima instalados, abra o aplicativo do **VS Code** e siga a sequência de passos abaixo:

### Passo 1: Abrir o Terminal no VS Code
Com o VS Code aberto, abra o terminal integrado usando o atalho do seu teclado:
* No Windows/Linux: aperte **`Ctrl + '`** (tecla de aspas simples, geralmente abaixo do Esc)
* No Mac: aperte **`Control + '`**

### Passo 2: Baixar o projeto do GitHub
No terminal que abriu na parte inferior do VS Code, cole o comando abaixo e aperte **Enter**:
```bash
git clone [https://github.com/jpbianchese/robo-pesquisa-concorrente.git](https://github.com/jpbianchese/robo-pesquisa-concorrente.git)
```
E use Git pull quando for atualizar qunado necessário.

---
## 📚 Bibliotecas necessárias


(Isso aqui serve para criar a página de internet do seu robô)
  ```bash
  pip install flask
  ```

(Esse é o cara que vai abrir o Chrome e pesquisar nos sites sozinho)
  ```bash
  pip install selenium
  ```

(Essa biblioteca organiza todos os preços e informações na memória)
  ```bash
  pip install pandas
  ```

  (Esse aqui serve para o robô conseguir mexer e salvar tudo em formato do Excel)
  ```bash
  pip install openpyxl
  ```