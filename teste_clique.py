import time
import ctypes

import pydirectinput


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def obter_posicao_mouse():
    """Le a posicao atual do mouse usando a API do Windows."""
    ponto = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(ponto))
    return ponto.x, ponto.y


def main():
    print("Coloque o mouse sobre uma casa do Gomoku.")
    print("O teste sera executado em 5 segundos.")

    for segundos in range(5, 0, -1):
        print(f"Clicando em {segundos}...")
        time.sleep(1)

    x, y = obter_posicao_mouse()
    print(f"Posicao capturada: X={x}, Y={y}")

    print("Tentativa 1: pydirectinput.moveTo + pydirectinput.click")
    pydirectinput.moveTo(x, y, duration=0.1)
    pydirectinput.click()
    time.sleep(0.5)

    print("Tentativa 2: pydirectinput.mouseDown + pydirectinput.mouseUp")
    pydirectinput.moveTo(x, y, duration=0.1)
    pydirectinput.mouseDown()
    time.sleep(0.08)
    pydirectinput.mouseUp()

    print("Teste finalizado.")


if __name__ == "__main__":
    main()
