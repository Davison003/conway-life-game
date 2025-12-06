import socket
import pickle
import numpy as np

def contar_vizinhos(grid, x, y, cols):
    # logica similar, mas x eh relativo a sub-grade recebida
    rows = len(grid)
    total = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0: continue
            ni, nj = x + i, y + j
            if 0 <= ni < rows and 0 <= nj < cols:
                total += grid[ni][nj]
    return total

def processar_pedaco(sub_grid_com_halo):
    """
    Recebe uma matriz que inclui a linha superior e inferior extra (halos).
    Deve processar apenas o miolo, ignorando a primeira e última linha na escrita.
    """
    rows = len(sub_grid_com_halo)
    cols = len(sub_grid_com_halo[0])
    # resultado sem as linhas de halo
    resultado = [] 
    
    # comeca do 1 e vai ate rows-1 para nao processar os halos (que servem pra leitura)
    for i in range(1, rows - 1):
        nova_linha = []
        for j in range(cols):
            vivos = contar_vizinhos(sub_grid_com_halo, i, j, cols)
            estado_atual = sub_grid_com_halo[i][j]
            
            novo_estado = 0
            if estado_atual == 1:
                if vivos == 2 or vivos == 3: novo_estado = 1
            else:
                if vivos == 3: novo_estado = 1
            nova_linha.append(novo_estado)
        resultado.append(nova_linha)
    
    return np.array(resultado)

def start_worker(port):
    # AF_INET - endereco IPv4.
    # SOCK_STREAM - tipo socket TCP.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', port))
    server.listen(1)
    print(f"Worker ouvindo na porta {port}...")
    
    # aceita conexao do cliente (master)
    conn, addr = server.accept()
    print(f"Conectado ao Mestre: {addr}")
    
    while True:
        try:
            # recebe dados (tamanho primeiro, depois payload)
            # protocolo simples -> 4 bytes int indicando tamanho
            data_len_bytes = conn.recv(4)
            if not data_len_bytes: break
            data_len = int.from_bytes(data_len_bytes, 'big')
            
            chunks = []
            bytes_recd = 0
            while bytes_recd < data_len:
                chunk = conn.recv(min(data_len - bytes_recd, 4096))
                if not chunk: break
                chunks.append(chunk)
                bytes_recd += len(chunk)
            
            data = b''.join(chunks)
            sub_grid = pickle.loads(data)
            
            # processa
            novo_pedaco = processar_pedaco(sub_grid)
            
            # envia resposta
            resp_data = pickle.dumps(novo_pedaco)
            conn.sendall(len(resp_data).to_bytes(4, 'big') + resp_data)
            
        except Exception as e:
            print(f"Erro ou conexão fechada: {e}")
            break
    conn.close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    start_worker(port)