# Modo de coordenadas:
#
# "absolute"
#   Usa as coordenadas absolutas WINNER_MOVES, LOSER_MOVES, WINNER_OK e LOSER_OK.
#   E o modo antigo, bom quando as janelas ficam sempre no mesmo lugar.
#
# "board_relative"
#   Detecta as janelas do Angels Online e calcula os cliques a partir da posicao
#   da janela + origem do tabuleiro + linha/coluna da casa.
#   E o modo recomendado para trocar de monitor, resolucao ou posicao da janela.
#
# "auto_board"
#   Detecta as janelas do Angels Online, captura a imagem de cada janela e tenta
#   encontrar automaticamente a grade 15x15 do Gomoku.
COORDINATE_MODE = "auto_board"


# Configuracao para detectar as janelas do Angels Online.
# O texto precisa aparecer no titulo da janela.
WINDOW_TITLE_KEYWORD = "Angels Online"

# Como ordenar as janelas detectadas:
# - "left_to_right": janela mais a esquerda vem primeiro.
# - "top_to_bottom": janela mais acima vem primeiro.
WINDOW_SORT_MODE = "left_to_right"

# Indices das janelas depois da ordenacao.
# Com duas janelas lado a lado, normalmente:
# 0 = esquerda
# 1 = direita
WINNER_WINDOW_INDEX = 0
LOSER_WINDOW_INDEX = 1


# Coordenadas absolutas da tela.
#
# Troque todos os valores abaixo pelas coordenadas encontradas com:
# python calibrar_mouse.py
#
# Importante:
# - As coordenadas podem ser positivas, grandes ou negativas.
# - Em setup com dois monitores, o Windows pode usar X/Y negativos.
# - Nao mova as janelas depois de calibrar.


# 5 posicoes que a conta GANHADORA vai clicar.
# Escolha uma sequencia que forme 5 pecas em linha:
# horizontal, vertical ou diagonal.
WINNER_MOVES = [
    (1527, 407),
    (1527, 386),
    (1527, 364),
    (1527, 340),
    (1527, 318),
]


# Pelo menos 5 posicoes que a conta PERDEDORA vai clicar.
# Escolha casas longe da sequencia do ganhador para nao bloquear.
LOSER_MOVES = [
    (2260, 412),
    (2240, 297),
    (2163, 214),
    (2260, 188),
    (2088, 190),
]


# Coordenada absoluta do botao OK/check na tela da conta ganhadora.
WINNER_OK = (1828, 469)


# Coordenada absoluta do botao OK/check na tela da conta perdedora.
LOSER_OK = (2272, 473)


# Configuracao do modo "board_relative".
#
# Primeiro calibre a coordenada relativa do centro da casa superior esquerda
# do tabuleiro em cada janela do jogo.
#
# Exemplo:
# Se o calibrador mostrar:
#   janela[0] relativo: X=22 Y=86
# entao use:
#   WINNER_BOARD_ORIGIN = (22, 86)
#
# O tamanho da casa costuma ficar perto de 22 ou 23 pixels, mas calibre no seu
# jogo medindo a distancia entre o centro de duas casas vizinhas.
WINNER_BOARD_ORIGIN = (22, 86)
LOSER_BOARD_ORIGIN = (22, 86)
BOARD_CELL_SIZE = 22


# Jogadas por linha/coluna, usando indice 0 a 14.
# (0, 0) = primeira linha, primeira coluna do tabuleiro.
# (14, 14) = ultima linha, ultima coluna.
WINNER_BOARD_MOVES = [
    (14, 0),
    (13, 0),
    (12, 0),
    (11, 0),
    (10, 0),
]

LOSER_BOARD_MOVES = [
    (14, 14),
    (9, 13),
    (5, 12),
    (3, 14),
    (3, 6),
]


# OK/check relativo a cada janela do Angels, usado no modo "board_relative".
WINNER_OK_RELATIVE = (410, 466)
LOSER_OK_RELATIVE = (410, 466)


