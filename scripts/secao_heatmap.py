import math
from dataclasses import dataclass

from dados_github import DiaContribuicao
from aurora import (
  COR_TEXTO,
  COR_TEXTO_2,
  COR_TURQUESA,
  COR_VERDE_CLARO,
  LARGURA_PAINEL,
  atraso,
  cabecalhoPainel,
  documentoSvg,
  numero,
  textoSvg,
)

# ============================================================
# 1. GRADE DO CALENDÁRIO
# ============================================================

CORES_NIVEL = ["#161B22", "#0E4A43", "#14806F", "#34D399", "#6EE7B7"]
CELULA = 11
PASSO = 14
GRADE_X = 64
GRADE_Y = 106
ALTURA_PAINEL = 252
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


@dataclass
class CelulaGrade:
  coluna: int
  linha: int
  nivel: int
  quantidade: int
  data: str

  @property
  def x(self) -> float:
    return GRADE_X + self.coluna * PASSO

  @property
  def y(self) -> float:
    return GRADE_Y + self.linha * PASSO


def montarCelulas(semanas: list[list[DiaContribuicao]]) -> list[CelulaGrade]:
  return [
    CelulaGrade(coluna, dia.diaSemana, dia.nivel, dia.quantidade, dia.data)
    for coluna, semana in enumerate(semanas)
    for dia in semana
  ]


def desenharCelula(celula: CelulaGrade, nivel: int, extra: str = "") -> str:
  borda = ' stroke="#1F2A33"' if nivel == 0 else ""
  return (
    f'<rect x="{celula.x}" y="{celula.y}" width="{CELULA}" height="{CELULA}" rx="2.5" '
    f'fill="{CORES_NIVEL[nivel]}"{borda}{extra}/>'
  )


def rotulosEixos(semanas: list[list[DiaContribuicao]]) -> str:
  partes = []
  mesAnterior = ""
  for coluna, semana in enumerate(semanas):
    mes = semana[0].data[5:7]
    pertoDoFim = coluna > len(semanas) - 3
    if mes != mesAnterior and not pertoDoFim:
      x = GRADE_X + coluna * PASSO
      partes.append(f'<text x="{x}" y="{GRADE_Y - 9}">{MESES[int(mes) - 1]}</text>')
    mesAnterior = mes
  for linha, nome in ((1, "Seg"), (3, "Qua"), (5, "Sex")):
    partes.append(f'<text x="{GRADE_X - 30}" y="{GRADE_Y + linha * PASSO + 9}">{nome}</text>')
  return f'<g class="mono surgir" font-size="10" fill="{COR_TEXTO_2}">{"".join(partes)}</g>'


def legendaNiveis(modo: str) -> str:
  inicio = LARGURA_PAINEL - 40 - 5 * PASSO - 76
  quadrados = "".join(
    f'<rect x="{inicio + 40 + indice * PASSO}" y="221" width="{CELULA}" height="{CELULA}" rx="2.5" fill="{cor}"/>'
    for indice, cor in enumerate(CORES_NIVEL)
  )
  return f"""<g class="mono surgir" {atraso(.6)} font-size="10" fill="{COR_TEXTO_2}">
<text x="{inicio}" y="230">Menos</text>{quadrados}
<text x="{inicio + 40 + 5 * PASSO + 4}" y="230">Mais</text>
<text x="40" y="230"><tspan fill="{COR_TURQUESA}">●</tspan> modo: {textoSvg(modo)}</text>
</g>"""


def montarPainelHeatmap(
  semanas: list[list[DiaContribuicao]], total: int, modo: str, conteudo: str, estilo: str, titulo: str
) -> str:
  cabecalho = cabecalhoPainel(
    "ATIVIDADE DE CONTRIBUIÇÕES", f"{total} contribuições no último ano", f"> heatmap --style {modo}", LARGURA_PAINEL
  )
  corpo = cabecalho + rotulosEixos(semanas) + conteudo + legendaNiveis(modo)
  return documentoSvg(LARGURA_PAINEL, ALTURA_PAINEL, titulo, corpo, estilo)


