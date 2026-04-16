from .Cartas import carta_x
from .Kalman import Kalman

class Main:
    @staticmethod
    def main():
        """Gera a carta de controle e PDF sem interação do usuário"""
        xr = carta_x()
        return xr

if __name__ == "__main__":
    Main.main()