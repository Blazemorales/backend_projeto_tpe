import numpy as np
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path
from .Kalman import Kalman
def carta_x():
    print("--- Carta de Controle X com Média das Médias das Amostras ---\n")

    # --- Leitura dos dados do banco de dados ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    projeto_root = os.path.dirname(os.path.dirname(script_dir))
    pasta_banco_dados = os.path.join(projeto_root, 'backend_tpe', 'banco_de_dados_amostras')

    print(f"Procurando dados em: {pasta_banco_dados}\n")

    # Lista todos os arquivos JSON na pasta
    arquivos_json = sorted([f for f in os.listdir(pasta_banco_dados) if f.endswith('.json')])

    if not arquivos_json:
        print("Nenhum arquivo JSON encontrado na pasta de banco de dados!")
        print("Execute o programa de coleta de dados primeiro.")
        exit()

    print(f"Arquivos encontrados: {arquivos_json}")
    print("Processando dados com Filtro de Kalman aplicado ao conjunto global...\n")

    # Variáveis para armazenar dados
    medias_amostras = []
    nomes_amostras = []
    dados_brutos_amostras = []  # Para visualizar o efeito do Kalman
    dados_filtrados_amostras = []
    parametros_kalman = {'processo_var': 0.01, 'medida_var': 2.0}  # Ajustados para melhor filtragem

    kf = Kalman(processo_var=parametros_kalman['processo_var'], 
                medida_var=parametros_kalman['medida_var'], 
                estimativa_inicial=0, 
                erro_inicial=1)

    print(f"Parâmetros do Filtro de Kalman:")
    print(f"  - Variância do Processo (Q): {parametros_kalman['processo_var']}")
    print(f"  - Variância da Medida (R): {parametros_kalman['medida_var']}\n")

    # Primeiro, lê TODOS os dados brutos de TODAS as amostras
    todos_dados_brutos = []
    mapeamento_amostras = {}  # Para rastrear qual dado pertence a qual amostra

    for arquivo in arquivos_json:
        caminho_arquivo = os.path.join(pasta_banco_dados, arquivo)
        
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados_json = json.load(f)
        
        # Extrai os valores brutos
        valores_amostra = []
        for item in dados_json:
            if 'valor_bruto' in item:
                valor = item['valor_bruto']
                valores_amostra.append(valor)
                todos_dados_brutos.append(valor)
        
        # Mapeia quais índices pertencem a esta amostra
        inicio = len(todos_dados_brutos) - len(valores_amostra)
        mapeamento_amostras[arquivo.replace('.json', '')] = {
            'inicio': inicio,
            'fim': len(todos_dados_brutos),
            'tamanho': len(valores_amostra)
        }

    print(f"Total de dados coletados de todas as amostras: {len(todos_dados_brutos)}\n")

    # Aplica o Filtro de Kalman a TODO o conjunto de dados
    todos_dados_filtrados = []
    kf.resetar(todos_dados_brutos[0], 1)

    for valor in todos_dados_brutos:
        filtrado = kf.filtrar(valor)
        todos_dados_filtrados.append(filtrado)

    # Calcula a redução de ruído global
    ruido_original_global = np.std(todos_dados_brutos)
    ruido_filtrado_global = np.std(todos_dados_filtrados)
    percentual_reducao_global = ((ruido_original_global - ruido_filtrado_global) / ruido_original_global * 100) if ruido_original_global > 0 else 0

    print(f"Redução de Ruído Global:")
    print(f"  Desvio Padrão Bruto: {ruido_original_global:.4f}")
    print(f"  Desvio Padrão Filtrado: {ruido_filtrado_global:.4f}")
    print(f"  Redução Total: {percentual_reducao_global:.1f}%\n")

    # Agora, calcula a média de cada amostra USANDO os dados filtrados
    for nome_amostra, info in mapeamento_amostras.items():
        inicio = info['inicio']
        fim = info['fim']
        
        # Pega os valores filtrados desta amostra
        valores_filtrados_amostra = todos_dados_filtrados[inicio:fim]
        
        # Calcula a média
        media_amostra = np.mean(valores_filtrados_amostra)
        medias_amostras.append(media_amostra)
        nomes_amostras.append(nome_amostra)
        dados_brutos_amostras.append(todos_dados_brutos[inicio:fim])
        dados_filtrados_amostras.append(valores_filtrados_amostra)
        
        print(f"  {nome_amostra}: Média Filtrada = {media_amostra:.4f}, Valores = {len(valores_filtrados_amostra)}")

    print(f"\nTotal de amostras processadas: {len(medias_amostras)}\n")

    # --- Processamento da Carta de Controle X ---
    if len(medias_amostras) < 2:
        print("Erro: Necessário pelo menos 2 amostras para criar a Carta de Controle X!")
        exit()

    # Calcula a média das médias (X-barra-barra)
    media_das_medias = np.mean(medias_amostras)

    # Calcula o desvio padrão das médias das amostras
    desvio_padrao_medias = np.std(medias_amostras, ddof=1)  # ddof=1 para amostra

    # Cálculo dos limites de controle (3-sigma)
    lsc = media_das_medias + (3 * desvio_padrao_medias)
    lic = media_das_medias - (3 * desvio_padrao_medias)

    print(f"--- Estatísticas da Carta X ---")
    print(f"Média das Médias (X̄̄): {media_das_medias:.4f}")
    print(f"Desvio Padrão das Médias: {desvio_padrao_medias:.4f}")
    print(f"LSC (Limite Superior de Controle): {lsc:.4f}")
    print(f"LIC (Limite Inferior de Controle): {lic:.4f}\n")

    # --- Verificação de pontos fora de controle ---
    pontos_fora_controle = []
    for i, media in enumerate(medias_amostras):
        if media > lsc or media < lic:
            pontos_fora_controle.append({
                'nome': nomes_amostras[i],
                'valor': media
            })

    if pontos_fora_controle:
        print("⚠️  ALERTAS - Pontos fora de controle:")
        for item in pontos_fora_controle:
            print(f"  - {item['nome']}: {item['valor']:.4f}")
    else:
        print("✓ Processo sob controle estatístico!")

    # --- Plotagem ---
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # ===== GRÁFICO 1: Comparação Bruto vs Filtrado (Primeira Amostra) =====
    ax1 = axes[0]
    eixo_x_amostras = range(1, len(dados_brutos_amostras[0]) + 1)
    ax1.plot(eixo_x_amostras, dados_brutos_amostras[0], 'ro-', alpha=0.5, linewidth=1.5, markersize=5, label='Dados Brutos')
    ax1.plot(eixo_x_amostras, dados_filtrados_amostras[0], 'b-s', linewidth=2, markersize=5, label='Dados Filtrados (Kalman)')
    ax1.set_title(f"Efeito do Filtro de Kalman - {nomes_amostras[0]}")
    ax1.set_xlabel("Número do Dado")
    ax1.set_ylabel("Valor")
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # ===== GRÁFICO 2: Carta de Controle X =====
    ax2 = axes[1]
    eixo_x = range(1, len(medias_amostras) + 1)

    # Plota as médias das amostras
    ax2.plot(eixo_x, medias_amostras, 'bo-', linewidth=2, markersize=8, label='Média de cada Amostra')

    # Linhas da Carta de Controle
    ax2.axhline(media_das_medias, color='green', linewidth=2, label=f'Média das Médias: {media_das_medias:.4f}')
    ax2.axhline(lsc, color='red', linestyle='--', linewidth=2, label=f'LSC: {lsc:.4f}')
    ax2.axhline(lic, color='red', linestyle='--', linewidth=2, label=f'LIC: {lic:.4f}')

    # Destaca pontos fora de controle
    if pontos_fora_controle:
        indices_fora = [eixo_x[nomes_amostras.index(amostra)] for amostra, _ in pontos_fora_controle]
        valores_fora = [valor for _, valor in pontos_fora_controle]
        ax2.plot(indices_fora, valores_fora, 'r*', markersize=15, label='Fora de Controle')

    ax2.set_title("Carta de Controle X - Média das Médias das Amostras")
    ax2.set_xlabel("Amostra")
    ax2.set_ylabel("Média")
    ax2.set_xticks(eixo_x)
    ax2.set_xticklabels(nomes_amostras, rotation=45)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # --- Salvar resultados em JSON (ANTES de mostrar o gráfico) ---
    pasta_resultados_x = os.path.join(projeto_root, 'app', 'banco_de_dados_X')

    # Cria a pasta se não existir
    if not os.path.exists(pasta_resultados_x):
        os.makedirs(pasta_resultados_x)
        print(f"✓ Pasta '{pasta_resultados_x}' criada com sucesso.")

    # Prepara dados das amostras com suas médias
    dados_amostras = [
        {
            'nome': nomes_amostras[i],
            'media_filtrada': round(medias_amostras[i], 4),
            'quantidade_valores': len(dados_brutos_amostras[i])
        }
        for i in range(len(nomes_amostras))
    ]

    # Monta o JSON com todos os dados
    serie_primeira_amostra = {
        'nome': nomes_amostras[0],
        'dados_brutos': dados_brutos_amostras[0],
        'dados_filtrados': dados_filtrados_amostras[0],
    }

    resultado_json = {
        'analise_carta_controle_x': {
            'media_das_medias': round(media_das_medias, 4),
            'desvio_padrao_medias': round(desvio_padrao_medias, 4),
            'lsc': round(lsc, 4),
            'lic': round(lic, 4),
            'processo_sob_controle': len(pontos_fora_controle) == 0,
            'pontos_fora_controle': pontos_fora_controle,
        },
        'parametros_kalman': parametros_kalman,
        'amostras': dados_amostras,
        'nomes_amostras': nomes_amostras,
        'medias_amostras': [round(valor, 4) for valor in medias_amostras],
        'serie_primeira_amostra': serie_primeira_amostra,
        'resumo_filtragem': {
            'desvio_padrao_bruto': round(ruido_original_global, 4),
            'desvio_padrao_filtrado': round(ruido_filtrado_global, 4),
            'percentual_reducao_ruido': round(percentual_reducao_global, 2)
        }
    }

    # Salva o arquivo
    caminho_json = os.path.join(pasta_resultados_x, 'Carta_x.json')
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(resultado_json, f, indent=4, ensure_ascii=False)

    print(f"\n✓ Resultados salvos em: {caminho_json}")

    print("\nGerando gráficos...")
    plt.show()