# ============================================================
# 2. MODO JATO: AVIÃO CRUZA A GRADE E ACENDE AS COLUNAS
# ============================================================

CICLO_JATO = 9.0
FRACAO_TRAVESSIA = .8
LINHA_ALTA = 1
LINHA_BAIXA = 5


def tempoJatoNaColuna(coluna: int, totalColunas: int) -> float:
  inicioX = GRADE_X - 60
  fimX = GRADE_X + totalColunas * PASSO + 60
  centro = GRADE_X + coluna * PASSO + CELULA / 2
  return (centro - inicioX) / (fimX - inicioX) * CICLO_JATO * FRACAO_TRAVESSIA


def linhaDoJato(tempo: float) -> int:
  meioPeriodo = CICLO_JATO / 4
  fase = (1 - math.cos(math.pi * tempo / meioPeriodo)) / 2
  return round(LINHA_ALTA + fase * (LINHA_BAIXA - LINHA_ALTA))


def estiloJato(totalColunas: int) -> str:
  inicioX = GRADE_X - 60
  fimX = GRADE_X + totalColunas * PASSO + 60
  yAlto = GRADE_Y + LINHA_ALTA * PASSO + CELULA / 2
  yBaixo = GRADE_Y + LINHA_BAIXA * PASSO + CELULA / 2
  fimTravessia = numero(FRACAO_TRAVESSIA * 100)
  return f"""
.voo{{animation:voar {CICLO_JATO}s linear infinite}}
.onda{{animation:ondular {numero(CICLO_JATO / 4)}s ease-in-out infinite alternate}}
.feixe{{opacity:0;animation:feixe {CICLO_JATO}s linear infinite}}
.acerto{{opacity:0;animation:acerto {CICLO_JATO}s ease-out infinite}}
.chama{{animation:piscar .18s steps(1) infinite}}
@keyframes voar{{0%{{transform:translateX({inicioX}px);opacity:1}}{fimTravessia}%{{transform:translateX({fimX}px);opacity:1}}
{numero(FRACAO_TRAVESSIA * 100 + .1)}%,100%{{transform:translateX({fimX}px);opacity:0}}}}
@keyframes ondular{{from{{transform:translateY({numero(yAlto)}px)}}to{{transform:translateY({numero(yBaixo)}px)}}}}
@keyframes feixe{{0%{{opacity:.28}}7%,100%{{opacity:0}}}}
@keyframes acerto{{0%{{opacity:1}}14%,100%{{opacity:0}}}}
"""


def desenharAviao() -> str:
  return f"""<g class="voo so-animado"><g class="onda">
<line x1="-150" y1="0" x2="-14" y2="0" stroke="url(#rastro)" stroke-width="2" stroke-linecap="round"/>
<path class="chama" d="M-13 -2.2 L-21 0 L-13 2.2 Z" fill="{COR_VERDE_CLARO}"/>
<g filter="url(#brilho)">
<path d="M15 0 L-11 -4 L-8 0 L-11 4 Z" fill="{COR_TEXTO}"/>
<path d="M1 -1.5 L-5 -12 L-9 -12 L-5 -1.5 Z M1 1.5 L-5 12 L-9 12 L-5 1.5 Z" fill="{COR_TURQUESA}"/>
<path d="M-8 -1 L-13 -6 L-15 -6 L-12 -1 Z M-8 1 L-13 6 L-15 6 L-12 1 Z" fill="{COR_TURQUESA}" fill-opacity=".8"/>
</g></g></g>"""


