import numpy as np
import matplotlib.pyplot as plt
import json
import os
from fpdf import FPDF
import matplotlib

matplotlib.use('Agg')

class Cartas:
    @staticmethod
    def carta_x():
        print("--- Gerando Relatório PDF e Carta de Controle ---\n")

        # --- Configuração de Caminhos ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_base = os.path.join(os.path.dirname(script_dir), 'banco_de_dados')
        caminho_destino = os.path.join(os.path.dirname(script_dir), 'relatorios')

        if not os.path.exists(caminho_destino):
            os.makedirs(caminho_destino)

        arquivos_alvo = ['estatisticas_individuais.json', 'estatisticas.json']
        caminho_estatisticas = next((os.path.join(caminho_base, f) for f in arquivos_alvo 
                                   if os.path.exists(os.path.join(caminho_base, f))), None)

        if not caminho_estatisticas:
            print(f"Erro: Nenhum arquivo encontrado em {caminho_base}.")
            return

        with open(caminho_estatisticas, 'r', encoding='utf-8') as f:
            dados_processados = json.load(f)

        nomes_amostras = [str(item['amostra']) for item in dados_processados]
        medias_amostras = [item.get('media', item.get('media da amostra')) for item in dados_processados]
        n = len(medias_amostras)

        # --- Cálculos da Carta X ---
        media_das_medias = np.mean(medias_amostras)
        sigma = np.std(medias_amostras, ddof=1)
        lsc, lic = media_das_medias + 3*sigma, media_das_medias - 3*sigma

        # --- Verificação de Regras de Controle ---
        condicoes = {
            "regra1": any(m > lsc or m < lic for m in medias_amostras),
            "regra2": False, # 2 de 3 pontos além de 2 sigma
            "regra3": False, # 4 de 5 pontos além de 1 sigma
            "regra4": False  # 8 pontos consecutivos do mesmo lado da média
        }

        # Verificação Regra 2 (2 de 3 consecutivos > 2 sigma)
        for i in range(n - 2):
            janela = medias_amostras[i:i+3]
            if sum(1 for x in janela if x > (media_das_medias + 2*sigma) or x < (media_das_medias - 2*sigma)) >= 2:
                condicoes["regra2"] = True

        # Verificação Regra 3 (4 de 5 consecutivos > 1 sigma)
        for i in range(n - 4):
            janela = medias_amostras[i:i+5]
            if sum(1 for x in janela if x > (media_das_medias + sigma) or x < (media_das_medias - sigma)) >= 4:
                condicoes["regra3"] = True

        # Verificação Regra 4 (8 consecutivos do mesmo lado)
        cont_acima = 0
        cont_abaixo = 0
        for m in medias_amostras:
            if m > media_das_medias:
                cont_acima += 1
                cont_abaixo = 0
            else:
                cont_abaixo += 1
                cont_acima = 0
            if cont_acima >= 8 or cont_abaixo >= 8:
                condicoes["regra4"] = True

        # Definição da Mensagem de Status
        if all(condicoes.values()):
            status_processo = "ALERTA CRÍTICO: Todas as condições de falha foram atingidas. Convém reavaliar o processo e considerar ações corretivas imediatas."
        elif any(condicoes.values()):
            status_processo = "Atenção: O processo apresenta instabilidades (pontos fora de controle detectados)."
        else:
            status_processo = "Processo sob controle: Todos os pontos seguem as normas estatísticas."

        # --- Geração do Gráfico ---
        plt.figure(figsize=(10, 5))
        plt.plot(range(1, n + 1), medias_amostras, 'bo-', linewidth=2, label='Média das Amostras')
        plt.axhline(media_das_medias, color='green', label=f'X_médio: {media_das_medias:.2f}')
        plt.axhline(lsc, color='red', linestyle='--', label=f'LSC: {lsc:.2f}')
        plt.axhline(lic, color='red', linestyle='--', label=f'LIC: {lic:.2f}')
        
        # Sombreamento das zonas de sigma para clareza visual
        plt.fill_between(range(1, n+1), media_das_medias + 2*sigma, lsc, color='red', alpha=0.1)
        plt.fill_between(range(1, n+1), lic, media_das_medias - 2*sigma, color='red', alpha=0.1)

        plt.title("Carta de Controle X")
        plt.xticks(range(1, n + 1), nomes_amostras)
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)

        temp_img = os.path.join(caminho_destino, "temp_chart.png")
        plt.savefig(temp_img, bbox_inches='tight', dpi=100)
        plt.close()

        # --- Geração do PDF ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(190, 10, "Relatório de Qualidade - Carta de Controle", ln=True, align='C')
        pdf.ln(10)

        # Status do Processo (O que você pediu)
        pdf.set_font("helvetica", 'B', 12)
        if all(condicoes.values()):
            pdf.set_text_color(255, 0, 0) # Texto em Vermelho se estiver crítico
        pdf.multi_cell(190, 8, f"Status: {status_processo}")
        pdf.set_text_color(0, 0, 0) # Volta para preto
        pdf.ln(5)

        # Resumo
        pdf.set_font("helvetica", '', 11)
        pdf.cell(190, 7, f"Média Geral: {media_das_medias:.4f}", ln=True)
        pdf.cell(190, 7, f"LSC: {lsc:.4f} / LIC: {lic:.4f}", ln=True)
        pdf.ln(5)

        # Gráfico e Tabela
        pdf.image(temp_img, x=15, w=170)
        pdf.ln(5)
        
        pdf.set_font("helvetica", 'B', 10)
        pdf.cell(40, 8, "Amostra", 1)
        pdf.cell(50, 8, "Média", 1)
        pdf.ln()

        pdf.set_font("helvetica", '', 10)
        for i in range(n):
            pdf.cell(40, 7, nomes_amostras[i], 1)
            pdf.cell(50, 7, f"{medias_amostras[i]:.4f}", 1)
            pdf.ln()

        caminho_pdf = os.path.join(caminho_destino, "relatorio_completo_x.pdf")
        pdf.output(caminho_pdf)
        
        if os.path.exists(temp_img): os.remove(temp_img)
        print(f"✓ Relatório gerado: {caminho_pdf}")
    
    @staticmethod
    def carta_r():
        print("--- Gerando Relatório PDF e Carta de Controle R (Amplitude) ---\n")

        # --- Configuração de Caminhos ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_base = os.path.join(os.path.dirname(script_dir), 'banco_de_dados')
        caminho_destino = os.path.join(os.path.dirname(script_dir), 'relatorios')

        if not os.path.exists(caminho_destino):
            os.makedirs(caminho_destino)

        caminho_estatisticas = os.path.join(caminho_base, 'estatisticas_individuais.json')

        if not os.path.exists(caminho_estatisticas):
            print(f"Erro: Arquivo {caminho_estatisticas} não encontrado.")
            return

        with open(caminho_estatisticas, 'r', encoding='utf-8') as f:
            dados_processados = json.load(f)

        nomes_amostras = [str(item['amostra']) for item in dados_processados]
        amplitudes = [item.get('amplitude', 0) for item in dados_processados]
        n_pontos = len(amplitudes)

        # --- Cálculos da Carta R ---
        r_bar = np.mean(amplitudes)
        
        # Nota: Em um sistema completo, d2 e d3 viriam do calculod3.obter_d3()
        # Para os limites LSC_r e LIC_r, usamos D4*R_bar e D3*R_bar
        # Aqui, como exemplo para n=5 (comum em seus scripts):
        d2, d3 = 2.326, 0.864 
        D4 = 1 + 3*(d3/d2)
        D3 = max(0, 1 - 3*(d3/d2))

        lsc_r = r_bar * D4
        lic_r = r_bar * D3

        # --- Verificação de Regra Simples (Ponto fora do limite) ---
        fora_de_controle = any(r > lsc_r or r < lic_r for r in amplitudes)
        status_r = "ALERTA: Variabilidade instável detectada!" if fora_de_controle else "Variabilidade sob controle."

        # --- Geração do Gráfico R ---
        plt.figure(figsize=(10, 5))
        plt.plot(range(1, n_pontos + 1), amplitudes, 'ro-', linewidth=2, label='Amplitude (R)')
        plt.axhline(r_bar, color='green', label=f'R-médio: {r_bar:.2f}')
        plt.axhline(lsc_r, color='darkred', linestyle='--', label=f'LSC_r: {lsc_r:.2f}')
        plt.axhline(lic_r, color='darkred', linestyle='--', label=f'LIC_r: {lic_r:.2f}')

        plt.title("Carta de Controle R (Amplitude)")
        plt.xlabel("Amostra")
        plt.ylabel("Amplitude")
        plt.xticks(range(1, n_pontos + 1), nomes_amostras)
        plt.legend(loc='upper right')
        plt.grid(True, alpha=0.3)

        temp_img_r = os.path.join(caminho_destino, "temp_chart_r.png")
        plt.savefig(temp_img_r, bbox_inches='tight', dpi=100)
        plt.close()

        # --- Geração do PDF R ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(190, 10, "Relatório de Qualidade - Carta R (Amplitude)", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("helvetica", 'B', 12)
        if fora_de_controle: pdf.set_text_color(255, 0, 0)
        pdf.cell(190, 8, f"Status da Variabilidade: {status_r}", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("helvetica", '', 11)
        pdf.cell(190, 7, f"Amplitude Média (R-bar): {r_bar:.4f}", ln=True)
        pdf.cell(190, 7, f"LSC: {lsc_r:.4f} / LIC: {lic_r:.4f}", ln=True)
        pdf.ln(5)

        pdf.image(temp_img_r, x=15, w=170)
        
        caminho_pdf_r = os.path.join(caminho_destino, "relatorio_carta_r.pdf")
        pdf.output(caminho_pdf_r)
        
        if os.path.exists(temp_img_r): os.remove(temp_img_r)
        print(f"✓ Carta R gerada com sucesso: {caminho_pdf_r}")

if __name__ == "__main__":
    Cartas.carta_x()