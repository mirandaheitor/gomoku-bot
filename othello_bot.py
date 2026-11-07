import time

import pydirectinput

from config import (
    OTHELLO_ALTERNATE_WINNER,
    OTHELLO_CONFIRMATION_ENABLED,
    OTHELLO_AUTO_MAX_CELL_SIZE,
    OTHELLO_AUTO_MIN_CELL_SIZE,
    OTHELLO_CONTINUE_FROM_BOARD_OFFSET,
    OTHELLO_COORDINATE_MODE,
    OTHELLO_DELAY_AFTER_CONFIRM,
    OTHELLO_DELAY_AFTER_CONTINUE,
    OTHELLO_DELAY_AFTER_RESULT,
    OTHELLO_DELAY_AFTER_SURRENDER,
    OTHELLO_DELAY_BEFORE_START,
    OTHELLO_DELAY_BETWEEN_CONTINUE_CLICKS,
    OTHELLO_DELAY_AFTER_FOCUS,
    OTHELLO_FOCUS_BEFORE_SURRENDER,
    OTHELLO_MOUSE_DOWN_DURATION,
    OTHELLO_LEFT_WINDOW_INDEX,
    OTHELLO_LEFT_CONFIRM,
    OTHELLO_LEFT_CONTINUE,
    OTHELLO_LEFT_SURRENDER,
    OTHELLO_PASS_FROM_BOARD_OFFSET,
    OTHELLO_RIGHT_WINDOW_INDEX,
    OTHELLO_RIGHT_CONFIRM,
    OTHELLO_RIGHT_CONTINUE,
    OTHELLO_RIGHT_SURRENDER,
    OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
    OTHELLO_START_FROM_FINAL_SCREEN,
    WINDOW_SORT_MODE,
    WINDOW_TITLE_KEYWORD,
)
from window_utils import detectar_janelas_jogo, formatar_janela


OTHELLO_POSITIONS_CACHE = None


def is_valid_position(position):
    """Confere se a coordenada esta no formato (x, y), com inteiros."""
    return (
        isinstance(position, tuple)
        and len(position) == 2
        and isinstance(position[0], int)
        and isinstance(position[1], int)
    )


def validate_othello_config():
    """Valida as coordenadas usadas pelo modo Othello."""
    errors = []

    if OTHELLO_COORDINATE_MODE not in ("manual", "auto_board"):
        errors.append('OTHELLO_COORDINATE_MODE precisa ser "manual" ou "auto_board".')

    if OTHELLO_COORDINATE_MODE == "auto_board":
        if OTHELLO_AUTO_MIN_CELL_SIZE <= 0:
            errors.append("OTHELLO_AUTO_MIN_CELL_SIZE precisa ser maior que zero.")

        if OTHELLO_AUTO_MAX_CELL_SIZE < OTHELLO_AUTO_MIN_CELL_SIZE:
            errors.append("OTHELLO_AUTO_MAX_CELL_SIZE precisa ser maior ou igual ao minimo.")

        if OTHELLO_LEFT_WINDOW_INDEX == OTHELLO_RIGHT_WINDOW_INDEX:
            errors.append("OTHELLO_LEFT_WINDOW_INDEX e OTHELLO_RIGHT_WINDOW_INDEX precisam ser diferentes.")

        positions = {
            "OTHELLO_PASS_FROM_BOARD_OFFSET": OTHELLO_PASS_FROM_BOARD_OFFSET,
            "OTHELLO_SURRENDER_FROM_BOARD_OFFSET": OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
            "OTHELLO_CONTINUE_FROM_BOARD_OFFSET": OTHELLO_CONTINUE_FROM_BOARD_OFFSET,
        }

        if OTHELLO_CONFIRMATION_ENABLED:
            positions.update(
                {
                    "OTHELLO_LEFT_CONFIRM": OTHELLO_LEFT_CONFIRM,
                    "OTHELLO_RIGHT_CONFIRM": OTHELLO_RIGHT_CONFIRM,
                }
            )
    else:
        positions = {
            "OTHELLO_LEFT_SURRENDER": OTHELLO_LEFT_SURRENDER,
            "OTHELLO_RIGHT_SURRENDER": OTHELLO_RIGHT_SURRENDER,
            "OTHELLO_LEFT_CONFIRM": OTHELLO_LEFT_CONFIRM,
            "OTHELLO_RIGHT_CONFIRM": OTHELLO_RIGHT_CONFIRM,
            "OTHELLO_LEFT_CONTINUE": OTHELLO_LEFT_CONTINUE,
            "OTHELLO_RIGHT_CONTINUE": OTHELLO_RIGHT_CONTINUE,
        }

    for name, position in positions.items():
        if not is_valid_position(position):
            errors.append(f"{name} precisa estar no formato (x, y), com numeros inteiros.")

    if errors:
        print("\n[OTHELLO] Erro na configuracao:")
        for error in errors:
            print(f"[OTHELLO] - {error}")
        print("[OTHELLO] Edite o config.py e tente novamente.")
        return False

    return True


