import os
from flask import Flask, send_file, jsonify
import matplotlib

# Configuração para servidores Headless (sem interface gráfica)
matplotlib.use('Agg') 

app = Flask(__name__)

# Caminhos absolutos baseados na localização deste arquivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_RELATORIOS = os.path.join(BASE_DIR, 'relatorios')

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "projeto": "CPE - Controle Estatístico de Processo",
        "autor": "João Morais",
        "endpoints": {
            "gerar_pdf_x": "/gerarpdfx",
            "gerar_pdf_r": "/gerarpdfr"
        }
    })

@app.route('/gerarpdfx', methods=['GET'])
def endpoint_pdf_x():
    try:
        # Importação tardia (Lazy Import) para evitar erros de path no startup
        from cartas_controle.main import Main
        
        # Executa a lógica que gera os arquivos JSON e o PDF
        Main.x()
        
        # O nome deve bater exatamente com o que está definido em Cartas.py
        caminho_pdf = os.path.join(PASTA_RELATORIOS, "relatorio_completo_x.pdf")
        
        if os.path.exists(caminho_pdf):
            return send_file(caminho_pdf, as_attachment=True)
        else:
            return jsonify({"error": f"PDF não encontrado no servidor."}), 404
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@app.route('/gerarpdfr', methods=['GET'])
def endpoint_pdf_r():
    try:
        # Importação tardia (Lazy Import) para evitar erros de path no startup
        from cartas_controle.main import Main
        
        # Executa a lógica que gera os arquivos JSON e o PDF
        Main.r() 
        
        # O nome deve bater exatamente com o que está definido em Cartas.py
        caminho_pdf = os.path.join(PASTA_RELATORIOS, "relatorio_carta_r.pdf")
        
        if os.path.exists(caminho_pdf):
            return send_file(caminho_pdf, as_attachment=True)
        else:
            return jsonify({"error": f"PDF não encontrado no servidor."}), 404
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)