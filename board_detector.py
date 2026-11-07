from PIL import ImageGrab

from window_utils import somar_coordenada


def pixel_parece_linha(pixel):
    """Identifica pixels claros usados nas linhas da grade do Gomoku."""
    r, g, b = pixel[:3]
    brilho = (r + g + b) / 3
    diferenca = max(r, g, b) - min(r, g, b)

    linha_branca = brilho >= 155 and diferenca <= 95
    linha_ciano = g >= 135 and b >= 135 and r >= 80

    return linha_branca or linha_ciano


def pixel_parece_borda_botao(pixel):
    """Identifica pixels claros das bordas dos botoes OK/X."""
    r, g, b = pixel[:3]
    brilho = (r + g + b) / 3
    diferenca = max(r, g, b) - min(r, g, b)

    return brilho >= 145 and diferenca <= 100


def capturar_janela(janela):
    """Captura a imagem da janela usando coordenadas da area virtual do Windows."""
    virtual_left = _get_system_metric(76)
    virtual_top = _get_system_metric(77)

    imagem = ImageGrab.grab(all_screens=True)
    caixa = (
        janela["left"] - virtual_left,
        janela["top"] - virtual_top,
        janela["right"] - virtual_left,
        janela["bottom"] - virtual_top,
    )
    return imagem.crop(caixa).convert("RGB")


def _get_system_metric(indice):
    import ctypes

    return ctypes.windll.user32.GetSystemMetrics(indice)


def calcular_scores_linhas(imagem):
    """Conta pixels claros por coluna e linha."""
    largura, altura = imagem.size
    pixels = imagem.load()
    colunas = [0] * largura
    linhas = [0] * altura

    for y in range(altura):
        for x in range(largura):
            if pixel_parece_linha(pixels[x, y]):
                colunas[x] += 1
                linhas[y] += 1

    return colunas, linhas


def calcular_scores_continuos(imagem):
    """Calcula o maior trecho continuo de linha por coluna e por linha."""
    largura, altura = imagem.size
    pixels = imagem.load()
    colunas = [0] * largura
    linhas = [0] * altura

    for x in range(largura):
        atual = 0
        melhor = 0

        for y in range(altura):
            if pixel_parece_linha(pixels[x, y]):
                atual += 1
                melhor = max(melhor, atual)
            else:
                atual = 0

        colunas[x] = melhor

    for y in range(altura):
        atual = 0
        melhor = 0

        for x in range(largura):
            if pixel_parece_linha(pixels[x, y]):
                atual += 1
                melhor = max(melhor, atual)
            else:
                atual = 0

        linhas[y] = melhor

    return colunas, linhas


def agrupar_picos(scores, limite):
    """Agrupa linhas vizinhas que passaram do limite em um unico pico."""
    picos = []
    inicio = None
    soma_posicao = 0
    soma_peso = 0

    for indice, score in enumerate(scores):
        if score >= limite:
            if inicio is None:
                inicio = indice
                soma_posicao = 0
                soma_peso = 0

            peso = max(score, 1)
            soma_posicao += indice * peso
            soma_peso += peso
        elif inicio is not None:
            centro = round(soma_posicao / soma_peso)
            picos.append({"pos": centro, "score": soma_peso})
            inicio = None

    if inicio is not None:
        centro = round(soma_posicao / soma_peso)
        picos.append({"pos": centro, "score": soma_peso})

    return picos


def encontrar_sequencias_grade(scores, limite, min_cell, max_cell, min_hits=14, line_count=16):
    """Procura linhas quase igualmente espacadas."""
    picos = agrupar_picos(scores, limite)
    posicoes = [pico["pos"] for pico in picos]
    mapa_scores = {pico["pos"]: pico["score"] for pico in picos}
    melhores = []

    for tamanho_casa in range(min_cell, max_cell + 1):
        tolerancia = max(2, round(tamanho_casa * 0.15))

        for inicio in posicoes:
            acertos = 0
            erro_total = 0
            score_total = 0

            for indice in range(line_count):
                esperado = inicio + (indice * tamanho_casa)
                mais_proximo = encontrar_mais_proximo(posicoes, esperado, tolerancia)

                if mais_proximo is not None:
                    acertos += 1
                    erro_total += abs(mais_proximo - esperado)
                    score_total += mapa_scores.get(mais_proximo, 0)

            if acertos >= min_hits:
                melhores.append(
                    {
                        "start": inicio,
                        "cell": tamanho_casa,
                        "hits": acertos,
                        "error": erro_total,
                        "score": score_total,
                    }
                )

    melhores.sort(key=lambda item: (item["hits"], item["score"], -item["error"]), reverse=True)
    return melhores[:100]


