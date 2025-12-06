import socket
import pickle
import numpy as np
import time
import argparse

def enviar_receber(sock, dados):
    """Envia objeto serializado e aguarda resposta."""
    msg = pickle.dumps(dados)
    # envia tamanho + dados
    sock.sendall(len(msg).to_bytes(4, 'big') + msg)
    
    # recebe resposta
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
    parser = argparse.ArgumentParser(description="Conway's Game of Life - Distributed Master")
    parser.add_argument('--N', type=int, default=200, help='Grid size (NxN)')
    parser.add_argument('--steps', type=int, default=10, help='Number of generations')
    parser.add_argument('--num-workers', type=int, default=1, help='Number of workers')
    args = parser.parse_args()

    N = args.N
    STEPS = args.steps
    num_workers = args.num_workers
    
    # gera portas automaticamente comecando de 5000
    WORKERS_PORTS = [5000 + i for i in range(num_workers)]
    
    # inicializa grid
    grid = np.random.choice([0, 1], size=(N, N))
    
    # conecta workers
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
            
    rows_per_worker = N // num_workers
    
    start_time = time.time()
    
    for s in range(STEPS):
        # lista para armazenar os pedaços futuros
        novos_pedacos = [None] * num_workers
        
        # enviar fatias para os workers
        for i, conn in enumerate(conexoes):
            start_row = i * rows_per_worker
            end_row = N if i == num_workers - 1 else (i + 1) * rows_per_worker
            
            # pega o pedaço principal
            slice_data = grid[start_row:end_row, :]
            
            # adiciona Halo Rows (Linhas Fantasma)
            # linha cima: se for o primeiro bloco, cria linha de zeros, senao pega a linha anterior da grade
            row_above = np.zeros((1, N), dtype=int) if start_row == 0 else grid[start_row-1:start_row, :]
            
            # linha baixo: se for o ultimo bloco, cria linha de zeros, senao pega a linha seguinte
            row_below = np.zeros((1, N), dtype=int) if end_row == N else grid[end_row:end_row+1, :]
            
            # concatena: [Halo Cima, Dados, Halo Baixo]
            pacote = np.vstack([row_above, slice_data, row_below])
            
            # envia para processamento (simulação simples: sequencial no envio, ideal seria Threads para envio assíncrono)
            #  enviando e esperando receber para simplificar a lógica do código
            resultado = enviar_receber(conn, pacote)
            novos_pedacos[i] = resultado
            
        # remonta matriz
        grid = np.vstack(novos_pedacos)

    print(f"Distribuído: Tempo total para {STEPS} gerações com grade {N}x{N} com {num_workers} workers: {time.time() - start_time:.4f}s")
    
    # fecha conexoes
    for c in conexoes: c.close()