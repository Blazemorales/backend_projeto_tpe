import numpy as np
import matplotlib.pyplot as plt
import json
import os
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg') # Define o backend para gerar arquivos sem precisar de interface gráfica
import matplotlib.pyplot as plt

def carta_x():
    print("--- Gerando Relatório PDF e Carta de Controle ---\n")

    # --- Configuração de Caminhos ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_base = os.path.join(os.path.dirname(script_dir), 'banco_de_dados')
    caminho_destino = os.path.join(os.path.dirname(script_dir), 'relatorios')

    # Garante que a pasta de relatórios existe
    if not os.path.exists(caminho_destino):
        os.makedirs(caminho_destino)
        print(f"✓ Pasta criada: {caminho_destino}")

    # Busca o arquivo de estatísticas
    arquivos_alvo = ['estatisticas_individuais.json', 'estatisticas.json']
    caminho_estatisticas = next((os.path.join(caminho_base, f) for f in arquivos_alvo 
                               if os.path.exists(os.path.join(caminho_base, f))), None)

    if not caminho_estatisticas:
        print(f"Erro: Nenhum arquivo encontrado em {caminho_base}.")
        return

    # --- Leitura dos Dados ---
    with open(caminho_estatisticas, 'r', encoding='utf-8') as f:
        dados_processados = json.load(f)

    nomes_amostras = [str(item['amostra']) for item in dados_processados]
    medias_amostras = [item.get('media', item.get('media da amostra')) for item in dados_processados]

    # --- Cálculos da Carta X ---
    media_das_medias = np.mean(medias_amostras)
    desvio_padrao_medias = np.std(medias_amostras, ddof=1)
    lsc = media_das_medias + (3 * desvio_padrao_medias)
    lic = media_das_medias - (3 * desvio_padrao_medias)

    # --- Geração do Gráfico ---
    plt.figure(figsize=(10, 5))
    eixo_x = range(1, len(medias_amostras) + 1)
    plt.plot(eixo_x, medias_amostras, 'bo-', linewidth=2, label='Média das Amostras')
    plt.axhline(media_das_medias, color='green', label=f'X̄̄: {media_das_medias:.2f}')
    plt.axhline(lsc, color='red', linestyle='--', label=f'LSC: {lsc:.2f}')
    plt.axhline(lic, color='red', linestyle='--', label=f'LIC: {lic:.2f}')
    
    plt.title("Carta de Controle X - Monitoramento de Amostras")
    plt.xlabel("Amostras")
    plt.ylabel("Valores Médios")
    plt.xticks(eixo_x, nomes_amostras)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    temp_img = os.path.join(caminho_destino, "temp_chart.png")
    plt.savefig(temp_img, bbox_inches='tight', dpi=100)
    plt.close()

    # --- Geração do PDF ---
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(190, 10, "Relatório de Qualidade - Processo de Produção", ln=True, align='C')
    pdf.ln(10)
    
    # Resumo Estatístico
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(190, 8, "Resumo Estatístico:", ln=True)
    pdf.set_font("helvetica", '', 11)
    pdf.cell(190, 7, f"Média das Médias (Xbb): {media_das_medias:.4f}", ln=True)
    pdf.cell(190, 7, f"Limite Superior de Controle (LSC): {lsc:.4f}", ln=True)
    pdf.cell(190, 7, f"Limite Inferior de Controle (LIC): {lic:.4f}", ln=True)
    pdf.ln(5)

    # Gráfico
    pdf.image(temp_img, x=15, w=170)
    pdf.ln(5)
    
    # Tabela de Amostras
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(40, 8, "ID Amostra", 1, align='C')
    pdf.cell(50, 8, "Média Calculada", 1, align='C')
    pdf.ln()
    
    pdf.set_font("helvetica", '', 10)
    for i in range(len(nomes_amostras)):
        pdf.cell(40, 7, nomes_amostras[i], 1, align='C')
        pdf.cell(50, 7, f"{medias_amostras[i]:.4f}", 1, align='C')
        pdf.ln()

    # Saída Final
    nome_relatorio = "relatorio_completo_x.pdf"
    caminho_pdf = os.path.join(caminho_destino, nome_relatorio)
    pdf.output(caminho_pdf)
    
    # Limpeza da imagem temporária
    if os.path.exists(temp_img):
        os.remove(temp_img)
        
    print(f"✓ PDF completo gerado com sucesso em: {caminho_pdf}")

if __name__ == "__main__":
    carta_x()