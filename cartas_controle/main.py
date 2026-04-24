import sys
import os

# --- CORREÇÃO DE PATH: Permite importar 'amostras' mesmo executando de dentro da pasta ---
# Pega o caminho da pasta 'cartas_controle' e sobe um nível para a raiz 'backend_tpe_e'
raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if raiz_projeto not in sys.path:
    sys.path.append(raiz_projeto)

# Agora os imports funcionam sem erro
from Cartas import Cartas
from amostras.data_processor import DataProcessor


class Main:
    @staticmethod
    def processar_dados(arquivo_dados='dados_producao_total.json'):
        """Processa dados brutos e gera dados tratados."""
        print("\n[ETAPA 1] Processando dados brutos...")
        processor = DataProcessor()
        # O processor agora usa caminhos absolutos internamente
        if processor.processar_e_salvar(arquivo_dados):
            print("✓ Dados processados com sucesso!")
            return True
        else:
            print("✗ Erro ao processar dados")
            return False
    
    @staticmethod
    def gerar_relatorios():
        """Gera todos os relatórios de controle."""
        print("\n[ETAPA 2] Gerando relatórios...")
        if Cartas.gerar_todos_relatorios():
            print("✓ Relatórios gerados com sucesso!")
            return True
        else:
            print("✗ Erro ao gerar relatórios")
            return False
    
    @staticmethod
    def executar_completo(arquivo_dados='dados_producao_total.json'):
        """Executa o pipeline completo: processamento + geração de relatórios."""
        print("\n" + "="*60)
        print("PIPELINE COMPLETO - PROCESSAMENTO E GERAÇÃO DE RELATÓRIOS")
        print("="*60)
        
        if Main.processar_dados(arquivo_dados):
            if Main.gerar_relatorios():
                print("\n" + "="*60)
                print("✓ PROCESSO FINALIZADO COM SUCESSO!")
                print("="*60 + "\n")
                return True
        
        print("\n" + "="*60)
        print("✗ ERRO NO PROCESSO")
        print("="*60 + "\n")
        return False
    
    @staticmethod
    def x():
        """Atalho para pipeline XR."""
        return Main.executar_completo()
    
    @staticmethod
    def r():
        """Gera apenas relatório R."""
        dados = Cartas.carregar_dados_tratados()
        if dados:
            dados_r = next((d for d in dados if d.get("chart") == "XR"), None)
            if dados_r:
                return Cartas.carta_xr(dados_r)
        return False
    
    @staticmethod
    def p():
        """Gera apenas relatório P."""
        dados = Cartas.carregar_dados_tratados()
        if dados:
            dados_p = next((d for d in dados if d.get("chart") == "P"), None)
            if dados_p:
                return Cartas.carta_p(dados_p)
        return Cartas.carta_p()
    
    @staticmethod
    def u():
        """Gera apenas relatório U."""
        dados = Cartas.carregar_dados_tratados()
        if dados:
            dados_u = next((d for d in dados if d.get("chart") == "U"), None)
            if dados_u:
                return Cartas.carta_u(dados_u)
        return Cartas.carta_u()
    
    @staticmethod
    def imr():
        """Gera apenas relatório IMR."""
        dados = Cartas.carregar_dados_tratados()
        if dados:
            dados_imr = next((d for d in dados if d.get("chart") == "IMR"), None)
            if dados_imr:
                return Cartas.carta_imr(dados_imr)
        return Cartas.carta_imr()
    
    @staticmethod
    def main():
        Main.executar_completo()


if __name__ == "__main__":
    Main.main()