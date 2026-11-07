# gomoku-bot

Bot em Python para automatizar mini games do Angels Online Global no Windows.

Modos disponiveis:

- Gomoku
- Othello

O projeto usa `pydirectinput` para clicar no jogo. O modo Othello pode detectar automaticamente a grade 8x8 para calcular os botoes ou usar coordenadas absolutas manuais como fallback. O modo Gomoku preserva as opcoes existentes, incluindo coordenadas absolutas, coordenadas relativas e deteccao simples do tabuleiro.

Nao usa OCR, OpenCV ou inteligencia artificial.

## 1. Visao geral

Abra duas instancias do Angels Online Global lado a lado, em dois monitores ou em area de trabalho estendida.

O menu principal e:

```text
===== BOT DE MINI GAMES =====

1 - Gomoku
2 - Othello
3 - Testes e calibracao
4 - Sair
```

Use `CTRL+C` para interromper loops pelo terminal. No Gomoku, `ESC` tambem cancela a macro durante a execucao.

## 2. Modo Gomoku

O Gomoku existente foi preservado.

Menu:

```text
===== GOMOKU =====

1 - Rodar 1 partida
2 - Rodar varias partidas
3 - Rodar infinito
4 - Testar sequencia sem loop
5 - Listar janelas detectadas
6 - Testar deteccao do tabuleiro
7 - Testar deteccao da tela final
8 - Rodar 1 partida a partir da tela final
9 - Sair
```

O fluxo recomendado no modo `auto_board` e:

1. Jogue manualmente ate aparecer `YOU WIN` e `YOU LOSE`.
2. Use `7 - Testar deteccao da tela final`.
3. Se detectar os botoes OK, use `8 - Rodar 1 partida a partir da tela final`.
4. Depois use varias partidas ou modo infinito.

Configuracao principal do Gomoku em `config.py`:

```python
COORDINATE_MODE = "auto_board"
AUTO_BOARD_OK_MODE = "detect_final_buttons"
START_FROM_FINAL_SCREEN = True
```

As jogadas do Gomoku continuam por linha/coluna:

```python
WINNER_BOARD_MOVES = [
    (14, 0),
    (13, 0),
    (12, 0),
    (11, 0),
    (10, 0),
]
```

## 3. Modo Othello

No Othello, o bot nao joga o tabuleiro. Ele faz a conta perdedora clicar em `Surrender`, fazendo a outra conta vencer.

Menu:

```text
===== OTHELLO =====

1 - Instancia da esquerda ganha primeiro
2 - Instancia da direita ganha primeiro
3 - Testar clique no Surrender da esquerda
4 - Testar clique no Surrender da direita
5 - Testar botoes OK
6 - Testar deteccao do tabuleiro e botoes
7 - Voltar
```

Configuracao recomendada:

```python
OTHELLO_COORDINATE_MODE = "auto_board"
OTHELLO_START_FROM_FINAL_SCREEN = True
OTHELLO_ALTERNATE_WINNER = True
OTHELLO_AUTO_MIN_CELL_SIZE = 12
OTHELLO_AUTO_MAX_CELL_SIZE = 45

OTHELLO_PASS_FROM_BOARD_OFFSET = (30, -22)
OTHELLO_SURRENDER_FROM_BOARD_OFFSET = (30, -1)
OTHELLO_CONTINUE_FROM_BOARD_OFFSET = (30, -1)
```

No modo `auto_board`, o bot detecta a grade 8x8 do Othello e tambem tenta detectar os botoes OK/check na tela final `YOU WIN` / `YOU LOSE`.

Fluxo recomendado:

1. Jogue manualmente uma partida ate aparecer `YOU WIN` em uma janela e `YOU LOSE` na outra.
2. Deixe essa tela final aberta.
3. Rode a deteccao do Othello.
4. Inicie o bot.

Com `OTHELLO_START_FROM_FINAL_SCREEN = True`, a primeira acao do bot sera clicar nos OKs da tela final para iniciar a proxima partida.

Com `OTHELLO_ALTERNATE_WINNER = True`, o bot alterna o vencedor a cada partida. Se a esquerda vencer primeiro, a direita clica em `Surrender` na primeira partida; na segunda, a esquerda clica em `Surrender`; na terceira, a direita novamente.

Depois de escolher o vencedor:

```text
1 - Rodar 1 partida
2 - Rodar N partidas
3 - Rodar em loop infinito
4 - Voltar
```

Fluxo de uma partida Othello:

1. Se estiver na tela final inicial, clica no OK do perdedor e depois no OK do ganhador.
2. Faz um clique de foco na janela perdedora.
3. Clica no `Surrender` da conta perdedora.
4. Se configurado, clica na confirmacao da desistencia.
5. Aguarda a tela de resultado.
6. Clica no OK do perdedor.
7. Clica no OK do ganhador.
8. Aguarda reiniciar e repete.

Se a esquerda deve ganhar, a direita clica em `Surrender`.

Se a direita deve ganhar, a esquerda clica em `Surrender`.

## 4. Instalacao

Instale o Python em:

```text
https://www.python.org/downloads/
```

Durante a instalacao, marque:

```text
Add Python to PATH
```

Confira:

```bash
python --version
```

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

## 5. Teste de clique

Antes de usar o bot, confirme que o jogo aceita cliques do `pydirectinput`:

