# Conway's Game of Life

Implementações do **Jogo da Vida de Conway** utilizando diferentes abordagens de computação: **Sequencial**, **Paralela** e **Distribuída**.


## 🛠️ Ferramentas Utilizadas

O projeto foi desenvolvido em **Python** e utiliza as seguintes bibliotecas:

*   **Numpy**: Para manipulação eficiente de matrizes (grids).
*   **Threading**: Para implementação da versão paralela com memória compartilhada.
*   **Socket**: Para comunicação via rede na versão distribuída (TCP).
*   **Pickle**: Para serialização de dados (envio de objetos Python via socket).
*   **Time**: Para medição de desempenho.

## 📂 Implementações

### 1. Sequencial (`conway-seq.py`)
A versão clássica e mais simples. O algoritmo itera sobre cada célula da grade, conta seus vizinhos e aplica as regras do jogo para gerar o estado da próxima geração. Todo o processamento ocorre em um único núcleo da CPU.

### 2. Paralela (`conway-para.py`)
Esta versão utiliza **Threads** para dividir o trabalho. A grade é fatiada horizontalmente, e cada thread é responsável por calcular a próxima geração de um conjunto de linhas.
*   Utiliza `threading.Barrier` para sincronizar as threads ao final de cada geração, garantindo que todas terminem antes de atualizar a grade principal.

### 3. Distribuída (`conway-dist/`)
Implementação baseada na arquitetura **Mestre-Escravo (Master-Worker)** utilizando **Sockets**.
*   **Mestre (`master-socket.py`)**: Gerencia a grade principal, divide o trabalho e envia fatias da matriz para os workers. Ele também lida com as "Halo Rows" (linhas de fronteira) para garantir que os workers tenham os dados vizinhos necessários para o cálculo.
*   **Worker (`worker-socket.py`)**: Recebe um pedaço da matriz, processa a próxima geração e retorna o resultado para o mestre.

---

## Execução

Certifique-se de ter o Python instalado e a biblioteca `numpy`:

```bash
pip install numpy
```

### Executando a Versão Sequencial

```bash
python conway-seq.py
```

### Executando a Versão Paralela

```bash
python conway-para.py
```
*Você pode ajustar o número de threads, gerações e o tamanho da grade editando as variáveis `NUM_THREADS`, `STEPS` e `N` nos arquivos.*

### Executando a Versão Distribuída

A versão distribuída requer que você inicie os **Workers** primeiro e depois o **Mestre**.

1.  **Inicie os Workers** (em terminais separados):
    ```bash
    # Terminal 1 (Worker na porta 5000)
    python conway-dist/worker-socket.py 5000

    # Terminal 2 (Worker na porta 5001)
    python conway-dist/worker-socket.py 5001
    ```

2.  **Inicie o Mestre** (em outro terminal):
    ```bash
    python conway-dist/master-socket.py
    ```

*O mestre tentará se conectar aos workers nas portas definidas (padrão 5000 e 5001). Se quiser adicionar mais workers, edite a lista `WORKERS_PORTS` no arquivo `master-socket.py`.*