def carregar_detector_othello():
    """Carrega o detector visual apenas quando o modo automatico for usado."""
    try:
        from board_detector import (
            coordenada_por_offset_tabuleiro,
            detectar_ok_tela_final,
            detectar_tabuleiro_othello,
            formatar_ok,
            formatar_tabuleiro,
        )
    except ImportError:
        print("\n[OTHELLO] A dependencia Pillow nao esta instalada.")
        print("[OTHELLO] Instale com: pip install -r requirements.txt")
        return None

    return {
        "coordenada_por_offset_tabuleiro": coordenada_por_offset_tabuleiro,
        "detectar_ok_tela_final": detectar_ok_tela_final,
        "detectar_tabuleiro_othello": detectar_tabuleiro_othello,
        "formatar_ok": formatar_ok,
        "formatar_tabuleiro": formatar_tabuleiro,
    }


def detectar_janelas_othello():
    """Detecta as janelas do Angels usadas pelo Othello."""
    janelas = detectar_janelas_jogo(WINDOW_TITLE_KEYWORD, WINDOW_SORT_MODE)
    maior_indice = max(OTHELLO_LEFT_WINDOW_INDEX, OTHELLO_RIGHT_WINDOW_INDEX)

    if len(janelas) <= maior_indice:
        print("\n[OTHELLO] Nao encontrei janelas suficientes do jogo.")
        print(f"[OTHELLO] Filtro usado: {WINDOW_TITLE_KEYWORD}")
        print(f"[OTHELLO] Janelas encontradas: {len(janelas)}")

        for indice, janela in enumerate(janelas):
            print(f"[OTHELLO] {formatar_janela(indice, janela)}")

        return None, None

    left_window = janelas[OTHELLO_LEFT_WINDOW_INDEX]
    right_window = janelas[OTHELLO_RIGHT_WINDOW_INDEX]

    print("[OTHELLO] Janelas selecionadas:")
    print(f"[OTHELLO] ESQUERDA: {formatar_janela(OTHELLO_LEFT_WINDOW_INDEX, left_window)}")
    print(f"[OTHELLO] DIREITA: {formatar_janela(OTHELLO_RIGHT_WINDOW_INDEX, right_window)}")
    return left_window, right_window


