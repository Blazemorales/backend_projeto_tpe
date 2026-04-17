import json
import math
import os
import scipy.stats
from scipy.stats import norm # Importação movida para o topo
import calculod3

class DataProcessor:
    def __init__(self):
        self.datasets = []

    def carregar_dados(self, nome_arquivo):
        # Ajustado para procurar na pasta 'banco_de_dados_amostras'
        caminho_diretorio = os.path.join(os.path.dirname(__file__), 'banco_de_dados_amostras')
        caminho_completo = os.path.join(caminho_diretorio, nome_arquivo)
        
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                conteudo = json.load(f)
                self.datasets = conteudo if isinstance(conteudo, list) else [conteudo]
            return True
        except Exception as e:
            print(f"Erro ao carregar {nome_arquivo}: {e}")
            return False

    def calcular_estatisticas(self, index):
        ds = self.datasets[index]
        measurements = ds.get("measurements", {})
        lse = ds.get("Limite sup. Esp", 0)
        lie = ds.get("Limite inf. Esp", 0)

        todas_as_medias = []
        amplitudes = []
        todos_os_valores = []
        estatisticas_por_amostra = []
        n_amostra = 0

        for id_amostra, valores in measurements.items():
            if valores:
                n_amostra = len(valores) # Define n com base nos dados reais
                media_amostra = sum(valores) / n_amostra
                amplitude_amostra = max(valores) - min(valores)
                
                soma_quad = sum((x - media_amostra) ** 2 for x in valores)
                dp_amostra = math.sqrt(soma_quad / n_amostra)

                estatisticas_por_amostra.append({
                    "amostra": id_amostra,
                    "media": media_amostra,
                    "dp": dp_amostra,
                    "amplitude": amplitude_amostra
                })

                todas_as_medias.append(media_amostra)
                amplitudes.append(amplitude_amostra)
                todos_os_valores.extend(valores)

        if not todos_os_valores:
            print("Nenhum dado encontrado.")
            return

        # Salvando os resultados individuais
        pasta_saida = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'banco_de_dados')
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)
        
        caminho_saida = os.path.join(pasta_saida, 'estatisticas_individuais.json')
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(estatisticas_por_amostra, f, indent=4)
        print(f"Estatísticas individuais salvas em: {caminho_saida}")

        # Cálculos Globais
        x_double_bar = sum(todas_as_medias) / len(todas_as_medias)
        r_bar = sum(amplitudes) / len(amplitudes)
        # Sigma global (desvio padrão populacional dos dados coletados)
        sigma = math.sqrt(sum((x - x_double_bar) ** 2 for x in todos_os_valores) / len(todos_os_valores))

        # Determinação de d2
        match n_amostra:
            case 2: d2 = 1.128
            case 3: d2 = 1.693
            case 4: d2 = 2.059
            case 5: d2 = 2.326
            case 6: d2 = 2.534
            case 7: d2 = 2.704
            case 8: d2 = 2.847
            case 9: d2 = 2.970
            case 10: d2 = 3.078
            case _: d2 = (n_amostra / (n_amostra - 0.8)) * math.sqrt(math.log(n_amostra))
        
        # Chama sua função externa para d3
        d3 = calculod3.obter_d3(n_amostra)

        # CORREÇÃO: Faltava o operador '*' e a lógica de truncamento para LIC
        lsc_r = r_bar * (1 + 3 * (d3 / d2)) if d2 != 0 else 0
        lic_r = max(0, r_bar * (1 - 3 * (d3 / d2))) if d2 != 0 else 0

        # Probabilidade
        try:
            value_input = input("\nValor para verificar probabilidade (ex: 530): ")
            if value_input:
                value = float(value_input)
                z = (value - x_double_bar) / sigma if sigma != 0 else 0
                prob = norm.cdf(z) * 100
                print(f"Probabilidade de valor <= {value}: {prob:.4f}%")
        except ValueError:
            print("Valor inválido para cálculo de probabilidade.")

        print(f"\n--- RESULTADOS GERAIS ---")
        print(f"X̄̄ (Média das Médias): {x_double_bar:.4f}")
        print(f"R̄ (Média das Amplitudes): {r_bar:.4f}")
        print(f"σ Global: {sigma:.4f}")
        print(f"Limites de Controle para R: [LIC: {lic_r:.4f}, LSC: {lsc_r:.4f}]")
        
        if lse != lie:
            cp = (lse - lie) / (6 * sigma) if sigma != 0 else 0
            print(f"Cp (Capacidade do Processo): {cp:.4f}")

    def menu_interativo(self):
        while True:
            print("\n--- PROCESSADOR DE DADOS ---")
            opcao = input("Nome do arquivo JSON (ou 'sair'): ").strip()
            if opcao.lower() == 'sair': break
            
            if self.carregar_dados(opcao):
                self.calcular_estatisticas(0)

if __name__ == "__main__":
    DataProcessor().menu_interativo()