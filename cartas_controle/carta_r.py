import numpy as np
import matplotlib.pyplot as plt

#calibragem
class Kalman:
    def __init__(self, processo_var, medida_var, estimativa_inicial, erro_inicial):
        self.__Q = processo_var  
        self.__R = medida_var    
        self.__x = estimativa_inicial
        self.__P = erro_inicial

    def filtrar(self, medida):
        # 1. Predição
        self.__P = self.__P + self.__Q
        # 2. Atualização
        K = self.__P / (self.__P + self.__R)
        self.__x = self.__x + K * (medida - self.__x)
        self.__P = (1 - K) * self.__P
        return self.__x

print("--- Configuração do Filtro de Kalman ---")

kf = Kalman(processo_var=0.001, medida_var=5, estimativa_inicial=0, erro_inicial=1)

dados_brutos = []
dados_filtrados = []

print("\nDigite os valores numéricos. Digite 'stop' para encerrar e gerar o gráfico.")

# Loop para recebimento de dados, que inclui o algoritmo de Kalman, para filtrar
while True:
    entrada = input(f"Valor #{len(dados_brutos) + 1}: ").strip().lower()
    
    if entrada == 'stop':
        if len(dados_brutos) < 2:
            print("Insira pelo menos 2 valores para gerar a carta.")
            continue
        break
    
    try:
        valor = float(entrada)
        # Se for o primeiro valor, ajustamos a estimativa inicial do filtro para ele
        if len(dados_brutos) == 0:
            kf.x = valor
            
        filtrado = kf.filtrar(valor)
        
        dados_brutos.append(valor)
        dados_filtrados.append(filtrado)
        print(f"  -> Valor Filtrado: {filtrado:.2f}")
        
    except ValueError:
        print("Por favor, digite um número válido ou 'sair'.")

# --- Processamento da Carta de Controle ---
media_central = np.mean(dados_filtrados)
sigma = np.std(dados_filtrados)

lsc = media_central + (3 * sigma)
lic = media_central - (3 * sigma)

# --- Plotagem ---
plt.figure(figsize=(10, 6))
eixo_x = range(1, len(dados_brutos) + 1)

plt.plot(eixo_x, dados_brutos, 'ro-', alpha=0.4, label='Entrada Usuário (Ruidoso)')
plt.plot(eixo_x, dados_filtrados, 'b-s', linewidth=2, label='Filtro de Kalman')

# Linhas da Carta de Controle
plt.axhline(media_central, color='green', label=f'Média: {media_central:.2f}')
plt.axhline(lsc, color='red', linestyle='--', label=f'LSC (Limite Superior): {lsc:.2f}')
plt.axhline(lic, color='red', linestyle='--', label=f'LIC (Limite Inferior): {lic:.2f}')

plt.title("Carta de Controle X usando Kalman e a tabela de distribuição normal")
plt.xlabel("Quantidade de dados obtidos")
plt.ylabel("Dados obtidos")
plt.legend()
plt.grid(True, alpha=0.3)

print("\nGerando gráfico...")
plt.show()