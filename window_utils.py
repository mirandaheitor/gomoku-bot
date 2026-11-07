import ctypes
from ctypes import wintypes


user32 = ctypes.windll.user32


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def listar_janelas_visiveis(filtro_titulo=""):
    """Lista janelas visiveis do Windows, filtrando por parte do titulo."""
    janelas = []
    filtro = filtro_titulo.lower()

    def callback(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True

        tamanho = user32.GetWindowTextLengthW(hwnd)
        if tamanho == 0:
            return True

        buffer = ctypes.create_unicode_buffer(tamanho + 1)
        user32.GetWindowTextW(hwnd, buffer, tamanho + 1)
        titulo = buffer.value.strip()

        if filtro and filtro not in titulo.lower():
            return True

        rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return True

        largura = rect.right - rect.left
        altura = rect.bottom - rect.top

        if largura <= 0 or altura <= 0:
            return True

        janelas.append(
            {
                "hwnd": hwnd,
                "title": titulo,
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
                "width": largura,
                "height": altura,
            }
        )
        return True

    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(enum_proc(callback), 0)
    return janelas


def ordenar_janelas(janelas, modo="left_to_right"):
    """Ordena as janelas para facilitar escolher ganhador/perdedor por indice."""
    if modo == "top_to_bottom":
        return sorted(janelas, key=lambda janela: (janela["top"], janela["left"]))

    return sorted(janelas, key=lambda janela: (janela["left"], janela["top"]))


def detectar_janelas_jogo(titulo, modo_ordenacao="left_to_right"):
    """Detecta as janelas do jogo pelo titulo e devolve ordenadas."""
    return ordenar_janelas(listar_janelas_visiveis(titulo), modo_ordenacao)


def somar_coordenada(janela, coordenada_relativa):
    """Converte uma coordenada relativa a janela em coordenada absoluta."""
    x, y = coordenada_relativa
    return janela["left"] + x, janela["top"] + y


def calcular_casa_tabuleiro(janela, origem_relativa, tamanho_casa, jogada):
    """Converte linha/coluna do tabuleiro em coordenada absoluta de clique."""
    linha, coluna = jogada
    origem_x, origem_y = origem_relativa

    x_relativo = origem_x + (coluna * tamanho_casa)
    y_relativo = origem_y + (linha * tamanho_casa)

    return somar_coordenada(janela, (x_relativo, y_relativo))


def formatar_janela(indice, janela):
    """Monta uma linha legivel para mostrar no terminal."""
    return (
        f"[{indice}] {janela['title']} | "
        f"X={janela['left']} Y={janela['top']} "
        f"W={janela['width']} H={janela['height']}"
    )
