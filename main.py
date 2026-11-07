import ctypes
import time

import pydirectinput

from othello_bot import (
    play_othello_match,
    run_othello_infinite,
    run_othello_matches,
    test_continue_buttons,
    test_left_surrender,
    test_othello_board_detection,
    test_right_surrender,
)
from config import (
    AUTO_BOARD_MAX_CELL_SIZE,
    AUTO_BOARD_CLICK_MODE,
    AUTO_BOARD_CLICK_OFFSET,
    AUTO_BOARD_MIN_CELL_SIZE,
    AUTO_BOARD_OK_MODE,
    BOARD_CELL_SIZE,
    COORDINATE_MODE,
    DELAY_AFTER_MATCH,
    DELAY_AFTER_OK,
    DELAY_BETWEEN_OK_CLICKS,
    DELAY_BETWEEN_CLICKS,
    DELAY_AFTER_FOCUS_CLICK,
    FOCUS_CLICK_BEFORE_ACTION,
    LOSER_BOARD_MOVES,
    LOSER_BOARD_ORIGIN,
    LOSER_MOVES,
    LOSER_OK,
    LOSER_OK_RELATIVE,
    LOSER_OK_FROM_BOARD_OFFSET,
    LOSER_OK_FROM_BOARD_ORIGIN,
    LOSER_WINDOW_INDEX,
    MOUSE_DOWN_DURATION,
    OTHELLO_START_FROM_FINAL_SCREEN,
    MOVE_DURATION,
    ACTION_CLICKS_PER_POSITION,
    START_FROM_FINAL_SCREEN,
    START_DELAY,
    WINDOW_SORT_MODE,
    WINDOW_TITLE_KEYWORD,
    WINNER_BOARD_MOVES,
    WINNER_BOARD_ORIGIN,
    WINNER_MOVES,
    WINNER_OK,
    WINNER_OK_RELATIVE,
    WINNER_OK_FROM_BOARD_OFFSET,
    WINNER_OK_FROM_BOARD_ORIGIN,
    WINNER_WINDOW_INDEX,
)
from window_utils import (
    calcular_casa_tabuleiro,
    detectar_janelas_jogo,
    formatar_janela,
    somar_coordenada,
)


TOTAL_MOVES = 5
VK_ESCAPE = 0x1B
COORDENADAS_CACHE = None


class MacroCancelado(Exception):
    """Usada para interromper o macro com a tecla ESC."""


def validar_configuracao():
    """Valida se existem coordenadas suficientes para uma partida."""
    erros = []

    if COORDINATE_MODE == "absolute":
        if len(WINNER_MOVES) < TOTAL_MOVES:
            erros.append("WINNER_MOVES precisa ter pelo menos 5 posicoes.")

        if len(LOSER_MOVES) < TOTAL_MOVES:
            erros.append("LOSER_MOVES precisa ter pelo menos 5 posicoes.")
    elif COORDINATE_MODE in ("board_relative", "auto_board"):
        if len(WINNER_BOARD_MOVES) < TOTAL_MOVES:
            erros.append("WINNER_BOARD_MOVES precisa ter pelo menos 5 jogadas.")

        if len(LOSER_BOARD_MOVES) < TOTAL_MOVES:
            erros.append("LOSER_BOARD_MOVES precisa ter pelo menos 5 jogadas.")

        if BOARD_CELL_SIZE <= 0:
            erros.append("BOARD_CELL_SIZE precisa ser maior que zero.")

        if WINNER_WINDOW_INDEX == LOSER_WINDOW_INDEX:
            erros.append("WINNER_WINDOW_INDEX e LOSER_WINDOW_INDEX precisam ser diferentes.")

        if COORDINATE_MODE == "auto_board":
            if AUTO_BOARD_MIN_CELL_SIZE <= 0:
                erros.append("AUTO_BOARD_MIN_CELL_SIZE precisa ser maior que zero.")

            if AUTO_BOARD_MAX_CELL_SIZE < AUTO_BOARD_MIN_CELL_SIZE:
                erros.append("AUTO_BOARD_MAX_CELL_SIZE precisa ser maior ou igual ao minimo.")

            modos_ok_validos = ("detect_final_buttons", "gomoku_relative", "board_offset")

            if AUTO_BOARD_OK_MODE not in modos_ok_validos:
                erros.append(
                    'AUTO_BOARD_OK_MODE precisa ser "detect_final_buttons", '
                    '"gomoku_relative" ou "board_offset".'
                )
    else:
        erros.append('COORDINATE_MODE precisa ser "absolute", "board_relative" ou "auto_board".')

    if erros:
        print("\nErro na configuracao:")
        for erro in erros:
            print(f"- {erro}")
        print("Edite o arquivo config.py e tente novamente.")
        return False

    return True


