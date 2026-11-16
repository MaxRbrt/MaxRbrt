from dados_github import DiaContribuicao, Linguagem
from aurora import (
  COR_BORDA,
  COR_SUPERFICIE,
  COR_TEXTO,
  COR_TEXTO_2,
  COR_TURQUESA,
  COR_VERDE_CLARO,
  LARGURA_PAINEL,
  atraso,
  cabecalhoPainel,
  documentoSvg,
  fluxoEtiquetas,
  numero,
  textoSvg,
)

NOMES_DIAS_SEMANA = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"]

# ============================================================
# 1. INDICADORES DE ATIVIDADE (CALCULADOS DO CALENDÁRIO)
# ============================================================


def calcularMaiorSequencia(semanas: list[list[DiaContribuicao]]) -> int:
  maior = 0
  atual = 0
  for semana in semanas:
    for dia in semana:
      atual = atual + 1 if dia.quantidade > 0 else 0
      maior = max(maior, atual)
  return maior


def calcularDiaMaisAtivo(semanas: list[list[DiaContribuicao]]) -> str:
  totais = [0] * 7
  for semana in semanas:
    for dia in semana:
      totais[dia.diaSemana] += dia.quantidade
  return NOMES_DIAS_SEMANA[totais.index(max(totais))]


def calcularMelhorSemana(semanas: list[list[DiaContribuicao]]) -> int:
  return max((sum(dia.quantidade for dia in semana) for semana in semanas), default=0)


def totaisSemanais(semanas: list[list[DiaContribuicao]], quantidade: int) -> list[int]:
  return [sum(dia.quantidade for dia in semana) for semana in semanas[-quantidade:]]


# ============================================================
# 2. CONTADOR ROLANTE (ODÔMETRO)
# ============================================================

ALTURA_DIGITO = 40
LARGURA_DIGITO = 21


def estiloRolagemDigitos() -> str:
  regras = []
  for digito in range(10):
    deslocamento = -digito * ALTURA_DIGITO
    regras.append(
      f".rolar{digito}{{transform:translateY({deslocamento}px);"
      f"animation:rolar{digito} 1.8s cubic-bezier(.2,.8,.2,1) both}}"
      f"@keyframes rolar{digito}{{from{{transform:translateY(0)}}to{{transform:translateY({deslocamento}px)}}}}"
    )
  return "\n".join(regras)


def contadorRolante(idRecorte: str, valor: int, x: float, yBase: float, inicio: float) -> str:
  digitos = str(valor)
  topo = yBase - 31
  recorte = (
    f'<clipPath id="{idRecorte}"><rect x="{numero(x - 2)}" y="{numero(topo)}" '
    f'width="{len(digitos) * LARGURA_DIGITO + 6}" height="{ALTURA_DIGITO}"/></clipPath>'
  )
  colunas = []
  for posicao, digito in enumerate(digitos):
    faixa = "".join(
      f'<text x="{numero(x + posicao * LARGURA_DIGITO)}" y="{numero(yBase + numeroFaixa * ALTURA_DIGITO)}">{numeroFaixa}</text>'
      for numeroFaixa in range(10)
    )
    demora = inicio + posicao * .12
    colunas.append(f'<g class="rolar{digito}" {atraso(demora)}>{faixa}</g>')
  return (
    f'<defs>{recorte}</defs><g clip-path="url(#{idRecorte})" class="mono" font-size="34" '
    f'font-weight="800" fill="{COR_TEXTO}">{"".join(colunas)}</g>'
  )


# ============================================================
# 3. PAINEL PROFILE SIGNAL
# ============================================================

ESTILO_SINAIS = """
.barra-tile{transform-box:fill-box;transform-origin:left center;animation:crescer 1.6s cubic-bezier(.2,.8,.2,1) both}
.pulso{animation:piscar 1.8s ease-in-out infinite}
@keyframes crescer{from{transform:scaleX(0)}to{transform:scaleX(1)}}
"""


def miniGraficoSemanas(semanas: list[int], x: float, y: float, largura: float, altura: float) -> str:
  maior = max(semanas) or 1
  passo = largura / max(len(semanas) - 1, 1)
  pontos = " ".join(
    f"{numero(x + indice * passo)},{numero(y + altura - valor / maior * altura)}"
    for indice, valor in enumerate(semanas)
  )
  return (
    f'<polyline class="surgir" {atraso(.9)} points="{pontos}" fill="none" stroke="url(#destaque)" '
    f'stroke-width="1.6" stroke-linejoin="round" filter="url(#brilho)"/>'
  )


def cartaoSinal(indice: int, x: float, largura: float, rotulo: str, valor: int, extra: str) -> str:
  y = 92
  return f"""<g class="surgir" {atraso(.15 + indice * .12)}>
<rect x="{numero(x)}" y="{y}" width="{numero(largura)}" height="98" rx="12" fill="{COR_SUPERFICIE}" stroke="{COR_BORDA}"/>
<circle class="pulso" cx="{numero(x + 20)}" cy="{y + 22}" r="3" fill="{COR_VERDE_CLARO}"/>
<text class="mono" x="{numero(x + 30)}" y="{y + 26}" font-size="10.5" letter-spacing="1.5" fill="{COR_TEXTO_2}">{textoSvg(rotulo)}</text>
{contadorRolante(f"recorteValor{indice}", valor, x + 16, y + 68, .4 + indice * .12)}
{extra}
<rect class="barra-tile" {atraso(.5 + indice * .12)} x="{numero(x + 16)}" y="{y + 84}" width="{numero(largura - 32)}" height="2" rx="1" fill="url(#destaque)" opacity=".7"/>
</g>"""