def encontrar_mais_proximo(posicoes, valor, tolerancia):
    melhor = None
    melhor_distancia = tolerancia + 1

    for posicao in posicoes:
        distancia = abs(posicao - valor)

        if distancia <= tolerancia and distancia < melhor_distancia:
            melhor = posicao
            melhor_distancia = distancia

    return melhor


def pontuar_grade_generica(imagem, x_inicio, y_inicio, tamanho_casa, cell_count):
    """Confirma se as linhas verticais e horizontais se cruzam na mesma regiao."""
    largura, altura = imagem.size
    pixels = imagem.load()
    tamanho_tabuleiro = cell_count * tamanho_casa

    if x_inicio < 0 or y_inicio < 0:
        return 0

    if x_inicio + tamanho_tabuleiro >= largura or y_inicio + tamanho_tabuleiro >= altura:
        return 0

    total = 0

    for indice in range(cell_count + 1):
        x = x_inicio + (indice * tamanho_casa)
        y = y_inicio + (indice * tamanho_casa)

        for linha_y in range(y_inicio, y_inicio + tamanho_tabuleiro + 1):
            if pixel_parece_linha(pixels[x, linha_y]):
                total += 1

        for coluna_x in range(x_inicio, x_inicio + tamanho_tabuleiro + 1):
            if pixel_parece_linha(pixels[coluna_x, y]):
                total += 1

    return total


def pontuar_grade(imagem, x_inicio, y_inicio, tamanho_casa):
    """Confirma se a grade 15x15 do Gomoku esta na regiao."""
    return pontuar_grade_generica(imagem, x_inicio, y_inicio, tamanho_casa, 15)


def detectar_grade(
    janela,
    cell_count,
    min_cell,
    max_cell,
    min_hits,
    min_top,
    min_score=0,
    max_top=None,
    right_padding=0,
    require_right_buttons=False,
):
    """Detecta uma grade quadrada generica dentro da janela."""
    imagem = capturar_janela(janela)
    largura, altura = imagem.size
    colunas, linhas = calcular_scores_continuos(imagem)

    menor_tabuleiro = cell_count * min_cell
    limite_colunas = max(35, int(menor_tabuleiro * 0.45))
    limite_linhas = max(35, int(menor_tabuleiro * 0.45))

    line_count = cell_count + 1
    sequencias_x = encontrar_sequencias_grade(
        colunas,
        limite_colunas,
        min_cell,
        max_cell,
        min_hits=min_hits,
        line_count=line_count,
    )
    sequencias_y = encontrar_sequencias_grade(
        linhas,
        limite_linhas,
        min_cell,
        max_cell,
        min_hits=min_hits,
        line_count=line_count,
    )

    melhor = None

    for seq_x in sequencias_x:
        for seq_y in sequencias_y:
            if abs(seq_x["cell"] - seq_y["cell"]) > 2:
                continue

            tamanho_casa = round((seq_x["cell"] + seq_y["cell"]) / 2)

            if seq_y["start"] < min_top:
                continue

            if max_top is not None and seq_y["start"] > max_top:
                continue

            if seq_x["start"] + (cell_count * tamanho_casa) + right_padding >= largura:
                continue

            if seq_y["start"] + (cell_count * tamanho_casa) >= altura:
                continue

            if require_right_buttons:
                button_count = contar_botoes_ao_lado_da_grade(
                    imagem,
                    seq_x["start"],
                    seq_y["start"],
                    tamanho_casa,
                    cell_count,
                )

                if button_count < 2:
                    continue

            score = pontuar_grade_generica(
                imagem,
                seq_x["start"],
                seq_y["start"],
                tamanho_casa,
                cell_count,
            )

            if melhor is None or score > melhor["score"]:
                melhor = {
                    "left": seq_x["start"],
                    "top": seq_y["start"],
                    "cell": tamanho_casa,
                    "score": score,
                    "image_width": largura,
                    "image_height": altura,
                    "cell_count": cell_count,
                }

    if melhor is None:
        return None

    if melhor["score"] < min_score:
        return None

    tamanho_tabuleiro = cell_count * melhor["cell"]
    melhor["right"] = melhor["left"] + tamanho_tabuleiro
    melhor["bottom"] = melhor["top"] + tamanho_tabuleiro
    melhor["abs_left"], melhor["abs_top"] = somar_coordenada(
        janela,
        (melhor["left"], melhor["top"]),
    )
    melhor["abs_right"], melhor["abs_bottom"] = somar_coordenada(
        janela,
        (melhor["right"], melhor["bottom"]),
    )
    return melhor