```bash
python teste_clique.py
```

Coloque o mouse sobre um ponto seguro do jogo. O script espera 5 segundos e clica.

Se nao clicar no jogo, abra o VS Code, CMD ou PowerShell como administrador e teste novamente.

## 6. Calibracao do Gomoku

Para coordenadas manuais:

```bash
python calibrar_mouse.py
```

Anote:

- 5 posicoes da conta ganhadora.
- 5 posicoes seguras da conta perdedora.
- OK/check da conta vencedora.
- OK/check da conta perdedora.

No modo `auto_board`, o bot tenta detectar o tabuleiro e os botoes finais. Ainda assim, deixe o tabuleiro visivel e sem janelas internas cobrindo.

## 7. Calibracao do Othello

O modo recomendado e `auto_board`.

1. Abra as duas instancias do Angels Online.
2. Posicione as janelas.
3. Jogue uma partida de Othello ate aparecer `YOU WIN` e `YOU LOSE`.
4. Deixe essa tela final aberta para o bot detectar os botoes OK.
5. Rode:

```bash
python main.py
```

6. Escolha:

```text
2 - Othello
6 - Testar deteccao do tabuleiro e botoes
```

Se funcionar, o terminal mostra as coordenadas calculadas:

```text
[OTHELLO] Surrender esquerda: X=... Y=...
[OTHELLO] Surrender direita: X=... Y=...
[OTHELLO] OK esquerda: X=... Y=...
[OTHELLO] OK direita: X=... Y=...
```

Se a deteccao automatica nao funcionar no seu layout, use fallback manual:

```python
OTHELLO_COORDINATE_MODE = "manual"
```

Depois execute:

```bash
python calibrar_mouse.py
```

Mova o mouse ate cada ponto e pressione `ENTER` para registrar.
Ao sair com `CTRL+C`, copie os pontos exibidos.

Anote:

- Surrender da esquerda.
- Surrender da direita.
- Confirmacao da esquerda, se existir.
- Confirmacao da direita, se existir.
- OK/check final da esquerda.
- OK/check final da direita.

Preencha no `config.py`:

```python
OTHELLO_LEFT_SURRENDER = (220, 450)
OTHELLO_RIGHT_SURRENDER = (1240, 450)

OTHELLO_LEFT_CONFIRM = (220, 480)
OTHELLO_RIGHT_CONFIRM = (1240, 480)

OTHELLO_LEFT_CONTINUE = (350, 430)   # OK/check final da esquerda
OTHELLO_RIGHT_CONTINUE = (1370, 430) # OK/check final da direita

OTHELLO_CONFIRMATION_ENABLED = False
```

Use `OTHELLO_CONFIRMATION_ENABLED = True` somente se aparecer uma confirmacao depois de clicar em `Surrender`.

As coordenadas podem ser negativas se o monitor estiver a esquerda do monitor principal.

## 8. Execucao

Rode:

```bash
python main.py
```

Para Othello, siga esta ordem:

1. Jogue manualmente ate a tela `YOU WIN` / `YOU LOSE`.
2. `2 - Othello`
3. `6 - Testar deteccao do tabuleiro e botoes`
4. `5 - Testar botoes OK`
5. Escolha quem ganha primeiro.
6. Rode somente 1 partida.
7. Depois teste N partidas ou loop infinito.

Nao mova as janelas depois de calibrar. Nao altere a resolucao depois de calibrar.

## 9. Compilacao

Com o ambiente virtual ativo:

```bash
pip install pyinstaller
pyinstaller --onefile --name MiniGameBot main.py
```

O executavel ficara em:

```text
dist\MiniGameBot.exe
```

Execute pelo terminal para ver os logs:

```bash
dist\MiniGameBot.exe
```

## 10. Solucao de problemas

Se nao clicar no jogo:

- Abra o VS Code, CMD ou PowerShell como administrador.
- Deixe o jogo em modo janela ou janela sem bordas.
- Clique manualmente na janela do jogo antes de iniciar o bot.
- Rode `python teste_clique.py`.

Se os cliques errarem:

- Rode `python calibrar_mouse.py`.
- Recalibre as coordenadas.
- Nao mova as janelas depois de calibrar.
- Use a mesma resolucao de tela.

No Othello, o bot faz um clique de foco antes do Surrender:

```python
OTHELLO_FOCUS_BEFORE_SURRENDER = True
OTHELLO_DELAY_AFTER_FOCUS = 0.07
OTHELLO_DELAY_BEFORE_START = 0.0
OTHELLO_MOUSE_DOWN_DURATION = 0.03
```

O clique real usa `pydirectinput.mouseDown()` e `pydirectinput.mouseUp()`, porque alguns jogos ignoram `pydirectinput.click()` simples.

Se o jogo estiver lento:

- Aumente os delays no `config.py`.
- No Othello, ajuste `OTHELLO_DELAY_AFTER_SURRENDER`, `OTHELLO_DELAY_AFTER_RESULT` e `OTHELLO_DELAY_AFTER_CONTINUE`.

Se a confirmacao de Surrender aparecer no Othello:

```python
OTHELLO_CONFIRMATION_ENABLED = True
```

Se nao aparecer:

```python
OTHELLO_CONFIRMATION_ENABLED = False
```