def gerarHeatmapJato(semanas: list[list[DiaContribuicao]], total: int) -> str:
  celulas = montarCelulas(semanas)
  totalColunas = len(semanas)
  grade = "".join(desenharCelula(celula, celula.nivel) for celula in celulas)
  efeitos = []
  for coluna in range(totalColunas):
    tempo = tempoJatoNaColuna(coluna, totalColunas)
    x = GRADE_X + coluna * PASSO
    linha = linhaDoJato(tempo)
    efeitos.append(
      f'<rect class="feixe so-animado" {atraso(tempo)} x="{x - 1}" y="{GRADE_Y - 2}" width="{CELULA + 2}" '
      f'height="{7 * PASSO + 1}" rx="3" fill="{COR_TURQUESA}"/>'
      f'<rect class="acerto so-animado" {atraso(tempo)} x="{x}" y="{GRADE_Y + linha * PASSO}" '
      f'width="{CELULA}" height="{CELULA}" rx="2.5" fill="{COR_VERDE_CLARO}"/>'
    )
  rastro = f"""<defs><linearGradient id="rastro" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
<stop offset="1" stop-color="{COR_VERDE_CLARO}" stop-opacity=".85"/>
</linearGradient></defs>"""
  conteudo = (
    rastro
    + f'<g class="surgir" {atraso(.2)}>{grade}</g>'
    + f'<g filter="url(#brilho)">{"".join(efeitos)}</g>'
    + desenharAviao()
  )
  titulo = f"Calendário de contribuições animado com um jato: {total} contribuições no último ano"
  return montarPainelHeatmap(semanas, total, "jato", conteudo, estiloJato(totalColunas), titulo)


# ============================================================
# 3. MODO COBRA: PERCORRE A GRADE E COME AS CONTRIBUIÇÕES
# ============================================================

PASSO_COBRA = .045
PAUSA_COBRA = 2.0
SEGMENTOS_COBRA = 7


def percursoSerpentina(celulas: list[CelulaGrade]) -> list[CelulaGrade]:
  porColuna: dict[int, list[CelulaGrade]] = {}
  for celula in celulas:
    porColuna.setdefault(celula.coluna, []).append(celula)
  percurso = []
  for coluna in sorted(porColuna):
    ordenadas = sorted(porColuna[coluna], key=lambda celula: celula.linha)
    descendo = coluna % 2 == 0
    percurso.extend(ordenadas if descendo else list(reversed(ordenadas)))
  return percurso


def caminhoCobra(percurso: list[CelulaGrade]) -> str:
  pontos = [f"{numero(celula.x + CELULA / 2)} {numero(celula.y + CELULA / 2)}" for celula in percurso]
  return "M" + " L".join(pontos)


def segmentosCobra(caminho: str, ciclo: float, fracaoMovimento: float) -> str:
  partes = []
  for indice in range(SEGMENTOS_COBRA):
    tamanho = 10 if indice == 0 else 9 - indice * .6
    cor = COR_VERDE_CLARO if indice == 0 else COR_TURQUESA
    opacidade = 1 if indice == 0 else 1 - indice * .1
    inicio = indice * PASSO_COBRA
    partes.append(f"""<rect x="{numero(-tamanho / 2)}" y="{numero(-tamanho / 2)}" width="{numero(tamanho)}" height="{numero(tamanho)}"
rx="2.5" fill="{cor}" opacity="0">
<set attributeName="opacity" to="{numero(opacidade)}" begin="{numero(inicio)}s"/>
<animateMotion path="{caminho}" dur="{numero(ciclo)}s" begin="{numero(inicio)}s" repeatCount="indefinite"
keyPoints="0;1;1" keyTimes="0;{numero(fracaoMovimento)};1" calcMode="linear"/>
</rect>""")
  return f'<g filter="url(#brilho)">{"".join(reversed(partes))}</g>'


def celulaComida(celula: CelulaGrade, indice: int, ciclo: float) -> str:
  instante = indice * PASSO_COBRA / ciclo
  depois = min(instante + .004, .96)
  animacao = (
    f'<animate attributeName="opacity" values="1;1;.12;.12;1" '
    f'keyTimes="0;{numero(round(instante, 4))};{numero(round(depois, 4))};.97;1" '
    f'dur="{numero(ciclo)}s" repeatCount="indefinite"/>'
  )
  return (
    f'<rect x="{celula.x}" y="{celula.y}" width="{CELULA}" height="{CELULA}" rx="2.5" '
    f'fill="{CORES_NIVEL[celula.nivel]}">{animacao}</rect>'
  )