def gerarSinais(
  totalContribuicoes: int,
  repositoriosPublicos: int,
  seguidores: int,
  estrelasRecebidas: int,
  semanas: list[list[DiaContribuicao]],
) -> str:
  largura = (LARGURA_PAINEL - 80 - 3 * 16) / 4
  posicoes = [40 + indice * (largura + 16) for indice in range(4)]
  grafico = miniGraficoSemanas(totaisSemanais(semanas, 26), posicoes[0] + 96, 120, largura - 112, 34)
  cartoes = [
    cartaoSinal(0, posicoes[0], largura, "CONTRIBUIÇÕES", totalContribuicoes, grafico),
    cartaoSinal(1, posicoes[1], largura, "REPOS PÚBLICOS", repositoriosPublicos, ""),
    cartaoSinal(2, posicoes[2], largura, "SEGUIDORES", seguidores, ""),
    cartaoSinal(3, posicoes[3], largura, "ESTRELAS RECEBIDAS", estrelasRecebidas, ""),
  ]
  indicadores = (
    f"dia mais ativo: {calcularDiaMaisAtivo(semanas)}   ·   "
    f"maior sequência: {calcularMaiorSequencia(semanas)} dias   ·   "
    f"melhor semana: {calcularMelhorSemana(semanas)} contribuições"
  )
  rodape = (
    f'<text class="mono surgir" {atraso(1.1)} x="40" y="222" font-size="11" fill="{COR_TEXTO_2}">'
    f'<tspan fill="{COR_TURQUESA}">› </tspan>{textoSvg(indicadores)}</text>'
  )
  cabecalho = cabecalhoPainel(
    "PROFILE SIGNAL", "Dados públicos do GitHub, atualizados todo dia", "> signal.read", LARGURA_PAINEL
  )
  corpo = cabecalho + "".join(cartoes) + rodape
  titulo = (
    f"Estatísticas: {totalContribuicoes} contribuições no último ano, {repositoriosPublicos} repositórios "
    f"públicos, {seguidores} seguidores, {estrelasRecebidas} estrelas recebidas"
  )
  return documentoSvg(LARGURA_PAINEL, 248, titulo, corpo, ESTILO_SINAIS + estiloRolagemDigitos())


# ============================================================
# 4. PAINEL TECH STACK
# ============================================================


def barrasLinguagens(linguagens: list[Linguagem]) -> str:
  partes = [
    f'<text class="mono surgir" x="40" y="104" font-size="10.5" letter-spacing="1.5" fill="{COR_TURQUESA}">LINGUAGENS · VOLUME DE CÓDIGO</text>'
  ]
  for indice, linguagem in enumerate(linguagens[:5]):
    y = 132 + indice * 40
    larguraBarra = max(4.0, 340 * linguagem.percentual / 100)
    partes.append(f"""<g class="surgir" {atraso(.2 + indice * .1)}>
<text class="mono" x="40" y="{y}" font-size="12" fill="{COR_TEXTO}">{textoSvg(linguagem.nome)}</text>
<text class="mono" x="380" y="{y}" font-size="12" text-anchor="end" fill="{COR_TEXTO_2}">{numero(round(linguagem.percentual))}%</text>
<rect x="40" y="{y + 9}" width="340" height="6" rx="3" fill="{COR_BORDA}" fill-opacity=".6"/>
<rect class="barra-tile" {atraso(.4 + indice * .1)} x="40" y="{y + 9}" width="{numero(larguraBarra)}" height="6" rx="3" fill="url(#destaque)"/>
</g>""")
  return "".join(partes)


def categoriasStack(categorias: list[dict]) -> tuple[str, float]:
  partes = []
  y = 96.0
  for indice, categoria in enumerate(categorias):
    etiquetas, alturaEtiquetas = fluxoEtiquetas(categoria["itens"], 432, y + 16, 388, 10.5)
    partes.append(
      f'<g class="surgir" {atraso(.3 + indice * .12)}>'
      f'<text class="mono" x="432" y="{numero(y + 8)}" font-size="10.5" letter-spacing="1.5" fill="{COR_TURQUESA}">'
      f'{textoSvg(categoria["categoria"])}</text>{etiquetas}</g>'
    )
    y += 16 + alturaEtiquetas + 18
  return "".join(partes), y


def gerarStack(linguagens: list[Linguagem], categorias: list[dict]) -> str:
  categoriasSvg, fimCategorias = categoriasStack(categorias)
  altura = max(fimCategorias + 18, 132 + 5 * 40 + 10)
  divisoria = f'<rect x="408" y="92" width="1" height="{numero(altura - 120)}" fill="{COR_BORDA}"/>'
  cabecalho = cabecalhoPainel(
    "TECH STACK", "Linguagens medidas nos repositórios públicos e ferramentas do dia a dia", "> stack.scan", LARGURA_PAINEL
  )
  corpo = cabecalho + barrasLinguagens(linguagens) + divisoria + categoriasSvg
  principais = ", ".join(linguagem.nome for linguagem in linguagens[:3])
  titulo = f"Stack de tecnologias; linguagens principais: {principais}"
  return documentoSvg(LARGURA_PAINEL, round(altura), titulo, corpo, ESTILO_SINAIS)
