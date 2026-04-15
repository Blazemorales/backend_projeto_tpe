from amostras import data_collector_x
from cartas_controle import carta_x

def main():
    opção = input("Escolha sua opção: 1 - Analisar dados aleatórios, 2 - Coletar seus próprios dados, 3 - Sair: ").strip()
    
    match opção:
        case '1':
            print("\nAnalisando dados aleatórios...")
            carta_x.carta_x()
        
        case '2':
            print("\nColetando seus próprios dados...")
            coletor = data_collector_x.BancoDeDadosProcesso()
            coletor.gerador_banco_de_dados()
        
        case '3':
            return 'Encerrando...'
        
        case _:
            print("Opção inválida. Por favor, escolha 1, 2 ou 3.")

if __name__ == "__main__":
    main()