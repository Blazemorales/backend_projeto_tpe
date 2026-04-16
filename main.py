import os
from flask import Flask, send_file, jsonify
# Importa a sua função do arquivo onde ela está
from seu_arquivo_da_carta import carta_x 

app = Flask(__name__)

# Configuração de caminhos para o Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_RELATORIOS = os.path.join(BASE_DIR, 'relatorios')

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "projeto": "CPE - Controle de Processos Eletronica FGA",
        "endpoint": "/gerar-pdf"
    })

@app.route('/gerar-pdf', methods=['GET'])
def endpoint_pdf():
    try:
        # 1. Executa a lógica que você já criou
        carta_x()
        
        # 2. Localiza o PDF gerado
        caminho_pdf = os.path.join(PASTA_RELATORIOS, "relatorio_completo_x.pdf")
        
        if os.path.exists(caminho_pdf):
            # 3. Retorna o arquivo para download no navegador
            return send_file(caminho_pdf, as_attachment=True)
        else:
            return jsonify({"error": "PDF não foi encontrado no servidor"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # O Render define a porta automaticamente na variável de ambiente PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)