def obter_janelas_configuradas():
    """Detecta as janelas do Angels e escolhe ganhador/perdedor por indice."""
    janelas = detectar_janelas_jogo(WINDOW_TITLE_KEYWORD, WINDOW_SORT_MODE)
    maior_indice = max(WINNER_WINDOW_INDEX, LOSER_WINDOW_INDEX)

    if len(janelas) <= maior_indice:
        print("\nNao encontrei janelas suficientes do jogo.")
        print(f"Filtro usado: {WINDOW_TITLE_KEYWORD}")
        print(f"Janelas encontradas: {len(janelas)}")

        for indice, janela in enumerate(janelas):
            print(formatar_janela(indice, janela))

        print("Confira WINDOW_TITLE_KEYWORD, WINNER_WINDOW_INDEX e LOSER_WINDOW_INDEX no config.py.")
        return None, None

    return janelas[WINNER_WINDOW_INDEX], janelas[LOSER_WINDOW_INDEX]


def carregar_detector_tabuleiro():
    """Carrega o detector visual apenas quando ele for necessario."""
    try:
        from board_detector import (
            coordenada_casa,
            coordenada_ok_por_tabuleiro,
            coordenada_relativa_origem_tabuleiro,
            detectar_ok_tela_final,
            detectar_tabuleiro,
            formatar_ok,
            formatar_tabuleiro,
        )
    except ImportError:
        print("\nA dependencia Pillow nao esta instalada.")
        print("Instale com: pip install -r requirements.txt")
        return None

    return {
        "coordenada_casa": coordenada_casa,
        "coordenada_ok_por_tabuleiro": coordenada_ok_por_tabuleiro,
        "coordenada_relativa_origem_tabuleiro": coordenada_relativa_origem_tabuleiro,
        "detectar_ok_tela_final": detectar_ok_tela_final,
        "detectar_tabuleiro": detectar_tabuleiro,
        "formatar_ok": formatar_ok,
        "formatar_tabuleiro": formatar_tabuleiro,
    }


def preparar_coordenadas():
    """Monta as coordenadas absolutas conforme o modo configurado."""
    if COORDINATE_MODE == "absolute":
        return WINNER_MOVES, LOSER_MOVES, WINNER_OK, LOSER_OK

    winner_window, loser_window = obter_janelas_configuradas()

    if not winner_window or not loser_window:
        return None

    print("\nJanelas selecionadas:")
    print(f"GANHADOR: {formatar_janela(WINNER_WINDOW_INDEX, winner_window)}")
    print(f"PERDEDOR: {formatar_janela(LOSER_WINDOW_INDEX, loser_window)}")

    if COORDINATE_MODE == "auto_board":
        return preparar_coordenadas_auto_board(winner_window, loser_window)

    winner_moves = [
        calcular_casa_tabuleiro(
            winner_window,
            WINNER_BOARD_ORIGIN,
            BOARD_CELL_SIZE,
            jogada,
        )
        for jogada in WINNER_BOARD_MOVES[:TOTAL_MOVES]
    ]

    loser_moves = [
        calcular_casa_tabuleiro(
            loser_window,
            LOSER_BOARD_ORIGIN,
            BOARD_CELL_SIZE,
            jogada,
        )
        for jogada in LOSER_BOARD_MOVES[:TOTAL_MOVES]
    ]

    winner_ok = somar_coordenada(winner_window, WINNER_OK_RELATIVE)
    loser_ok = somar_coordenada(loser_window, LOSER_OK_RELATIVE)

    return winner_moves, loser_moves, winner_ok, loser_ok


def obter_coordenadas_cacheadas():
    """Detecta coordenadas uma vez e reutiliza durante a execucao."""
    global COORDENADAS_CACHE

    if COORDENADAS_CACHE is None:
        COORDENADAS_CACHE = preparar_coordenadas()

    return COORDENADAS_CACHE


