import numpy as np
import threading
import time

# mesma func de contar_vizinhos
def contar_vizinhos(grid, x, y, N):
    total = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0: continue
            ni, nj = x + i, y + j
            if 0 <= ni < N and 0 <= nj < N:
                total += grid[ni][nj]
    return total

# vars globais 
N = 500
NUM_THREADS = 10
STEPS = 80
grid = np.random.choice([0, 1], size=(N, N))
novo_grid = np.zeros((N, N), dtype=int)

# barreira para sincronizar as threads ao fim de cada gen
# esperar NUM_THREADS + 1 pq main thread tbm espera pra trocar os ponteiros
barrier = threading.Barrier(NUM_THREADS + 1)

def worker(thread_id, start_row, end_row):
    """Função executada por cada thread."""
    global grid, novo_grid
    
    for s in range(STEPS):
        # processa fatia da matriz
        for i in range(start_row, end_row):
            for j in range(N):
                vivos = contar_vizinhos(grid, i, j, N)
                if grid[i][j] == 1:
                    novo_grid[i][j] = 1 if 2 <= vivos <= 3 else 0
                else:
                    novo_grid[i][j] = 1 if vivos == 3 else 0
        
        # espera outras threads e a main terminar o calc
        barrier.wait() 
        # main  troca grid = novo_grid
        # espera a main liberar para prox gen
        barrier.wait()

if __name__ == "__main__":
    threads = []
    rows_per_thread = N // NUM_THREADS
    
    start_time = time.time()
    
    # cria e init threads
    for t in range(NUM_THREADS):
        start_row = t * rows_per_thread
        # ultima thread pega as linhas restantes caso tenha resto na div
        end_row = N if t == NUM_THREADS - 1 else (t + 1) * rows_per_thread
        
        th = threading.Thread(target=worker, args=(t, start_row, end_row))
        th.start()
        threads.append(th)
    
    # loop thread principal
    for s in range(STEPS):
        # espera workers terminarem o calc da gen atual
        barrier.wait()
        
        # atualiza a matriz para prox iterr
        grid = np.copy(novo_grid)
        
        # libera workers para prox iterr
        barrier.wait()
        
    for th in threads:
        th.join()

    print(f"Paralelo (Threads): Tempo total: {time.time() - start_time:.4f}s")