def gerarHeatmapCobra(semanas: list[list[DiaContribuicao]], total: int) -> str:
  celulas = montarCelulas(semanas)
  percurso = percursoSerpentina(celulas)
  tempoMovimento = len(percurso) * PASSO_COBRA
  ciclo = tempoMovimento + PAUSA_COBRA
  fundo = "".join(desenharCelula(celula, 0) for celula in celulas)
  comidas = "".join(
    celulaComida(celula, indice, ciclo) for indice, celula in enumerate(percurso) if celula.nivel > 0
  )
  conteudo = (
    f'<g class="surgir">{fundo}{comidas}</g>'
    + f'<g class="so-animado">{segmentosCobra(caminhoCobra(percurso), ciclo, tempoMovimento / ciclo)}</g>'
  )
  titulo = f"Calendário de contribuições com uma cobra que percorre a grade: {total} contribuições no último ano"
  return montarPainelHeatmap(semanas, total, "cobra", conteudo, "", titulo)


# ============================================================
# 4. MODO BORRACHA: APAGA E REDESENHA A ATIVIDADE
# ============================================================

CICLO_BORRACHA = 10.0


def colunaApagavel(coluna: int, celulas: list[CelulaGrade], totalColunas: int) -> str:
  idaApaga = .05 + coluna / totalColunas * .4
  voltaRedesenha = .55 + (totalColunas - coluna) / totalColunas * .4
  desenho = "".join(desenharCelula(celula, celula.nivel) for celula in celulas if celula.nivel > 0)
  if not desenho:
    return ""
  animacao = (
    f'<animate attributeName="opacity" values="1;1;0;0;1;1" '
    f'keyTimes="0;{numero(round(idaApaga, 4))};{numero(round(idaApaga + .01, 4))};'
    f'{numero(round(voltaRedesenha, 4))};{numero(round(voltaRedesenha + .01, 4))};1" '
    f'dur="{numero(CICLO_BORRACHA)}s" repeatCount="indefinite"/>'
  )
  return f"<g>{desenho}{animacao}</g>"


def desenharBorracha(totalColunas: int) -> str:
  inicioX = GRADE_X - 10
  fimX = GRADE_X + totalColunas * PASSO - 4
  valores = f"{inicioX} 0;{inicioX} 0;{fimX} 0;{fimX} 0;{inicioX} 0;{inicioX} 0"
  return f"""<g class="so-animado">
<animateTransform attributeName="transform" type="translate" values="{valores}"
keyTimes="0;.05;.45;.55;.95;1" dur="{numero(CICLO_BORRACHA)}s" repeatCount="indefinite"/>
<rect x="0" y="{GRADE_Y - 6}" width="14" height="{7 * PASSO + 9}" rx="4" fill="{COR_TEXTO}" fill-opacity=".92" filter="url(#brilho)"/>
<rect x="0" y="{GRADE_Y - 6}" width="14" height="22" rx="4" fill="{COR_TURQUESA}"/>
</g>"""


def gerarHeatmapBorracha(semanas: list[list[DiaContribuicao]], total: int) -> str:
  celulas = montarCelulas(semanas)
  totalColunas = len(semanas)
  fundo = "".join(desenharCelula(celula, 0) for celula in celulas)
  colunas = "".join(
    colunaApagavel(coluna, [celula for celula in celulas if celula.coluna == coluna], totalColunas)
    for coluna in range(totalColunas)
  )
  conteudo = f'<g class="surgir">{fundo}{colunas}</g>' + desenharBorracha(totalColunas)
  titulo = f"Calendário de contribuições apagado e redesenhado por uma borracha: {total} contribuições no último ano"
  return montarPainelHeatmap(semanas, total, "borracha", conteudo, "", titulo)