def preparar_coordenadas_auto_board(winner_window, loser_window):
    """Detecta o tabuleiro nas duas janelas e calcula os cliques."""
    detector = carregar_detector_tabuleiro()

    if not detector:
        return None

    print("\nDetectando tabuleiro do GANHADOR...")
    winner_board = detector["detectar_tabuleiro"](
        winner_window,
        AUTO_BOARD_MIN_CELL_SIZE,
        AUTO_BOARD_MAX_CELL_SIZE,
    )

    print("Detectando tabuleiro do PERDEDOR...")
    loser_board = detector["detectar_tabuleiro"](
        loser_window,
        AUTO_BOARD_MIN_CELL_SIZE,
        AUTO_BOARD_MAX_CELL_SIZE,
    )

    if not winner_board or not loser_board:
        print("\nNao foi possivel detectar o tabuleiro nas duas janelas.")
        print("Confira se o Gomoku esta aberto e visivel nas duas instancias.")
        print("Se a deteccao falhar, use COORDINATE_MODE = \"board_relative\".")
        return None

    print(detector["formatar_tabuleiro"]("GANHADOR", winner_board))
    print(detector["formatar_tabuleiro"]("PERDEDOR", loser_board))

    winner_moves = [
        detector["coordenada_casa"](
            winner_board,
            jogada,
            AUTO_BOARD_CLICK_MODE,
            AUTO_BOARD_CLICK_OFFSET,
        )
        for jogada in WINNER_BOARD_MOVES[:TOTAL_MOVES]
    ]
    loser_moves = [
        detector["coordenada_casa"](
            loser_board,
            jogada,
            AUTO_BOARD_CLICK_MODE,
            AUTO_BOARD_CLICK_OFFSET,
        )
        for jogada in LOSER_BOARD_MOVES[:TOTAL_MOVES]
    ]
    if AUTO_BOARD_OK_MODE == "detect_final_buttons":
        winner_ok_detectado = detector["detectar_ok_tela_final"](winner_window, winner_board)
        loser_ok_detectado = detector["detectar_ok_tela_final"](loser_window, loser_board)

        if not winner_ok_detectado or not loser_ok_detectado:
            print("\nNao foi possivel detectar os botoes OK/check na tela final.")
            print("Confira se as duas telas estao em YOU WIN/YOU LOSE.")
            print('Fallback: use AUTO_BOARD_OK_MODE = "gomoku_relative" e calibre manualmente.')
            return None

        print(detector["formatar_ok"]("OK GANHADOR", winner_ok_detectado))
        print(detector["formatar_ok"]("OK PERDEDOR", loser_ok_detectado))

        winner_ok = (winner_ok_detectado["abs_x"], winner_ok_detectado["abs_y"])
        loser_ok = (loser_ok_detectado["abs_x"], loser_ok_detectado["abs_y"])
    elif AUTO_BOARD_OK_MODE == "board_offset":
        winner_ok = detector["coordenada_ok_por_tabuleiro"](
            winner_board,
            WINNER_OK_FROM_BOARD_OFFSET,
        )
        loser_ok = detector["coordenada_ok_por_tabuleiro"](
            loser_board,
            LOSER_OK_FROM_BOARD_OFFSET,
        )
    else:
        winner_ok = detector["coordenada_relativa_origem_tabuleiro"](
            winner_board,
            WINNER_OK_FROM_BOARD_ORIGIN,
        )
        loser_ok = detector["coordenada_relativa_origem_tabuleiro"](
            loser_board,
            LOSER_OK_FROM_BOARD_ORIGIN,
        )

    return winner_moves, loser_moves, winner_ok, loser_ok


def verificar_cancelamento():
    """Cancela o macro se a tecla ESC estiver pressionada."""
    if ctypes.windll.user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
        raise MacroCancelado


def aguardar(segundos):
    """Espera alguns segundos, mas continua checando a tecla ESC."""
    fim = time.time() + segundos

    while time.time() < fim:
        verificar_cancelamento()
        time.sleep(0.05)


