import socket
import pickle
import numpy as np
import time

def enviar_receber(sock, dados):
    """Envia objeto serializado e aguarda resposta."""
    msg = pickle.dumps(dados)
    # Envia tamanho + dados
    sock.sendall(len(msg).to_bytes(4, 'big') + msg)
    
    # Recebe resposta
    len_bytes = sock.recv(4)
    if not len_bytes: return None
    resp_len = int.from_bytes(len_bytes, 'big')
    
    chunks = []
    bytes_recd = 0
    while bytes_recd < resp_len:
        chunk = sock.recv(min(resp_len - bytes_recd, 4096))
        chunks.append(chunk)
        bytes_recd += len(chunk)
        
    return pickle.loads(b''.join(chunks))

if __name__ == "__main__":
    N = 500
    STEPS = 30
    WORKERS_PORTS = [5000, 5001] # Assumindo 2 workers rodando
    
    # Inicializa grid
    grid = np.random.choice([0, 1], size=(N, N))
    
    # Conecta aos workers
    conexoes = []
    for port in WORKERS_PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', port))
            conexoes.append(s)
            print(f"Conectado ao worker na porta {port}")
        except:
            print(f"Não foi possível conectar na porta {port}. Rode o worker_socket.py primeiro.")
            exit()
            
    num_workers = len(conexoes)
    rows_per_worker = N // num_workers
    
    start_time = time.time()
    
    for s in range(STEPS):
        # Lista para armazenar os pedaços futuros
        novos_pedacos = [None] * num_workers
        
        # 1. Enviar fatias para os workers
        for i, conn in enumerate(conexoes):
            start_row = i * rows_per_worker
            end_row = N if i == num_workers - 1 else (i + 1) * rows_per_worker
            
            # Pega o pedaço principal
            slice_data = grid[start_row:end_row, :]
            
            # Adiciona Halo Rows (Linhas Fantasma)
            # Linha de cima: se for o primeiro bloco, cria linha de zeros, senão pega a linha anterior da grade
            row_above = np.zeros((1, N), dtype=int) if start_row == 0 else grid[start_row-1:start_row, :]
            
            # Linha de baixo: se for o último bloco, cria linha de zeros, senão pega a linha seguinte
            row_below = np.zeros((1, N), dtype=int) if end_row == N else grid[end_row:end_row+1, :]
            
            # Concatena: [Halo Cima, Dados, Halo Baixo]
            pacote = np.vstack([row_above, slice_data, row_below])
            
            # Envia para processamento (simulação simples: sequencial no envio, ideal seria Threads para envio assíncrono)
            # Aqui estamos enviando e esperando receber para simplificar a lógica do código
            resultado = enviar_receber(conn, pacote)
            novos_pedacos[i] = resultado
            
        # 2. Remontar a matriz
        grid = np.vstack(novos_pedacos)
        # print(f"Geração {s+1} Distribuída concluída.")

    print(f"Distribuído: Tempo total: {time.time() - start_time:.4f}s")
    
    # Fecha conexões
    for c in conexoes: c.close()