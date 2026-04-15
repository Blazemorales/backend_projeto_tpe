import json
import numpy as np
import os

def gerar_dados_aleatorios():
    """
    Gera dados aleatórios realistas simulando um processo industrial
    com variações controladas
    """
    
    # Configurações
    num_amostras = 10
    tamanho_amostra = 10
    media_processo = 50.0  # Média central do processo
    desvio_padrao = 3.0    # Variação do processo
    
    # Pasta de destino
    script_dir = os.path.dirname(os.path.abspath(__file__))
    projeto_root = os.path.dirname(os.path.dirname(script_dir))
    pasta_destino = os.path.join(projeto_root, 'app', 'banco_de_dados_amostras')
    
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    print("=" * 60)
    print("Gerador de Dados Aleatórios para Carta de Controle X")
    print("=" * 60)
    print(f"\nConfigurações:")
    print(f"  - Número de amostras: {num_amostras}")
    print(f"  - Tamanho de cada amostra: {tamanho_amostra}")
    print(f"  - Média do processo: {media_processo:.2f}")
    print(f"  - Desvio padrão: {desvio_padrao:.2f}")
    print(f"  - Pasta de destino: {pasta_destino}\n")
    
    # Gera as amostras
    for num_amostra in range(1, num_amostras + 1):
        # Gera dados com distribuição normal
        dados = np.random.normal(media_processo, desvio_padrao, tamanho_amostra)
        
        # Converte para lista de dicionários no formato esperado
        historico = [
            {
                "id": i + 1,
                "valor_bruto": float(valor)
            }
            for i, valor in enumerate(dados)
        ]
        
        # Calcula estatísticas dessa amostra
        media_amostra = np.mean(dados)
        desvio_amostra = np.std(dados)
        
        # Adiciona estatísticas ao final
        historico.append({
            "media": round(float(media_amostra), 4),
            "desvio_padrao": round(float(desvio_amostra), 4)
        })
        
        # Salva o arquivo
        nome_arquivo = f"amostra_{num_amostra}.json"
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
        
        print(f"✓ {nome_arquivo}")
        print(f"    Média: {media_amostra:.4f}")
        print(f"    Desvio Padrão: {desvio_amostra:.4f}")
        print(f"    Valores: {[f'{v:.2f}' for v in dados]}\n")
    
    # Calcula estatísticas globais
    todas_amostras_medias = []
    for num_amostra in range(1, num_amostras + 1):
        nome_arquivo = f"amostra_{num_amostra}.json"
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            media = [item for item in data if 'media' in item and 'id' not in item]
            if media:
                todas_amostras_medias.append(media[0]['media'])
    
    media_das_medias = np.mean(todas_amostras_medias)
    desvio_das_medias = np.std(todas_amostras_medias)
    
    print("=" * 60)
    print("Resumo Global:")
    print(f"  - Média das Médias: {media_das_medias:.4f}")
    print(f"  - Desvio Padrão das Médias: {desvio_das_medias:.4f}")
    print(f"  - LSC (Limite Superior): {media_das_medias + 3*desvio_das_medias:.4f}")
    print(f"  - LIC (Limite Inferior): {media_das_medias - 3*desvio_das_medias:.4f}")
    print("=" * 60)
    print("\n✅ Dados aleatórios gerados com sucesso!")
    print(f"   Localizados em: {pasta_destino}")

if __name__ == "__main__":
    gerar_dados_aleatorios()
