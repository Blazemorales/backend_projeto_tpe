import json
import math
import os
import scipy.stats

class DataProcessor:
    def __init__(self):
        self.datasets = []

    def carregar_dados(self, nome_arquivo):
        # Ajustando para o caminho: ../amostras/banco_de_dados_amostras/
        caminho_diretorio = os.path.join(os.path.dirname(__file__), 'banco_de_dados_amostras')
        caminho_completo = os.path.join(caminho_diretorio, nome_arquivo)
        
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                conteudo = json.load(f)
                # Garante que datasets seja uma lista (mesmo que o JSON seja um único objeto)
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

        for id_amostra, valores in measurements.items():
            if valores:
                media_amostra = sum(valores) / len(valores)
                amplitude_amostra = max(valores) - min(valores)
                
                # DP da amostra
                n_amostra = len(valores)
                soma_quad = sum((x - media_amostra) ** 2 for x in valores)
                dp_amostra = math.sqrt(soma_quad / n_amostra)

                estatisticas_por_amostra.append({
                    "amostra": id_amostra,
                    "media": media_amostra,
                    "dp": dp_amostra,
                    "amplitude": amplitude_amostra
                })

                # ALIMENTANDO AS LISTAS GLOBAIS (Faltava isso!)
                todas_as_medias.append(media_amostra)
                amplitudes.append(amplitude_amostra)
                todos_os_valores.extend(valores)

        if not todos_os_valores:
            print("Nenhum dado encontrado.")
            return

        # SALVANDO NO DIRETÓRIO: ../banco_de_dados
        pasta_saida = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'banco_de_dados')
        if not os.path.exists(pasta_saida):
            os.makedirs(pasta_saida)
        
        caminho_saida = os.path.join(pasta_saida, 'estatisticas_individuais.json')
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(estatisticas_por_amostra, f, indent=4)
        print(f"Estatísticas salvas em: {caminho_saida}")

        # Cálculos Globais
        x_double_bar = sum(todas_as_medias) / len(todas_as_medias)
        r_bar = sum(amplitudes) / len(amplitudes)
        sigma = math.sqrt(sum((x - x_double_bar) ** 2 for x in todos_os_valores) / len(todos_os_valores))

        # Probabilidade
        try:
            value_input = input("\nValor para verificar probabilidade (ex: 530): ")
            value = float(value_input)
            z = (value - x_double_bar) / sigma # Parênteses corrigidos
            
            from scipy.stats import norm
            probabilidade = norm.cdf(z)
            prob = probabilidade * 100
            print(f"Probabilidade de valor <= {value}: {prob:.4f}")
        except (ImportError, ValueError):
            print("Pulei o cálculo de probabilidade (scipy não instalado ou valor inválido).")

        print(f"\n--- RESULTADOS GERAIS ---")
        print(f"X̄̄: {x_double_bar:.4f} | R̄: {r_bar:.4f} | σ Global: {sigma:.4f}")
        
        if lse != lie:
            cp = (lse - lie) / (6 * sigma) if sigma != 0 else 0
            print(f"Cp Estimado: {cp:.4f}")

    def menu_interativo(self):
        while True:
            print("\n--- PROCESSADOR DE DADOS ---")
            opcao = input("Nome do arquivo JSON (ex: dados_producao.json) ou 'sair': ").strip()
            if opcao.lower() == 'sair': break
            
            if self.carregar_dados(opcao):
                self.calcular_estatisticas(0)

if __name__ == "__main__":
    DataProcessor().menu_interativo()