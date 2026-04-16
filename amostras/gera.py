import json
import os
import random

def gerar_dados_teste(quantidade_amostras=5, medidas_por_amostra=10):
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_destino = os.path.join(diretorio_atual, 'banco_de_dados_amostras')

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Vamos criar um único arquivo JSON que contém várias amostras, 
    # simulando o objeto que estava no quadro.
    dados_processo = {
        "Chart": "XR",
        "measurements": {},
        "Limite sup. Esp": 550,
        "Limite inf. Esp": 530
    }

    for i in range(1, quantidade_amostras + 1):
        # Gera valores aleatórios próximos à média 540
        valores = [round(random.uniform(535, 545), 2) for _ in range(medidas_por_amostra)]
        
        # Adiciona ao dicionário de medições usando o ID da amostra como chave
        dados_processo["measurements"][str(i)] = valores

    # Salva o arquivo final
    caminho_completo = os.path.join(pasta_destino, 'dados_producao.json')
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        json.dump(dados_processo, f, indent=4, ensure_ascii=False)
            
    print(f"Sucesso! Arquivo gerado em: {caminho_completo}")

if __name__ == "__main__":
    gerar_dados_teste()