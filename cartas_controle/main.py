from Cartas import Cartas

class Main:
    @staticmethod
    def main():

        x = Cartas.carta_x()
        r = Cartas.carta_r()
        print("Processamento finalizado com sucesso.")
        return x, r

if __name__ == "__main__":
    Main.main()