def clicar(nome, posicao):
    """Move ate uma coordenada absoluta da tela e executa um clique."""
    verificar_cancelamento()
    x, y = posicao
    print(f"Clicando {nome}: X={x}, Y={y}")
    pydirectinput.moveTo(x, y, duration=MOVE_DURATION)
    verificar_cancelamento()

    if FOCUS_CLICK_BEFORE_ACTION:
        print("  Clique de foco")
        pydirectinput.click()
        aguardar(DELAY_AFTER_FOCUS_CLICK)
        pydirectinput.moveTo(x, y, duration=MOVE_DURATION)
        verificar_cancelamento()

    for numero_clique in range(1, ACTION_CLICKS_PER_POSITION + 1):
        print(f"  Clique real {numero_clique}/{ACTION_CLICKS_PER_POSITION}")
        pydirectinput.mouseDown()
        aguardar(MOUSE_DOWN_DURATION)
        pydirectinput.mouseUp()

        if numero_clique < ACTION_CLICKS_PER_POSITION:
            aguardar(DELAY_AFTER_FOCUS_CLICK)


def aguardar_inicio():
    """Da tempo para o usuario focar/organizar as janelas do jogo."""
    print(f"A partida vai comecar em {START_DELAY} segundos.")
    aguardar(START_DELAY)


def executar_jogadas(winner_moves, loser_moves):
    """Executa as 5 jogadas do ganhador e as 5 jogadas do perdedor."""
    for indice in range(TOTAL_MOVES):
        jogada = indice + 1
        print(f"\nJogada {jogada}/{TOTAL_MOVES}")

        clicar("GANHADOR", winner_moves[indice])
        aguardar(DELAY_BETWEEN_CLICKS)

        clicar("PERDEDOR", loser_moves[indice])
        aguardar(DELAY_BETWEEN_CLICKS)


def clicar_ok(winner_ok, loser_ok):
    """Clica nos botoes OK das duas instancias depois da partida."""
    print(f"\nAguardando {DELAY_AFTER_MATCH} segundos antes de clicar OK.")
    aguardar(DELAY_AFTER_MATCH)

    clicar("OK do GANHADOR", winner_ok)
    aguardar(DELAY_BETWEEN_OK_CLICKS)

    clicar("OK do PERDEDOR", loser_ok)
    aguardar(DELAY_AFTER_OK)


def clicar_ok_inicial(winner_ok, loser_ok):
    """Clica OK nas duas telas finais antes de iniciar a primeira partida."""
    print("\nClicando OK inicial para sair da tela final.")
    clicar("OK inicial do GANHADOR", winner_ok)
    aguardar(DELAY_BETWEEN_OK_CLICKS)
    clicar("OK inicial do PERDEDOR", loser_ok)
    aguardar(DELAY_AFTER_OK)


def rodar_partida(numero_partida=1, aguardar_antes=True, clicar_ok_antes=False):
    """Executa uma partida completa."""
    if not validar_configuracao():
        return False

    coordenadas = obter_coordenadas_cacheadas()

    if not coordenadas:
        return False

    winner_moves, loser_moves, winner_ok, loser_ok = coordenadas

    try:
        print(f"\n=== Partida {numero_partida} ===")
        print("Pressione ESC para cancelar o macro.")
        if aguardar_antes:
            aguardar_inicio()
        if clicar_ok_antes:
            clicar_ok_inicial(winner_ok, loser_ok)
        executar_jogadas(winner_moves, loser_moves)
        clicar_ok(winner_ok, loser_ok)
        print(f"Partida {numero_partida} finalizada.")
        return True
    except MacroCancelado:
        print("\nMacro cancelado pela tecla ESC.")
        return False


def rodar_varias_partidas():
    """Pergunta quantas partidas devem ser executadas."""
    try:
        quantidade = int(input("Quantas partidas deseja rodar? ").strip())
    except ValueError:
        print("Digite um numero inteiro valido.")
        return

    if quantidade <= 0:
        print("A quantidade precisa ser maior que zero.")
        return

    for numero_partida in range(1, quantidade + 1):
        if not rodar_partida(
            numero_partida,
            aguardar_antes=numero_partida == 1,
            clicar_ok_antes=START_FROM_FINAL_SCREEN and numero_partida == 1,
        ):
            break