def detectar_tabuleiro(janela, min_cell=10, max_cell=35):
    """Detecta o tabuleiro 15x15 do Gomoku dentro da janela do jogo."""
    return detectar_grade(janela, 15, min_cell, max_cell, min_hits=11, min_top=70)


def detectar_tabuleiro_othello(janela, min_cell=12, max_cell=45, surrender_offset=(30, -1)):
    """Detecta o tabuleiro 8x8 do Othello dentro da janela do jogo."""
    por_botoes = detectar_tabuleiro_othello_por_botoes(
        janela,
        min_cell,
        max_cell,
        surrender_offset,
    )

    if por_botoes:
        return por_botoes

    return detectar_grade(
        janela,
        8,
        min_cell,
        max_cell,
        min_hits=7,
        min_top=70,
        min_score=2500,
        max_top=130,
        right_padding=45,
        require_right_buttons=True,
    )


def detectar_tabuleiro_othello_por_botoes(janela, min_cell, max_cell, surrender_offset):
    """Infere a grade do Othello a partir dos botoes ao lado do tabuleiro."""
    imagem = capturar_janela(janela)
    largura, altura = imagem.size
    pixels = imagem.load()
    componentes = encontrar_componentes_botoes(pixels, 0, 60, largura, min(altura, 430))
    candidatos_botoes = []

    for comp in componentes:
        largura_comp = comp["right"] - comp["left"] + 1
        altura_comp = comp["bottom"] - comp["top"] + 1

        if 10 <= largura_comp <= 35 and 8 <= altura_comp <= 30 and comp["count"] >= 12:
            centro_x = round((comp["left"] + comp["right"]) / 2)
            centro_y = round((comp["top"] + comp["bottom"]) / 2)
            candidatos_botoes.append((centro_x, centro_y))

    melhor = None
    offset_x, offset_y = surrender_offset

    for botao_x, botao_y in candidatos_botoes:
        for ajuste_x in range(-2, 3):
            for ajuste_y in range(-2, 3):
                centro_x = botao_x + ajuste_x
                centro_y = botao_y + ajuste_y

                for tamanho_casa in range(min_cell, max_cell + 1):
                    board_right = centro_x - offset_x
                    board_bottom = centro_y - offset_y
                    board_left = board_right - (8 * tamanho_casa)
                    board_top = board_bottom - (8 * tamanho_casa)

                    if board_left < 0 or board_top < 70 or board_top > 130:
                        continue

                    if board_right + 45 >= largura or board_bottom >= altura:
                        continue

                    score = pontuar_grade_generica(
                        imagem,
                        board_left,
                        board_top,
                        tamanho_casa,
                        8,
                    )

                    if score < 2500:
                        continue

                    if melhor is None or score > melhor["score"]:
                        melhor = {
                            "left": board_left,
                            "top": board_top,
                            "cell": tamanho_casa,
                            "score": score,
                            "image_width": largura,
                            "image_height": altura,
                            "cell_count": 8,
                        }

    if melhor is None:
        return None

    tamanho_tabuleiro = 8 * melhor["cell"]
    melhor["right"] = melhor["left"] + tamanho_tabuleiro
    melhor["bottom"] = melhor["top"] + tamanho_tabuleiro
    melhor["abs_left"], melhor["abs_top"] = somar_coordenada(
        janela,
        (melhor["left"], melhor["top"]),
    )
    melhor["abs_right"], melhor["abs_bottom"] = somar_coordenada(
        janela,
        (melhor["right"], melhor["bottom"]),
    )
    return melhor


