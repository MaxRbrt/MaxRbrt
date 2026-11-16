from aurora import (
  COR_CIANO,
  COR_TEXTO_2,
  COR_TURQUESA,
  COR_VERDE_CLARO,
  LARGURA_PAINEL,
  atraso,
  documentoSvg,
  numero,
  recorteDigitado,
  textoSvg,
)

# ============================================================
# 1. FONTE ASCII EM BLOCOS (ESTILO ANSI SHADOW)
# ============================================================

FONTE_BLOCOS: dict[str, list[str]] = {
  "M": ["███╗   ███╗", "████╗ ████║", "██╔████╔██║", "██║╚██╔╝██║", "██║ ╚═╝ ██║", "╚═╝     ╚═╝"],
  "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
  "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
  "C": [" ██████╗", "██╔════╝", "██║     ", "██║     ", "╚██████╗", " ╚═════╝"],
  "O": [" ██████╗ ", "██╔═══██╗", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
  "S": ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"],
  "B": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██████╔╝", "╚═════╝ "],
  "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
  "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
  " ": ["   "] * 6,
}

DIRECOES_MOLDURA = {
  "═": "ED",
  "║": "CB",
  "╗": "EB",
  "╔": "DB",
  "╝": "EC",
  "╚": "DC",
}

# ============================================================
# 2. MONTAGEM DAS LINHAS DE CARACTERES
# ============================================================


def montarLinhasAscii(texto: str) -> list[str]:
  linhas = [""] * 6
  for letra in texto.upper():
    desenho = FONTE_BLOCOS.get(letra)
    if desenho is None:
      raise ValueError(f"Letra \"{letra}\" sem desenho na fonte: esperado A-Z presente em FONTE_BLOCOS")
    for indice in range(6):
      linhas[indice] += desenho[indice]
  return linhas


# ============================================================
# 3. DESENHO DE CADA CÉLULA
# ============================================================


def segmentoDuplo(direcao: str, cx: float, cy: float, largura: float, altura: float) -> str:
  afastamento = 1.4
  meiaLargura = largura / 2
  meiaAltura = altura / 2
  if direcao == "E":
    pontos = (cx - meiaLargura, cy, cx, cy)
  elif direcao == "D":
    pontos = (cx, cy, cx + meiaLargura, cy)
  elif direcao == "C":
    pontos = (cx, cy - meiaAltura, cx, cy)
  else:
    pontos = (cx, cy, cx, cy + meiaAltura)
  x1, y1, x2, y2 = pontos
  horizontal = direcao in "ED"
  dx = 0 if horizontal else afastamento
  dy = afastamento if horizontal else 0
  primeiro = f"M{numero(x1 - dx)} {numero(y1 - dy)}L{numero(x2 - dx)} {numero(y2 - dy)}"
  segundo = f"M{numero(x1 + dx)} {numero(y1 + dy)}L{numero(x2 + dx)} {numero(y2 + dy)}"
  return primeiro + segundo


def desenharCelula(caractere: str, x: float, y: float, largura: float, altura: float) -> tuple[str, str]:
  if caractere == "█":
    bloco = (
      f'<rect x="{numero(x + .5)}" y="{numero(y + .7)}" width="{numero(largura - 1)}" '
      f'height="{numero(altura - 1.4)}" rx=".8"/>'
    )
    return bloco, ""
  direcoes = DIRECOES_MOLDURA.get(caractere, "")
  centroX = x + largura / 2
  centroY = y + altura / 2
  sombra = "".join(segmentoDuplo(direcao, centroX, centroY, largura, altura) for direcao in direcoes)
  return "", sombra


# ============================================================
# 4. COLUNAS ANIMADAS DE UMA LINHA DO WORDMARK
# ============================================================


def desenharLinhaWordmark(
  linhas: list[str], x0: float, y0: float, celula: float, idLinha: int, colunaInicial: int
) -> str:
  altura = celula * 2
  totalColunas = len(linhas[0])
  colunas = []
  for coluna in range(totalColunas):
    blocos = []
    sombras = []
    for indiceLinha, linha in enumerate(linhas):
      xCelula = x0 + coluna * celula
      yCelula = y0 + indiceLinha * altura
      bloco, sombra = desenharCelula(linha[coluna], xCelula, yCelula, celula, altura)
      blocos.append(bloco)
      sombras.append(sombra)
    conteudoBlocos = "".join(blocos)
    caminhoSombra = "".join(sombras)
    if not conteudoBlocos and not caminhoSombra:
      continue
    demora = 0.35 + (colunaInicial + coluna) * 0.014
    sombraSvg = f'<path d="{caminhoSombra}"/>' if caminhoSombra else ""
    colunas.append(
      f'<g class="coluna" {atraso(demora)}><g fill="url(#bloco{idLinha})">{conteudoBlocos}</g>'
      f'<g class="sombra">{sombraSvg}</g></g>'
    )
  gradiente = f"""<linearGradient id="bloco{idLinha}" gradientUnits="userSpaceOnUse" x1="0" y1="{numero(y0)}" x2="0" y2="{numero(y0 + 6 * altura)}">
<stop offset="0" stop-color="{COR_VERDE_CLARO}"/>
<stop offset=".55" stop-color="{COR_TURQUESA}"/>
<stop offset="1" stop-color="{COR_CIANO}"/>
</linearGradient>"""
  larguraArte = totalColunas * celula
  fimRevelacao = 0.35 + (colunaInicial + totalColunas) * 0.014
  cursor = (
    f'<rect class="cursor so-animado" x="{numero(x0)}" y="{numero(y0)}" width="{numero(celula)}" '
    f'height="{numero(6 * altura)}" fill="{COR_VERDE_CLARO}" '
    f'style="--fim:{numero(larguraArte)}px;animation-duration:{numero(fimRevelacao - 0.35 - colunaInicial * 0.014)}s;'
    f'animation-delay:{numero(0.35 + colunaInicial * 0.014)}s"/>'
  )
  return f'<defs>{gradiente}</defs><g filter="url(#brilho)">{"".join(colunas)}</g>{cursor}'


# ============================================================
# 5. PAINEL COMPLETO
# ============================================================

ESTILO_WORDMARK = f"""
.coluna{{opacity:0;animation:revelar .5s ease-out forwards}}
.sombra{{fill:none;stroke:{COR_TURQUESA};stroke-opacity:.5;stroke-width:.8}}
.cursor{{opacity:0;animation-name:cursorPassa;animation-timing-function:linear;animation-fill-mode:forwards}}
.varredura{{animation:varrer 6s linear 2.4s infinite;transform:translateX(-200px)}}
@keyframes revelar{{0%{{opacity:0;transform:translateY(-4px)}}100%{{opacity:1;transform:none}}}}
@keyframes cursorPassa{{0%{{opacity:.9;transform:translateX(0)}}92%{{opacity:.9}}100%{{opacity:0;transform:translateX(var(--fim))}}}}
@keyframes varrer{{0%{{transform:translateX(-200px)}}60%,100%{{transform:translateX({LARGURA_PAINEL + 40}px)}}}}
@media (prefers-reduced-motion:reduce){{.coluna{{opacity:1}}}}
"""


def faixaVarredura(y: float, altura: float) -> str:
  return f"""<defs><linearGradient id="feixe" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
<stop offset=".5" stop-color="{COR_VERDE_CLARO}" stop-opacity=".22"/>
<stop offset="1" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
</linearGradient></defs>
<rect class="varredura so-animado" x="0" y="{numero(y)}" width="160" height="{numero(altura)}" fill="url(#feixe)"/>"""


def comandoTerminal(usuario: str, rotulo: str) -> str:
  comando = f'{usuario.lower()}@github:~$ render --wordmark "{rotulo}"'
  largura = len(comando) * 11 * 0.62
  return f"""<defs>{recorteDigitado("recorteComando", 38, 22, largura + 4, 18, 0.1, 0.9)}</defs>
<text class="mono" x="40" y="35" font-size="11" fill="{COR_VERDE_CLARO}" fill-opacity=".7"
clip-path="url(#recorteComando)">{textoSvg(comando)}</text>"""


def gerarWordmark(usuario: str, nome: str, subtitulo: str, empilhado: bool) -> str:
  palavras = nome.upper().split() if empilhado else [nome.upper()]
  linhasPorPalavra = [montarLinhasAscii(palavra) for palavra in palavras]
  maiorLargura = max(len(linhas[0]) for linhas in linhasPorPalavra)
  celula = min(7.0, (LARGURA_PAINEL - 80) / maiorLargura)
  alturaArte = celula * 12
  espacoEntreLinhas = celula * 1.6
  partes = []
  colunaInicial = 0
  y = 56.0
  for indice, linhas in enumerate(linhasPorPalavra):
    largura = len(linhas[0]) * celula
    x0 = (LARGURA_PAINEL - largura) / 2
    partes.append(desenharLinhaWordmark(linhas, x0, y, celula, indice, colunaInicial))
    colunaInicial += len(linhas[0])
    y += alturaArte + espacoEntreLinhas
  alturaTotal = y - espacoEntreLinhas + 64
  inicioSubtitulo = 0.35 + colunaInicial * 0.014
  subtituloSvg = (
    f'<text class="mono surgir" {atraso(inicioSubtitulo)} x="{LARGURA_PAINEL / 2}" '
    f'y="{numero(alturaTotal - 28)}" font-size="12" letter-spacing="4" text-anchor="middle" '
    f'fill="{COR_TEXTO_2}">{textoSvg(subtitulo)}</text>'
  )
  corpo = (
    comandoTerminal(usuario, nome)
    + "".join(partes)
    + faixaVarredura(48, alturaTotal - 96)
    + subtituloSvg
  )
  titulo = f"Wordmark ASCII animado de {nome}"
  return documentoSvg(LARGURA_PAINEL, round(alturaTotal), titulo, corpo, ESTILO_WORDMARK)