def preparar_posicoes_othello_auto():
    """Detecta os tabuleiros Othello e calcula botoes por offset."""
    detector = carregar_detector_othello()

    if not detector:
        return None

    left_window, right_window = detectar_janelas_othello()

    if not left_window or not right_window:
        return None

    print("[OTHELLO] Detectando tabuleiro da esquerda...")
    left_board = detector["detectar_tabuleiro_othello"](
        left_window,
        OTHELLO_AUTO_MIN_CELL_SIZE,
        OTHELLO_AUTO_MAX_CELL_SIZE,
        OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
    )

    print("[OTHELLO] Detectando tabuleiro da direita...")
    right_board = detector["detectar_tabuleiro_othello"](
        right_window,
        OTHELLO_AUTO_MIN_CELL_SIZE,
        OTHELLO_AUTO_MAX_CELL_SIZE,
        OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
    )

    if not left_board or not right_board:
        print("\n[OTHELLO] Nao foi possivel detectar o tabuleiro nas duas janelas.")
        print("[OTHELLO] Confira se o Othello esta aberto e visivel nas duas instancias.")
        print('[OTHELLO] Fallback: use OTHELLO_COORDINATE_MODE = "manual".')
        return None

    print("[OTHELLO] " + detector["formatar_tabuleiro"]("ESQUERDA", left_board))
    print("[OTHELLO] " + detector["formatar_tabuleiro"]("DIREITA", right_board))

    left_surrender = detector["coordenada_por_offset_tabuleiro"](
        left_board,
        OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
    )
    right_surrender = detector["coordenada_por_offset_tabuleiro"](
        right_board,
        OTHELLO_SURRENDER_FROM_BOARD_OFFSET,
    )
    left_continue = detector["coordenada_por_offset_tabuleiro"](
        left_board,
        OTHELLO_CONTINUE_FROM_BOARD_OFFSET,
    )
    right_continue = detector["coordenada_por_offset_tabuleiro"](
        right_board,
        OTHELLO_CONTINUE_FROM_BOARD_OFFSET,
    )
    left_pass = detector["coordenada_por_offset_tabuleiro"](
        left_board,
        OTHELLO_PASS_FROM_BOARD_OFFSET,
    )
    right_pass = detector["coordenada_por_offset_tabuleiro"](
        right_board,
        OTHELLO_PASS_FROM_BOARD_OFFSET,
    )

    left_ok = left_continue
    right_ok = right_continue
    left_ok_detected = detector["detectar_ok_tela_final"](left_window, left_board)
    right_ok_detected = detector["detectar_ok_tela_final"](right_window, right_board)

    if left_ok_detected and right_ok_detected:
        left_ok = (left_ok_detected["abs_x"], left_ok_detected["abs_y"])
        right_ok = (right_ok_detected["abs_x"], right_ok_detected["abs_y"])
        print("[OTHELLO] " + detector["formatar_ok"]("OK ESQUERDA", left_ok_detected))
        print("[OTHELLO] " + detector["formatar_ok"]("OK DIREITA", right_ok_detected))
    else:
        print("[OTHELLO] OK final nao detectado nas duas janelas; usando offset configurado.")

    print(f"[OTHELLO] Pass esquerda: X={left_pass[0]} Y={left_pass[1]}")
    print(f"[OTHELLO] Pass direita: X={right_pass[0]} Y={right_pass[1]}")
    print(f"[OTHELLO] Surrender esquerda: X={left_surrender[0]} Y={left_surrender[1]}")
    print(f"[OTHELLO] Surrender direita: X={right_surrender[0]} Y={right_surrender[1]}")
    print(f"[OTHELLO] OK esquerda: X={left_ok[0]} Y={left_ok[1]}")
    print(f"[OTHELLO] OK direita: X={right_ok[0]} Y={right_ok[1]}")

    return {
        "left_surrender": left_surrender,
        "right_surrender": right_surrender,
        "left_confirm": OTHELLO_LEFT_CONFIRM,
        "right_confirm": OTHELLO_RIGHT_CONFIRM,
        "left_continue": left_ok,
        "right_continue": right_ok,
        "left_ok": left_ok,
        "right_ok": right_ok,
        "left_pass": left_pass,
        "right_pass": right_pass,
    }


def preparar_posicoes_othello():
    """Retorna as posicoes do Othello conforme o modo configurado."""
    if OTHELLO_COORDINATE_MODE == "auto_board":
        return preparar_posicoes_othello_auto()

    return {
        "left_surrender": OTHELLO_LEFT_SURRENDER,
        "right_surrender": OTHELLO_RIGHT_SURRENDER,
        "left_confirm": OTHELLO_LEFT_CONFIRM,
        "right_confirm": OTHELLO_RIGHT_CONFIRM,
        "left_continue": OTHELLO_LEFT_CONTINUE,
        "right_continue": OTHELLO_RIGHT_CONTINUE,
        "left_ok": OTHELLO_LEFT_CONTINUE,
        "right_ok": OTHELLO_RIGHT_CONTINUE,
        "left_pass": None,
        "right_pass": None,
    }


def obter_posicoes_othello_cacheadas():
    """Detecta uma vez e reutiliza as coordenadas do Othello."""
    global OTHELLO_POSITIONS_CACHE

    if OTHELLO_POSITIONS_CACHE is None:
        OTHELLO_POSITIONS_CACHE = preparar_posicoes_othello()

    return OTHELLO_POSITIONS_CACHE


def countdown(seconds):
    """Contagem regressiva simples antes de executar cliques."""
    if seconds <= 0:
        return

    for remaining in range(int(seconds), 0, -1):
        print(f"[OTHELLO] Comecando em {remaining}...")
        time.sleep(1)


def click_othello_position(position, description):
    """Move o mouse ate uma coordenada absoluta e clica de forma simples."""
    x, y = position
    print(f"[OTHELLO] Clicando em {description}: X={x} Y={y}")
    pydirectinput.moveTo(x, y)
    pydirectinput.click()


