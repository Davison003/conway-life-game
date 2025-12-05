import numpy as np
import time

def contar_vizinhos(grid, x, y, N):
    """Conta os vizinhos vivos (1) ao redor da coord x,y."""
    total = 0
    # vai de -1 a +1 nas linhas e colunas
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0: continue # pula a propria celula
            
            # ni e nj sao os indices absolutos computados dos vizinhos
            ni, nj = x + i, y + j
            
            # checa se vizinho ta dentro dos limites da grade
            if 0 <= ni < N and 0 <= nj < N:
                total += grid[ni][nj]
    return total

def passo_simulacao(grid, N):
    """Gera a nova matriz baseada nas regras."""
    novo_grid = np.zeros((N, N), dtype=int)
    
    for i in range(N):
        for j in range(N):
            vivos = contar_vizinhos(grid, i, j, N)
            
            # regras jogo da vida
            if grid[i][j] == 1:
                if vivos < 2 or vivos > 3:
                    novo_grid[i][j] = 0 # solidao ou superpopulacao
                else:
                    novo_grid[i][j] = 1 # sobrevive
            else:
                if vivos == 3:
                    novo_grid[i][j] = 1 # reproducao
                    
    return novo_grid

# exec principal
if __name__ == "__main__":
    N = 100  # tamanho da grade
    steps = 50 # num de gens
    
    # init grid random
    grid = np.random.choice([0, 1], size=(N, N))

    start = time.time()
    for s in range(steps):
        grid = passo_simulacao(grid, N)
    
    end = time.time()
    print(f"Sequencial: Tempo total para {steps} gerações com grade {N}x{N}: {end - start:.4f}s")