# Configuracao do modo "auto_board".
#
# Intervalo de tamanho esperado de cada casa do tabuleiro, em pixels.
# Em janelas 800x600 costuma ser menor. Em janelas maiores costuma aumentar.
AUTO_BOARD_MIN_CELL_SIZE = 10
AUTO_BOARD_MAX_CELL_SIZE = 35


# Como clicar no OK/check no modo auto_board:
#
# "detect_final_buttons"
#   Recomendado para iniciar o bot a partir da tela final YOU WIN/YOU LOSE.
#   O bot detecta automaticamente os botoes OK/check nas duas janelas.
#
# "gomoku_relative"
#   Recomendado. O bot detecta o tabuleiro e usa uma coordenada relativa a ele.
#   Calibre uma vez usando a opcao 6 do menu, que mostra a posicao detectada
#   do tabuleiro. Depois use OK relativo ao canto superior esquerdo do tabuleiro.
#
# "board_offset"
#   Modo antigo. Calcula o OK a partir do canto inferior direito do tabuleiro.
AUTO_BOARD_OK_MODE = "detect_final_buttons"


# Se True, o bot assume que vai comecar com as duas janelas na tela final
# YOU WIN/YOU LOSE. Ele detecta os botoes OK/check, clica OK nas duas telas
# e entao inicia a proxima partida.
START_FROM_FINAL_SCREEN = True


# OK/check relativo ao canto superior esquerdo do tabuleiro detectado.
# Calibre pelo print/log do modo 6:
#   OK_REL_X = OK_ABS_X - BOARD_ABS_LEFT
#   OK_REL_Y = OK_ABS_Y - BOARD_ABS_TOP
#
# Exemplo em janela 800x600: o OK costuma ficar um pouco abaixo e perto
# do canto direito do tabuleiro.
WINNER_OK_FROM_BOARD_ORIGIN = (806, 535)
LOSER_OK_FROM_BOARD_ORIGIN = (225, 257)


# Modo antigo, usado apenas se AUTO_BOARD_OK_MODE = "board_offset".
WINNER_OK_FROM_BOARD_OFFSET = (-8, 26)
LOSER_OK_FROM_BOARD_OFFSET = (-8, 26)


# No Gomoku do Angels, a jogada normalmente e feita na intersecao das linhas,
# nao no centro do quadrado.
#
# Use:
# - "intersection": clica nas linhas/intersecoes da grade.
# - "cell_center": clica no centro dos quadrados.
AUTO_BOARD_CLICK_MODE = "intersection"


# Ajuste fino aplicado ao clique calculado no modo auto_board.
# Se o clique ficar um pouco para esquerda/direita/cima/baixo, ajuste aqui.
# Exemplo: (1, 0), (-1, 0), (0, 1), (0, -1)
AUTO_BOARD_CLICK_OFFSET = (0, 0)


# Tempo entre cada clique de jogada, em segundos.
DELAY_BETWEEN_CLICKS = 0.12


# Tempo antes da primeira partida comecar.
# Em varias partidas ou loop infinito, essa espera acontece apenas na primeira.
START_DELAY = 5.0


# Se True, o bot faz um clique inicial para focar a janela do jogo
# antes de tentar executar a jogada.
FOCUS_CLICK_BEFORE_ACTION = True


# Tempo depois do clique de foco, em segundos.
# Aumente se a janela demora para ficar ativa.
DELAY_AFTER_FOCUS_CLICK = 0.07


# Tempo que o bot segura o botao do mouse no clique real.
MOUSE_DOWN_DURATION = 0.03


# Tempo de espera depois da ultima jogada antes de clicar nos OKs.
DELAY_AFTER_MATCH = 0.05


# Tempo de espera depois dos OKs antes da proxima partida.
DELAY_AFTER_OK = 0.05


# Tempo entre clicar OK na tela ganhadora e clicar OK na tela perdedora.
DELAY_BETWEEN_OK_CLICKS = 0.02


# Duracao do movimento do mouse ate cada coordenada.
# Use 0 para movimento instantaneo.
MOVE_DURATION = 0.01


