from html import escape

# ============================================================
# 1. PALETA E TIPOGRAFIA AURORA
# ============================================================

COR_FUNDO = "#0D1117"
COR_SUPERFICIE = "#111827"
COR_SUPERFICIE_2 = "#161B22"
COR_TURQUESA = "#2DD4BF"
COR_ESMERALDA = "#34D399"
COR_VERDE_CLARO = "#6EE7B7"
COR_CIANO = "#22D3EE"
COR_TEXTO = "#E6EDF3"
COR_TEXTO_2 = "#94A3B8"
COR_BORDA = "#30363D"

FONTE_MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
FONTE_SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

LARGURA_PAINEL = 860

ESTILO_BASE = f"""
.mono{{font-family:{FONTE_MONO}}}
.sans{{font-family:{FONTE_SANS}}}
.surgir{{opacity:0;animation:surgir .8s cubic-bezier(.2,.7,.2,1) forwards}}
.borda-viva{{animation:bordaViva 4.8s ease-in-out infinite}}
.piscar{{animation:piscar 1.1s steps(1) infinite}}
@keyframes surgir{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes bordaViva{{0%,100%{{stroke-opacity:.55}}50%{{stroke-opacity:1}}}}
@keyframes piscar{{0%{{opacity:1}}50%{{opacity:0}}}}
"""

ESTILO_MOVIMENTO_REDUZIDO = """
@media (prefers-reduced-motion:reduce){
*{animation:none!important}
.surgir{opacity:1}
.so-animado{display:none}
}
"""

# ============================================================
# 2. TEXTO E NÚMEROS SEGUROS PARA SVG
# ============================================================


def textoSvg(valor: str) -> str:
  return escape(valor, quote=True)


def numero(valor: float) -> str:
  return f"{valor:.2f}".rstrip("0").rstrip(".")


def atraso(segundos: float) -> str:
  return f'style="animation-delay:{numero(segundos)}s"'


# ============================================================
# 3. DEFINIÇÕES COMUNS (GRADIENTES E BRILHO)
# ============================================================


def definicoesAurora(largura: int, altura: int) -> str:
  return f"""<defs>
<linearGradient id="borda" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{COR_TURQUESA}"/>
<stop offset=".55" stop-color="{COR_CIANO}" stop-opacity=".55"/>
<stop offset="1" stop-color="{COR_ESMERALDA}"/>
</linearGradient>
<linearGradient id="fundo" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{COR_SUPERFICIE}"/>
<stop offset="1" stop-color="{COR_FUNDO}"/>
</linearGradient>
<linearGradient id="destaque" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{COR_VERDE_CLARO}"/>
<stop offset=".5" stop-color="{COR_TURQUESA}"/>
<stop offset="1" stop-color="{COR_CIANO}"/>
</linearGradient>
<radialGradient id="auraLateral" cx="0" cy="{numero(altura / 2)}" r="{numero(largura * .55)}"
gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{COR_TURQUESA}" stop-opacity=".17"/>
<stop offset="1" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="linhaTopo" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
<stop offset=".5" stop-color="{COR_VERDE_CLARO}" stop-opacity=".9"/>
<stop offset="1" stop-color="{COR_CIANO}" stop-opacity="0"/>
</linearGradient>
<filter id="brilho" x="-30%" y="-30%" width="160%" height="160%">
<feGaussianBlur stdDeviation="2.4" result="desfoque"/>
<feMerge><feMergeNode in="desfoque"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>"""


# ============================================================
# 4. MOLDURA DOS PAINÉIS
# ============================================================


def molduraPainel(largura: int, altura: int) -> str:
  return f"""<rect x=".5" y=".5" width="{largura - 1}" height="{altura - 1}" rx="18" fill="url(#fundo)"/>
<rect x=".5" y=".5" width="{largura - 1}" height="{altura - 1}" rx="18" fill="url(#auraLateral)"/>
<rect x="7.5" y="7.5" width="{largura - 15}" height="{altura - 15}" rx="12" fill="none"
stroke="{COR_BORDA}" stroke-opacity=".55"/>
<rect x="60" y="0" width="{largura - 120}" height="1.4" fill="url(#linhaTopo)"/>
<rect class="borda-viva" x=".5" y=".5" width="{largura - 1}" height="{altura - 1}" rx="18"
fill="none" stroke="url(#borda)" stroke-width="1.4"/>"""


