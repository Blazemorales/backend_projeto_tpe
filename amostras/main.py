from data_collector_x import BancoDeDadosProcesso

def main():
    print("=" * 50)
    print("   SISTEMA DE COLETA DE DADOS")
    print("=" * 50)
    
    while True:
        print("\nOpções:")
        print("1 - Coletar múltiplas amostras")
        print("2 - Sair")
        
        opcao = input("\nEscolha uma opção (1 ou 2): ").strip()
        
        if opcao == '1':
            amostras = BancoDeDadosProcesso()
            amostras.gerador_banco_de_dados()
    
        elif opcao == '2':
            print("\nEncerrando programa...")
            break
            
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()
