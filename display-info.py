import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Carregar e limpar os dados
file_path = 'time-algos.csv'
# Lê o CSV lidando com decimais em vírgula
try:
    df = pd.read_csv(file_path, decimal=',')
except:
    df = pd.read_csv(file_path) # Fallback

# Remove coluna de índice se existir
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

# Preenche valores sequenciais faltantes (propagando a média para o mesmo N e steps)
df['sequencial'] = df.groupby(['N', 'steps'])['sequencial'].transform(lambda x: x.fillna(x.mean()))

# Configura estilo dos gráficos
sns.set(style="whitegrid")

# --- GRÁFICO 1: Comparação Geral (Barplot) ---
# Transformar dados para formato longo para facilitar plotagem com Seaborn
df_melted = df.melt(id_vars=['N', 'steps', 'threads', 'sockets'], 
                    value_vars=['sequencial', 'paralelo', 'distribuido'],
                    var_name='Abordagem', value_name='Tempo (s)')

plt.figure(figsize=(12, 6))
# Usamos escala logarítmica porque a diferença entre N=200 e N=2000 é enorme
sns.barplot(x='N', y='Tempo (s)', hue='Abordagem', data=df_melted, errorbar=None)
plt.title('Comparação de Tempo de Execução por Tamanho da Grade (N)')
plt.ylabel('Tempo (segundos) - Escala Log')
plt.xlabel('Tamanho da Grade (NxN)')
# plt.yscale('log')
plt.show()

# --- GRÁFICO 2: Escalabilidade para o Maior Caso (Linhas) ---
# Focamos no maior N para ver onde a paralelização faz diferença
max_n = df['N'].max()
df_max_n = df[df['N'] == max_n].sort_values(by='threads')

plt.figure(figsize=(10, 6))
plt.plot(df_max_n['threads'], df_max_n['sequencial'], label='Sequencial', linestyle='--', color='blue')
plt.plot(df_max_n['threads'], df_max_n['paralelo'], label='Paralelo', marker='o', color='orange')
plt.plot(df_max_n['sockets'], df_max_n['distribuido'], label='Distribuído', marker='x', color='green')

plt.title(f'Escalabilidade para Grade N={max_n} (Threads/Sockets variando)')
plt.xlabel('Número de Threads / Sockets')
plt.ylabel('Tempo (segundos)')
plt.legend()
plt.grid(True)
plt.show()

# --- GRÁFICO 3: Speedup (Opcional) ---
# Speedup = Tempo Sequencial / Tempo da Abordagem
df_max_n['speedup_paralelo'] = df_max_n['sequencial'] / df_max_n['paralelo']
df_max_n['speedup_distribuido'] = df_max_n['sequencial'] / df_max_n['distribuido']

plt.figure(figsize=(10, 6))
plt.plot(df_max_n['threads'], df_max_n['speedup_paralelo'], label='Speedup Paralelo', marker='o')
plt.plot(df_max_n['sockets'], df_max_n['speedup_distribuido'], label='Speedup Distribuído', marker='x')
plt.axhline(y=1, color='red', linestyle='--', label='Baseline Sequencial (1.0)')

plt.title(f'Speedup para Grade N={max_n}')
plt.xlabel('Número de Threads / Sockets')
plt.ylabel('Speedup (Maior é melhor)')
plt.legend()
plt.grid(True)
plt.show()