def contar_botoes_ao_lado_da_grade(imagem, x_inicio, y_inicio, tamanho_casa, cell_count):
    """Conta pequenos botoes retangulares a direita da grade."""
    largura, altura = imagem.size
    pixels = imagem.load()
    tamanho_tabuleiro = cell_count * tamanho_casa
    board_right = x_inicio + tamanho_tabuleiro
    board_bottom = y_inicio + tamanho_tabuleiro

    busca_left = max(0, board_right - 5)
    busca_top = max(0, board_bottom - 80)
    busca_right = min(largura, board_right + 75)
    busca_bottom = min(altura, board_bottom + 45)

    componentes = encontrar_componentes_botoes(
        pixels,
        busca_left,
        busca_top,
        busca_right,
        busca_bottom,
    )
    total = 0

    for comp in componentes:
        largura_comp = comp["right"] - comp["left"] + 1
        altura_comp = comp["bottom"] - comp["top"] + 1

        if 10 <= largura_comp <= 35 and 8 <= altura_comp <= 30 and comp["count"] >= 12:
            total += 1

    return total


def coordenada_casa(tabuleiro, jogada, modo_clique="intersection", offset=(0, 0)):
    """Converte linha/coluna 0-14 em coordenada absoluta de clique."""
    linha, coluna = jogada
    tamanho_casa = tabuleiro["cell"]

    if modo_clique == "cell_center":
        x = tabuleiro["abs_left"] + round((coluna + 0.5) * tamanho_casa)
        y = tabuleiro["abs_top"] + round((linha + 0.5) * tamanho_casa)
    else:
        x = tabuleiro["abs_left"] + round(coluna * tamanho_casa)
        y = tabuleiro["abs_top"] + round(linha * tamanho_casa)

    offset_x, offset_y = offset
    x += offset_x
    y += offset_y

    return x, y


def coordenada_ok_por_tabuleiro(tabuleiro, offset):
    """Calcula o OK/check a partir do canto inferior direito do tabuleiro."""
    offset_x, offset_y = offset
    return tabuleiro["abs_right"] + offset_x, tabuleiro["abs_bottom"] + offset_y


def coordenada_relativa_origem_tabuleiro(tabuleiro, coordenada_relativa):
    """Calcula uma coordenada absoluta a partir do canto superior esquerdo do tabuleiro."""
    x, y = coordenada_relativa
    return tabuleiro["abs_left"] + x, tabuleiro["abs_top"] + y


def coordenada_por_offset_tabuleiro(tabuleiro, offset):
    """Calcula uma coordenada absoluta a partir do canto inferior direito da grade."""
    offset_x, offset_y = offset
    return tabuleiro["abs_right"] + offset_x, tabuleiro["abs_bottom"] + offset_y