def click_othello_position_forced(position, description):
    """Clique real usando mouseDown/mouseUp para jogos que ignoram click simples."""
    x, y = position
    print(f"[OTHELLO] Clique real em {description}: X={x} Y={y}")
    pydirectinput.moveTo(x, y)
    pydirectinput.mouseDown()
    time.sleep(OTHELLO_MOUSE_DOWN_DURATION)
    pydirectinput.mouseUp()


def click_othello_surrender(position, description):
    """Foca a janela e depois clica em Surrender."""
    x, y = position

    if OTHELLO_FOCUS_BEFORE_SURRENDER:
        print(f"[OTHELLO] Focando janela antes do {description}: X={x} Y={y}")
        pydirectinput.moveTo(x, y)
        pydirectinput.click()
        time.sleep(OTHELLO_DELAY_AFTER_FOCUS)

    click_othello_position_forced(position, description)


def get_match_positions(winner_side, detected_positions):
    """Define perdedor, surrender, confirmacao e ordem dos botoes de continuar."""
    if winner_side == "left":
        return {
            "winner_label": "ESQUERDA",
            "loser_label": "DIREITA",
            "surrender": detected_positions["right_surrender"],
            "surrender_description": "Surrender da direita",
            "confirm": detected_positions["right_confirm"],
            "confirm_description": "confirmacao da direita",
            "winner_ok": detected_positions["left_ok"],
            "winner_ok_description": "OK do ganhador esquerdo",
            "loser_ok": detected_positions["right_ok"],
            "loser_ok_description": "OK do perdedor direito",
        }

    if winner_side == "right":
        return {
            "winner_label": "DIREITA",
            "loser_label": "ESQUERDA",
            "surrender": detected_positions["left_surrender"],
            "surrender_description": "Surrender da esquerda",
            "confirm": detected_positions["left_confirm"],
            "confirm_description": "confirmacao da esquerda",
            "winner_ok": detected_positions["right_ok"],
            "winner_ok_description": "OK do ganhador direito",
            "loser_ok": detected_positions["left_ok"],
            "loser_ok_description": "OK do perdedor esquerdo",
        }

    raise ValueError('winner_side precisa ser "left" ou "right".')


def opposite_side(side):
    """Retorna o lado oposto."""
    if side == "left":
        return "right"

    if side == "right":
        return "left"

    raise ValueError('side precisa ser "left" ou "right".')


def winner_side_for_match(initial_winner_side, match_number):
    """Alterna o vencedor quando OTHELLO_ALTERNATE_WINNER esta ativo."""
    if not OTHELLO_ALTERNATE_WINNER:
        return initial_winner_side

    if match_number % 2 == 1:
        return initial_winner_side

    return opposite_side(initial_winner_side)


def click_othello_result_ok(positions):
    """Clica OK do perdedor primeiro e depois OK do ganhador."""
    print("[OTHELLO] Clicando em OK do perdedor")
    click_othello_position_forced(positions["loser_ok"], positions["loser_ok_description"])
    time.sleep(OTHELLO_DELAY_BETWEEN_CONTINUE_CLICKS)

    print("[OTHELLO] Clicando em OK do ganhador")
    click_othello_position_forced(positions["winner_ok"], positions["winner_ok_description"])
    time.sleep(OTHELLO_DELAY_AFTER_CONTINUE)


def play_othello_match(
    winner_side,
    match_number=None,
    detected_positions=None,
    click_ok_before_match=False,
):
    """Executa uma partida de Othello fazendo o perdedor desistir."""
    if not validate_othello_config():
        return False

    if detected_positions is None:
        detected_positions = obter_posicoes_othello_cacheadas()

    if not detected_positions:
        return False

    positions = get_match_positions(winner_side, detected_positions)
    match_label = match_number if match_number is not None else 1

    print(f"\n[OTHELLO] Preparando partida {match_label}")
    print(f"[OTHELLO] Vencedor selecionado: {positions['winner_label']}")
    print(f"[OTHELLO] Perdedor: {positions['loser_label']}")
    countdown(OTHELLO_DELAY_BEFORE_START)

    if click_ok_before_match:
        print("[OTHELLO] Tela final inicial detectada. Clicando OKs antes da partida.")
        click_othello_result_ok(positions)

    click_othello_surrender(positions["surrender"], positions["surrender_description"])
    time.sleep(OTHELLO_DELAY_AFTER_SURRENDER)

    if OTHELLO_CONFIRMATION_ENABLED:
        click_othello_position_forced(positions["confirm"], positions["confirm_description"])
        time.sleep(OTHELLO_DELAY_AFTER_CONFIRM)

    print("[OTHELLO] Aguardando resultado...")
    time.sleep(OTHELLO_DELAY_AFTER_RESULT)

    click_othello_result_ok(positions)

    print(f"[OTHELLO] Partida {match_label} finalizada")
    return True


