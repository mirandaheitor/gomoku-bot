import ctypes
import msvcrt
import time

import pydirectinput

from config import (
    AUTO_BOARD_MAX_CELL_SIZE,
    AUTO_BOARD_MIN_CELL_SIZE,
    OTHELLO_AUTO_MAX_CELL_SIZE,
    OTHELLO_AUTO_MIN_CELL_SIZE,
    OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
    WINDOW_SORT_MODE,
    WINDOW_TITLE_KEYWORD,
)
from board_detector import detectar_tabuleiro, detectar_tabuleiro_othello
from window_utils import detectar_janelas_jogo, formatar_janela


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def obter_posicao_com_ctypes():
    """Le a posicao atual do mouse usando a API do Windows."""
    ponto = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(ponto))
    return ponto.x, ponto.y


def obter_posicao_mouse():
    """Usa pydirectinput.position(), se existir, ou uma alternativa equivalente."""
    if hasattr(pydirectinput, "position"):
        return pydirectinput.position()

    return obter_posicao_com_ctypes()


def main():
    print("Calibrador de coordenadas do mouse.")
    print("Mova o mouse ate o ponto desejado.")
    print("Pressione ENTER para registrar a posicao atual.")
    print("Pressione CTRL+C para sair e ver os pontos registrados.\n")

    janelas = detectar_janelas_jogo(WINDOW_TITLE_KEYWORD, WINDOW_SORT_MODE)

    if janelas:
        print("Janelas detectadas:")
        for indice, janela in enumerate(janelas):
            print(formatar_janela(indice, janela))
        print()
    else:
        print(f'Nenhuma janela detectada com o filtro "{WINDOW_TITLE_KEYWORD}".')
        print("O calibrador ainda mostrara a coordenada absoluta do mouse.\n")

    tabuleiros = []
    tabuleiros_othello = []

    for indice, janela in enumerate(janelas[:4]):
        tabuleiro = detectar_tabuleiro(
            janela,
            AUTO_BOARD_MIN_CELL_SIZE,
            AUTO_BOARD_MAX_CELL_SIZE,
        )
        tabuleiros.append(tabuleiro)
        tabuleiro_othello = detectar_tabuleiro_othello(
            janela,
            OTHELLO_AUTO_MIN_CELL_SIZE,
            OTHELLO_AUTO_MAX_CELL_SIZE,
            OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
        )
        tabuleiros_othello.append(tabuleiro_othello)

        if tabuleiro:
            print(
                f"Tabuleiro Gomoku J{indice}: "
                f"ABS X={tabuleiro['abs_left']} Y={tabuleiro['abs_top']} "
                f"CELL={tabuleiro['cell']}"
            )
        else:
            print(f"Tabuleiro Gomoku J{indice}: nao detectado")

        if tabuleiro_othello:
            print(
                f"Tabuleiro Othello J{indice}: "
                f"ABS X={tabuleiro_othello['abs_left']} Y={tabuleiro_othello['abs_top']} "
                f"CELL={tabuleiro_othello['cell']}"
            )
        else:
            print(f"Tabuleiro Othello J{indice}: nao detectado")

    if tabuleiros:
        print()

    pontos_registrados = []

    try:
        while True:
            x, y = obter_posicao_mouse()
            partes = [f"ABS X={x} Y={y}"]

            for indice, janela in enumerate(janelas[:4]):
                relativo_x = x - janela["left"]
                relativo_y = y - janela["top"]
                partes.append(f"J{indice} REL X={relativo_x} Y={relativo_y}")

                if indice < len(tabuleiros) and tabuleiros[indice]:
                    board_x = x - tabuleiros[indice]["abs_left"]
                    board_y = y - tabuleiros[indice]["abs_top"]
                    partes.append(f"J{indice} GOMOKU X={board_x} Y={board_y}")

                if indice < len(tabuleiros_othello) and tabuleiros_othello[indice]:
                    board_x = x - tabuleiros_othello[indice]["abs_left"]
                    board_y = y - tabuleiros_othello[indice]["abs_top"]
                    partes.append(f"J{indice} OTHELLO X={board_x} Y={board_y}")

            print(" | ".join(partes) + "     ", end="\r")

            if msvcrt.kbhit():
                tecla = msvcrt.getwch()

                if tecla == "\r":
                    print()
                    descricao = input("Descricao do ponto: ").strip()

                    if not descricao:
                        descricao = f"Ponto {len(pontos_registrados) + 1}"

                    pontos_registrados.append((descricao, x, y))
                    print(f"Registrado: {descricao}: ({x}, {y})")
                    print("Continue movendo o mouse ou pressione CTRL+C para sair.")

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nCalibracao encerrada.")

        if pontos_registrados:
            print("\nPontos registrados:")

            for descricao, x, y in pontos_registrados:
                print(f"{descricao}: ({x}, {y})")
        else:
            print("Nenhum ponto registrado.")


if __name__ == "__main__":
    main()
