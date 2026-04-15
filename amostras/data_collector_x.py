import json
import math
import os

class BancoDeDadosProcesso:
    def __init__(self, nome_arquivo='amostra.json'):

        # Obtém o caminho absoluto da pasta de destino
        script_dir = os.path.dirname(os.path.abspath(__file__))
        projeto_root = os.path.dirname(os.path.dirname(script_dir))
        self.pasta_destino = os.path.join(projeto_root, 'app', 'banco_de_dados_amostras', 'dados_coletados')
        
        if not os.path.exists(self.pasta_destino):
            os.makedirs(self.pasta_destino)
            print(f"Pasta '{self.pasta_destino}' criada com sucesso.")

        self.caminho_arquivo = os.path.join(self.pasta_destino, nome_arquivo)
        
        self.valores = []

    def calcular_estatisticas_finais(self):
        """Calcula média e desvio-padrão apenas ao final da coleta"""
        if not self.valores:
            return 0, 0
            
        n = len(self.valores)
        media = (sum(self.valores)) / n
        
        soma_quadrados_desvios = sum((x - media) ** 2 for x in self.valores)
        variancia = soma_quadrados_desvios / n
        desvio_padrao = math.sqrt(variancia)
        
        return media, desvio_padrao

    def coletar_e_salvar(self):
        print(f"\n>>> Coletando dados para: {self.caminho_arquivo}")
        print("Digite 'stop' para encerrar.")
        
        numero_dado = 1
        while True:
            entrada = input(f"Inserir Dado #{numero_dado}: ").strip().lower()
            if entrada == 'stop': 
                break
                
            try:
                valor = float(entrada)
                self.valores.append(valor)
                numero_dado += 1
            except ValueError:
                print("Erro: Digite um número válido.")

        # Calcular estatísticas apenas ao final
        media, desvio_padrao = self.calcular_estatisticas_finais()
        
        # Criar histórico com apenas os valores brutos
        historico = [
            {
                "id": i + 1,
                "valor_bruto": valor,
            }
            for i, valor in enumerate(self.valores)
        ]
        
        # Adicionar estatísticas ao final
        historico.append({
            "media": round(media, 4),
            "desvio_padrao": round(desvio_padrao, 4)
        })

        # Salvando no caminho configurado no __init__
        with open(self.caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
            
        print(f"\nResumo da coleta:")
        print(f"  Total de valores: {len(self.valores)}")
        print(f"  Média: {round(media, 4)}")
        print(f"  Desvio-padrão: {round(desvio_padrao, 4)}")
        print(f"Arquivo salvo em: {self.caminho_arquivo}")
        return historico 
    
    def gerador_banco_de_dados(self):
        print("Pronto para coletar amostras!")
        contador = 1
        
        while True:
            confirmacao = input(f"\nDeseja iniciar a coleta da Amostra nº{contador}? (digite 'stop' para parar, e 's' para continuar): ").strip().lower()
            
            if confirmacao == 'stop':
                print("Finalizando criação de bancos.")
                break
            elif confirmacao == 's':
            
                # O 'f' antes das aspas permite que o {contador} seja substituído pelo número
                nome = f'amostra_{contador}.json'
                
                # Criamos uma nova instância para cada arquivo novo
                nova_amostra = BancoDeDadosProcesso(nome_arquivo=nome)
                nova_amostra.coletar_e_salvar()
                
                contador += 1
            else:
                print("Opção inválida, tente novamente.")
            