def rodar_infinito():
    """Executa partidas ate o usuario parar com Ctrl+C."""
    numero_partida = 1

    try:
        while True:
            if not rodar_partida(
                numero_partida,
                aguardar_antes=numero_partida == 1,
                clicar_ok_antes=START_FROM_FINAL_SCREEN and numero_partida == 1,
            ):
                break
            numero_partida += 1
    except (KeyboardInterrupt, MacroCancelado):
        print("\nLoop infinito interrompido pelo usuario.")


def testar_sequencia_sem_loop():
    """Testa somente a sequencia de jogadas, sem clicar nos botoes OK."""
    if not validar_configuracao():
        return

    coordenadas = obter_coordenadas_cacheadas()

    if not coordenadas:
        return

    winner_moves, loser_moves, _, _ = coordenadas

    print("\n=== Teste de sequencia sem loop ===")
    print("Este teste faz as 5 jogadas do ganhador e do perdedor.")
    print("Ele nao clica nos botoes OK no final.")
    try:
        print("Pressione ESC para cancelar o macro.")
        aguardar_inicio()
        executar_jogadas(winner_moves, loser_moves)
        print("\nTeste de sequencia finalizado.")
    except MacroCancelado:
        print("\nMacro cancelado pela tecla ESC.")


def listar_janelas_detectadas():
    """Mostra as janelas encontradas pelo filtro configurado."""
    janelas = detectar_janelas_jogo(WINDOW_TITLE_KEYWORD, WINDOW_SORT_MODE)

    print(f'\nJanelas encontradas com "{WINDOW_TITLE_KEYWORD}": {len(janelas)}')

    for indice, janela in enumerate(janelas):
        print(formatar_janela(indice, janela))

    if not janelas:
        print("Nenhuma janela encontrada. Confira se o jogo esta aberto e o titulo bate com o config.py.")


def testar_deteccao_tabuleiro():
    """Detecta e mostra o tabuleiro sem executar cliques."""
    detector = carregar_detector_tabuleiro()

    if not detector:
        return

    winner_window, loser_window = obter_janelas_configuradas()

    if not winner_window or not loser_window:
        return

    print("\nDetectando tabuleiros sem clicar...")
    winner_board = detector["detectar_tabuleiro"](
        winner_window,
        AUTO_BOARD_MIN_CELL_SIZE,
        AUTO_BOARD_MAX_CELL_SIZE,
    )
    loser_board = detector["detectar_tabuleiro"](
        loser_window,
        AUTO_BOARD_MIN_CELL_SIZE,
        AUTO_BOARD_MAX_CELL_SIZE,
    )

    if winner_board:
        print(detector["formatar_tabuleiro"]("GANHADOR", winner_board))
    else:
        print("GANHADOR: tabuleiro nao detectado.")

    if loser_board:
        print(detector["formatar_tabuleiro"]("PERDEDOR", loser_board))
    else:
        print("PERDEDOR: tabuleiro nao detectado.")


def testar_deteccao_tela_final():
    """Detecta tabuleiro e OK/check na tela final, sem clicar."""
    global COORDENADAS_CACHE

    COORDENADAS_CACHE = None
    coordenadas = obter_coordenadas_cacheadas()

    if not coordenadas:
        return

    _, _, winner_ok, loser_ok = coordenadas
    print("\nDeteccao de tela final concluida.")
    print(f"OK GANHADOR: X={winner_ok[0]}, Y={winner_ok[1]}")
    print(f"OK PERDEDOR: X={loser_ok[0]}, Y={loser_ok[1]}")


def rodar_partida_da_tela_final():
    """Roda uma partida assumindo que as duas janelas estao na tela final."""
    rodar_partida(numero_partida=1, aguardar_antes=True, clicar_ok_antes=True)


def mostrar_menu_gomoku():
    print("\n===== GOMOKU =====")
    print("1 - Rodar 1 partida")
    print("2 - Rodar varias partidas")
    print("3 - Rodar infinito")
    print("4 - Testar sequencia sem loop")
    print("5 - Listar janelas detectadas")
    print("6 - Testar deteccao do tabuleiro")
    print("7 - Testar deteccao da tela final")
    print("8 - Rodar 1 partida a partir da tela final")
    print("9 - Sair")