# Quantidade de cliques reais por coordenada, depois do clique de foco.
# Normalmente 1 e suficiente.
ACTION_CLICKS_PER_POSITION = 1


# ============================================================
# CONFIGURACOES DO OTHELLO
# ============================================================
#
# Todas as coordenadas abaixo sao exemplos ficticios.
# Calibre no seu computador usando:
# python calibrar_mouse.py
#
# As coordenadas podem ser positivas ou negativas, dependendo da posicao
# dos monitores no Windows.


# Botao Surrender da instancia esquerda e da instancia direita.
OTHELLO_LEFT_SURRENDER = (220, 450)
OTHELLO_RIGHT_SURRENDER = (1240, 450)


# Modo de coordenadas do Othello:
# - "manual": usa as coordenadas absolutas acima.
# - "auto_board": detecta a grade 8x8 do Othello e calcula os botoes.
OTHELLO_COORDINATE_MODE = "auto_board"


# Se True, o Othello deve ser iniciado com a tela final YOU WIN/YOU LOSE aberta.
# O bot detecta os botoes OK, clica OK do perdedor, depois OK do ganhador,
# e entao comeca o loop de partidas.
OTHELLO_START_FROM_FINAL_SCREEN = True


# Se True, alterna quem vence a cada partida.
# Isso tambem alterna quem clica em Surrender:
# partida 1: o perdedor escolhido desiste
# partida 2: o outro lado desiste
OTHELLO_ALTERNATE_WINNER = True


# Intervalo esperado do tamanho de cada casa do tabuleiro Othello.
OTHELLO_AUTO_MIN_CELL_SIZE = 12
OTHELLO_AUTO_MAX_CELL_SIZE = 45


# Indices das janelas usadas pelo Othello depois da ordenacao.
# Normalmente 0 = esquerda e 1 = direita.
OTHELLO_LEFT_WINDOW_INDEX = 0
OTHELLO_RIGHT_WINDOW_INDEX = 1


# Offsets a partir do canto inferior direito do tabuleiro Othello detectado.
# Pela interface do Angels, Pass, Surrender e OK ficam a direita/abaixo da grade.
# Ajuste estes valores se o clique ficar alguns pixels fora.
OTHELLO_PASS_FROM_BOARD_OFFSET = (30, -22)
OTHELLO_SURRENDER_FROM_BOARD_OFFSET = (30, -1)
OTHELLO_CONTINUE_FROM_BOARD_OFFSET = (30, -1)


# Botao de confirmacao da desistencia, se existir.
# Use somente se OTHELLO_CONFIRMATION_ENABLED = True.
OTHELLO_LEFT_CONFIRM = (220, 480)
OTHELLO_RIGHT_CONFIRM = (1240, 480)


# Botao para continuar depois da tela de resultado.
OTHELLO_LEFT_CONTINUE = (350, 430)
OTHELLO_RIGHT_CONTINUE = (1370, 430)


# Configure como True somente se o jogo mostrar confirmacao apos Surrender.
OTHELLO_CONFIRMATION_ENABLED = False


# Tempos do modo Othello, em segundos.
OTHELLO_DELAY_BEFORE_START = 0.0
OTHELLO_DELAY_AFTER_SURRENDER = 1.0
OTHELLO_DELAY_AFTER_CONFIRM = 1.0
OTHELLO_DELAY_AFTER_RESULT = 2.0
OTHELLO_DELAY_BETWEEN_CONTINUE_CLICKS = 0.3
OTHELLO_DELAY_AFTER_CONTINUE = 1.5


# Antes de clicar em Surrender, faz um clique de foco na mesma janela.
# Isso evita que o primeiro clique apenas selecione a janela sem acionar o botao.
OTHELLO_FOCUS_BEFORE_SURRENDER = True
OTHELLO_DELAY_AFTER_FOCUS = 0.07


# Clique real do Othello usando mouseDown/mouseUp, igual ao ajuste usado
# no Gomoku para jogos que ignoram pydirectinput.click() simples.
OTHELLO_MOUSE_DOWN_DURATION = 0.03