def documentoSvg(largura: int, altura: int, titulo: str, corpo: str, estiloExtra: str = "") -> str:
  estilo = ESTILO_BASE + estiloExtra + ESTILO_MOVIMENTO_REDUZIDO
  return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}" role="img" aria-label="{textoSvg(titulo)}">
<title>{textoSvg(titulo)}</title>
<style>{estilo}</style>
{definicoesAurora(largura, altura)}
{molduraPainel(largura, altura)}
{corpo}
</svg>
"""


# ============================================================
# 5. CABEÇALHO E ETIQUETAS
# ============================================================


def cabecalhoPainel(titulo: str, subtitulo: str, comando: str, largura: int) -> str:
  return f"""<g class="surgir">
<text class="mono" x="40" y="46" font-size="13" font-weight="700" letter-spacing="3" fill="{COR_TURQUESA}">{textoSvg(titulo)}</text>
<text class="sans" x="40" y="68" font-size="13" fill="{COR_TEXTO_2}">{textoSvg(subtitulo)}</text>
<text class="mono" x="{largura - 40}" y="46" font-size="11" text-anchor="end" fill="{COR_VERDE_CLARO}" fill-opacity=".55">{textoSvg(comando)}</text>
</g>"""


def larguraEtiqueta(rotulo: str, tamanhoFonte: float) -> float:
  return len(rotulo) * tamanhoFonte * 0.62 + 18


def etiqueta(x: float, y: float, rotulo: str, tamanhoFonte: float = 11) -> str:
  largura = larguraEtiqueta(rotulo, tamanhoFonte)
  altura = tamanhoFonte + 12
  return f"""<g>
<rect x="{numero(x)}" y="{numero(y)}" width="{numero(largura)}" height="{numero(altura)}" rx="{numero(altura / 2)}"
fill="{COR_TURQUESA}" fill-opacity=".08" stroke="{COR_TURQUESA}" stroke-opacity=".45"/>
<text class="mono" x="{numero(x + largura / 2)}" y="{numero(y + altura / 2 + tamanhoFonte * .36)}" font-size="{tamanhoFonte}"
text-anchor="middle" fill="{COR_VERDE_CLARO}">{textoSvg(rotulo)}</text>
</g>"""


def fluxoEtiquetas(
  rotulos: list[str], x: float, y: float, larguraMaxima: float, tamanhoFonte: float = 11
) -> tuple[str, float]:
  partes = []
  cursorX = x
  cursorY = y
  alturaLinha = tamanhoFonte + 12
  for rotulo in rotulos:
    largura = larguraEtiqueta(rotulo, tamanhoFonte)
    passouDoLimite = cursorX + largura > x + larguraMaxima
    if passouDoLimite and cursorX > x:
      cursorX = x
      cursorY += alturaLinha + 8
    partes.append(etiqueta(cursorX, cursorY, rotulo, tamanhoFonte))
    cursorX += largura + 7
  return "\n".join(partes), cursorY + alturaLinha - y


def recorteDigitado(
  idRecorte: str, x: float, y: float, largura: float, altura: float, inicio: float, duracao: float
) -> str:
  return f"""<clipPath id="{idRecorte}">
<rect x="{numero(x)}" y="{numero(y)}" width="0" height="{numero(altura)}">
<animate attributeName="width" begin="{numero(inicio)}s"
dur="{numero(duracao)}s" fill="freeze" calcMode="discrete"
values="{valoresDigitacao(largura)}"/>
</rect>
</clipPath>"""


def valoresDigitacao(largura: float) -> str:
  passos = 16
  return ";".join(numero(largura * passo / passos) for passo in range(passos + 1))


def quebrarTexto(texto: str, maximoCaracteres: int) -> list[str]:
  linhas: list[str] = []
  atual = ""
  for palavra in texto.split():
    candidata = f"{atual} {palavra}".strip()
    if len(candidata) > maximoCaracteres and atual:
      linhas.append(atual)
      atual = palavra
      continue
    atual = candidata
  if atual:
    linhas.append(atual)
  return linhas