def run_othello_matches(winner_side, quantity):
    """Executa uma quantidade fixa de partidas."""
    global OTHELLO_POSITIONS_CACHE

    OTHELLO_POSITIONS_CACHE = None
    detected_positions = obter_posicoes_othello_cacheadas()

    if not detected_positions:
        return

    for match_number in range(1, quantity + 1):
        current_winner_side = winner_side_for_match(winner_side, match_number)

        if not play_othello_match(
            current_winner_side,
            match_number,
            detected_positions,
            click_ok_before_match=OTHELLO_START_FROM_FINAL_SCREEN and match_number == 1,
        ):
            break


def run_othello_infinite(winner_side):
    """Executa partidas ate o usuario interromper com Ctrl+C."""
    print("[OTHELLO] Pressione CTRL+C para interromper.")
    global OTHELLO_POSITIONS_CACHE

    OTHELLO_POSITIONS_CACHE = None
    detected_positions = obter_posicoes_othello_cacheadas()

    if not detected_positions:
        return

    match_number = 1

    try:
        while True:
            current_winner_side = winner_side_for_match(winner_side, match_number)

            if not play_othello_match(
                current_winner_side,
                match_number,
                detected_positions,
                click_ok_before_match=OTHELLO_START_FROM_FINAL_SCREEN and match_number == 1,
            ):
                break
            match_number += 1
    except KeyboardInterrupt:
        print("\n[OTHELLO] Loop infinito interrompido pelo usuario.")


def test_left_surrender():
    """Testa apenas o clique no Surrender da esquerda."""
    if not validate_othello_config():
        return

    positions = preparar_posicoes_othello()

    if not positions:
        return

    print("[OTHELLO] Teste: sera clicado somente o Surrender da esquerda.")
    countdown(OTHELLO_DELAY_BEFORE_START)
    click_othello_surrender(positions["left_surrender"], "Surrender da esquerda")
    print("[OTHELLO] Teste finalizado.")


def test_right_surrender():
    """Testa apenas o clique no Surrender da direita."""
    if not validate_othello_config():
        return

    positions = preparar_posicoes_othello()

    if not positions:
        return

    print("[OTHELLO] Teste: sera clicado somente o Surrender da direita.")
    countdown(OTHELLO_DELAY_BEFORE_START)
    click_othello_surrender(positions["right_surrender"], "Surrender da direita")
    print("[OTHELLO] Teste finalizado.")


def test_continue_buttons():
    """Testa os botoes OK, primeiro esquerda e depois direita."""
    if not validate_othello_config():
        return

    positions = preparar_posicoes_othello()

    if not positions:
        return

    print("[OTHELLO] Teste: botoes OK esquerda e direita.")
    countdown(OTHELLO_DELAY_BEFORE_START)
    click_othello_position_forced(positions["left_ok"], "OK da esquerda")
    time.sleep(OTHELLO_DELAY_BETWEEN_CONTINUE_CLICKS)
    click_othello_position_forced(positions["right_ok"], "OK da direita")
    print("[OTHELLO] Teste finalizado.")


def test_othello_board_detection():
    """Detecta tabuleiro e botoes calculados, sem clicar."""
    if not validate_othello_config():
        return

    positions = preparar_posicoes_othello()

    if not positions:
        return

    print("[OTHELLO] Deteccao concluida.")
    print(f"[OTHELLO] Surrender esquerda: X={positions['left_surrender'][0]} Y={positions['left_surrender'][1]}")
    print(f"[OTHELLO] Surrender direita: X={positions['right_surrender'][0]} Y={positions['right_surrender'][1]}")
    print(f"[OTHELLO] OK esquerda: X={positions['left_ok'][0]} Y={positions['left_ok'][1]}")
    print(f"[OTHELLO] OK direita: X={positions['right_ok'][0]} Y={positions['right_ok'][1]}")
