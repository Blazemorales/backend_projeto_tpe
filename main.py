import os
from flask import Flask, send_file, jsonify
import matplotlib
# ESSENCIAL: Impede que o Matplotlib tente abrir uma janela no servidor
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

# Importa a função do seu arquivo data_processor.py
from cartas_controle import Carta_x 

app = Flask(__name__)

# Define os caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_RELATORIOS = os.path.join(BASE_DIR, 'relatorios')

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "projeto": "CPE - Controle de Processos Eletronica FGA",
        "endpoints": {
            "gerar_pdf": "/gerar-pdf"
        }
    })

@app.route('/gerar-pdf', methods=['GET'])
def endpoint_pdf():
    try:
        # Garante que a pasta de relatórios existe no servidor
        if not os.path.exists(PASTA_RELATORIOS):
            os.makedirs(PASTA_RELATORIOS)
        
        # Executa a sua lógica de cálculo e geração de gráfico
        Carta_x.carta_x()
        
        # O nome do arquivo deve ser o mesmo que você definiu na função carta_x
        caminho_pdf = os.path.join(PASTA_RELATORIOS, "relatorio_completo_x.pdf")
        
        if os.path.exists(caminho_pdf):
            return send_file(caminho_pdf, as_attachment=True)
        else:
            return jsonify({"error": f"PDF nao encontrado em: {caminho_pdf}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # O Render usa a variável de ambiente PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)