def detectar_ok_tela_final(janela, tabuleiro):
    """Detecta o botao OK/check na tela final do Gomoku.

    Na tela final existem dois botoes no canto inferior direito do Gomoku:
    OK/check a esquerda e surrender/X a direita. Este detector procura esses
    retangulos claros abaixo do tabuleiro e escolhe o mais a esquerda.
    """
    imagem = capturar_janela(janela)
    largura, altura = imagem.size
    pixels = imagem.load()
    board_width = tabuleiro["right"] - tabuleiro["left"]

    busca_left = max(0, tabuleiro["left"] + int(board_width * 0.70))
    busca_top = max(0, tabuleiro["bottom"] - 10)
    busca_right = min(largura, tabuleiro["right"] + 60)
    busca_bottom = min(altura, tabuleiro["bottom"] + 70)

    componentes = encontrar_componentes_botoes(
        pixels,
        busca_left,
        busca_top,
        busca_right,
        busca_bottom,
    )

    candidatos = []

    for comp in componentes:
        largura_comp = comp["right"] - comp["left"] + 1
        altura_comp = comp["bottom"] - comp["top"] + 1

        if not 14 <= largura_comp <= 36:
            continue

        if not 10 <= altura_comp <= 28:
            continue

        if comp["count"] < 20:
            continue

        candidatos.append(comp)

    if len(candidatos) < 2:
        candidatos = [
            comp
            for comp in componentes
            if 10 <= (comp["right"] - comp["left"] + 1) <= 45
            and 8 <= (comp["bottom"] - comp["top"] + 1) <= 35
            and comp["count"] >= 12
        ]

    if not candidatos:
        return None

    candidatos.sort(key=lambda comp: (comp["left"], comp["top"]))
    ok = candidatos[0]
    centro_x = round((ok["left"] + ok["right"]) / 2)
    centro_y = round((ok["top"] + ok["bottom"]) / 2)

    return {
        "left": ok["left"],
        "top": ok["top"],
        "right": ok["right"],
        "bottom": ok["bottom"],
        "abs_x": janela["left"] + centro_x,
        "abs_y": janela["top"] + centro_y,
        "rel_x": centro_x,
        "rel_y": centro_y,
        "count": ok["count"],
    }


def encontrar_componentes_botoes(pixels, left, top, right, bottom):
    """Encontra componentes conectados de pixels claros na regiao de busca."""
    largura = right - left
    altura = bottom - top

    if largura <= 0 or altura <= 0:
        return []

    visitado = set()
    componentes = []

    for y in range(top, bottom):
        for x in range(left, right):
            chave = (x, y)

            if chave in visitado:
                continue

            if not pixel_parece_borda_botao(pixels[x, y]):
                visitado.add(chave)
                continue

            fila = [chave]
            visitado.add(chave)
            comp_left = x
            comp_right = x
            comp_top = y
            comp_bottom = y
            count = 0

            while fila:
                atual_x, atual_y = fila.pop()
                count += 1
                comp_left = min(comp_left, atual_x)
                comp_right = max(comp_right, atual_x)
                comp_top = min(comp_top, atual_y)
                comp_bottom = max(comp_bottom, atual_y)

                for prox_x, prox_y in (
                    (atual_x - 1, atual_y),
                    (atual_x + 1, atual_y),
                    (atual_x, atual_y - 1),
                    (atual_x, atual_y + 1),
                ):
                    if prox_x < left or prox_x >= right or prox_y < top or prox_y >= bottom:
                        continue

                    prox_chave = (prox_x, prox_y)

                    if prox_chave in visitado:
                        continue

                    visitado.add(prox_chave)

                    if pixel_parece_borda_botao(pixels[prox_x, prox_y]):
                        fila.append(prox_chave)

            componentes.append(
                {
                    "left": comp_left,
                    "top": comp_top,
                    "right": comp_right,
                    "bottom": comp_bottom,
                    "count": count,
                }
            )

    return componentes


def formatar_tabuleiro(nome, tabuleiro):
    return (
        f"{nome}: board_rel=({tabuleiro['left']}, {tabuleiro['top']}) "
        f"cell={tabuleiro['cell']} "
        f"board_abs=({tabuleiro['abs_left']}, {tabuleiro['abs_top']}) "
        f"score={tabuleiro['score']}"
    )


def formatar_ok(nome, ok):
    return (
        f"{nome}: ok_rel=({ok['rel_x']}, {ok['rel_y']}) "
        f"ok_abs=({ok['abs_x']}, {ok['abs_y']}) "
        f"bbox=({ok['left']}, {ok['top']}, {ok['right']}, {ok['bottom']})"
    )
