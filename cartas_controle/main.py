import Carta_x
from Kalman import Kalman

class Main:
    def main():
        opção = input("Escolha uma opção:\n1. XR\n2. P\n3. U\n4. IMR\n5. Sair\n\n")
        choice = True
        match opção:
            case "1":
                xr = Carta_x.carta_x()
            case "2":
                ...
            case "3":
                ...
            case "4":
                ...
            case "5":
                print("Saindo...")
                choice = False
            case _:
                print("Opção inválida. Retorne.")

if __name__ == "__main__":
    Main.main()