def menu_gomoku():
    while True:
        mostrar_menu_gomoku()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            rodar_partida(clicar_ok_antes=START_FROM_FINAL_SCREEN)
        elif opcao == "2":
            rodar_varias_partidas()
        elif opcao == "3":
            rodar_infinito()
        elif opcao == "4":
            testar_sequencia_sem_loop()
        elif opcao == "5":
            listar_janelas_detectadas()
        elif opcao == "6":
            testar_deteccao_tabuleiro()
        elif opcao == "7":
            testar_deteccao_tela_final()
        elif opcao == "8":
            rodar_partida_da_tela_final()
        elif opcao == "9":
            print("Voltando ao menu principal.")
            break
        else:
            print("Opcao invalida.")


def escolher_modo_execucao_othello(winner_side):
    """Pergunta como o usuario quer executar o Othello."""
    while True:
        print("\n===== OTHELLO - EXECUCAO =====")
        print("1 - Rodar 1 partida")
        print("2 - Rodar N partidas")
        print("3 - Rodar em loop infinito")
        print("4 - Voltar")

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            try:
                play_othello_match(
                    winner_side,
                    1,
                    click_ok_before_match=OTHELLO_START_FROM_FINAL_SCREEN,
                )
            except KeyboardInterrupt:
                print("\n[OTHELLO] Execucao interrompida pelo usuario.")
        elif opcao == "2":
            try:
                quantidade = int(input("Quantas partidas deseja rodar? ").strip())
            except ValueError:
                print("[OTHELLO] Digite um numero inteiro valido.")
                continue

            if quantidade <= 0:
                print("[OTHELLO] A quantidade precisa ser maior que zero.")
                continue

            try:
                run_othello_matches(winner_side, quantidade)
            except KeyboardInterrupt:
                print("\n[OTHELLO] Execucao interrompida pelo usuario.")
        elif opcao == "3":
            run_othello_infinite(winner_side)
        elif opcao == "4":
            break
        else:
            print("Opcao invalida.")


def menu_othello():
    while True:
        print("\n===== OTHELLO =====")
        print("1 - Instancia da esquerda ganha primeiro")
        print("2 - Instancia da direita ganha primeiro")
        print("3 - Testar clique no Surrender da esquerda")
        print("4 - Testar clique no Surrender da direita")
        print("5 - Testar botoes OK")
        print("6 - Testar deteccao do tabuleiro e botoes")
        print("7 - Voltar")

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            escolher_modo_execucao_othello("left")
        elif opcao == "2":
            escolher_modo_execucao_othello("right")
        elif opcao == "3":
            try:
                test_left_surrender()
            except KeyboardInterrupt:
                print("\n[OTHELLO] Teste interrompido pelo usuario.")
        elif opcao == "4":
            try:
                test_right_surrender()
            except KeyboardInterrupt:
                print("\n[OTHELLO] Teste interrompido pelo usuario.")
        elif opcao == "5":
            try:
                test_continue_buttons()
            except KeyboardInterrupt:
                print("\n[OTHELLO] Teste interrompido pelo usuario.")
        elif opcao == "6":
            test_othello_board_detection()
        elif opcao == "7":
            break
        else:
            print("Opcao invalida.")


def menu_testes_calibracao():
    while True:
        print("\n===== TESTES E CALIBRACAO =====")
        print("1 - Listar janelas detectadas")
        print("2 - Testar deteccao do tabuleiro Gomoku")
        print("3 - Testar deteccao da tela final Gomoku")
        print("4 - Testar deteccao do tabuleiro Othello")
        print("5 - Voltar")

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            listar_janelas_detectadas()
        elif opcao == "2":
            testar_deteccao_tabuleiro()
        elif opcao == "3":
            testar_deteccao_tela_final()
        elif opcao == "4":
            test_othello_board_detection()
        elif opcao == "5":
            break
        else:
            print("Opcao invalida.")


def mostrar_menu_principal():
    print("\n===== BOT DE MINI GAMES =====")
    print("1 - Gomoku")
    print("2 - Othello")
    print("3 - Testes e calibracao")
    print("4 - Sair")


def main():
    while True:
        mostrar_menu_principal()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            menu_gomoku()
        elif opcao == "2":
            menu_othello()
        elif opcao == "3":
            menu_testes_calibracao()
        elif opcao == "4":
            print("Saindo.")
            break
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()
