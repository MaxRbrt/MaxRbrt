import io

from PIL import Image, ImageOps

from aurora import (
  COR_BORDA,
  COR_TEXTO,
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
# 1. RETRATO ASCII A PARTIR DO AVATAR
# ============================================================

RAMPA_CARACTERES = " .:-=+*#%@"
COLUNAS_RETRATO = 56
LINHAS_RETRATO = 34
RECORTE_ROSTO = (70, 60, 350, 300)


def ehFundoNeutro(vermelho: int, verde: int, azul: int) -> bool:
  maior = max(vermelho, verde, azul)
  menor = min(vermelho, verde, azul)
  saturacao = (maior - menor) / maior if maior else 0
  semCor = saturacao < .16
  tomMedio = 70 <= maior <= 175
  return semCor and tomMedio


def gerarLinhasRetrato(avatarJpeg: bytes) -> list[str]:
  imagem = Image.open(io.BytesIO(avatarJpeg)).convert("RGB").crop(RECORTE_ROSTO)
  colorida = imagem.resize((COLUNAS_RETRATO, LINHAS_RETRATO), Image.LANCZOS)
  cinza = ImageOps.equalize(colorida.convert("L"))
  linhas = []
  for linha in range(LINHAS_RETRATO):
    caracteres = []
    for coluna in range(COLUNAS_RETRATO):
      pixel = colorida.getpixel((coluna, linha))
      if ehFundoNeutro(*pixel):
        caracteres.append(" ")
        continue
      brilho = cinza.getpixel((coluna, linha)) / 255
      indice = min(len(RAMPA_CARACTERES) - 1, int(brilho * len(RAMPA_CARACTERES)))
      caracteres.append(RAMPA_CARACTERES[max(indice, 1)])
    linhas.append("".join(caracteres))
  return linhas


# ============================================================
# 2. JANELA DE TERMINAL
# ============================================================

ALTURA_SCAN = 384
CICLO_SCANNER = 5.0
TOPO_CONTEUDO = 48


def barraJanela(usuario: str) -> str:
  return f"""<circle cx="26" cy="22" r="5.5" fill="#FF5F57"/>
<circle cx="44" cy="22" r="5.5" fill="#FEBC2E"/>
<circle cx="62" cy="22" r="5.5" fill="#28C840"/>
<text class="mono" x="{LARGURA_PAINEL / 2}" y="26" font-size="11" text-anchor="middle" fill="{COR_TEXTO_2}">{textoSvg(usuario.lower())}@github — profile-scan</text>
<rect x="8" y="40" width="{LARGURA_PAINEL - 16}" height="1" fill="{COR_BORDA}"/>"""


def retratoAscii(linhas: list[str]) -> str:
  alturaLinha = 8.4
  topo = TOPO_CONTEUDO + 20
  partes = [
    f'<rect x="24" y="{TOPO_CONTEUDO + 8}" width="360" height="{ALTURA_SCAN - TOPO_CONTEUDO - 30}" rx="10" '
    f'fill="#0A0F14" stroke="{COR_BORDA}"/>'
  ]
  for indice, linha in enumerate(linhas):
    y = topo + indice * alturaLinha + 6
    demora = (y - TOPO_CONTEUDO) / (ALTURA_SCAN - TOPO_CONTEUDO) * CICLO_SCANNER
    partes.append(
      f'<text class="linha-retrato" {atraso(demora)} x="36" y="{numero(y)}" textLength="336" '
      f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{textoSvg(linha)}</text>'
    )
  return f'<g class="mono surgir" font-size="8.6" fill="{COR_TURQUESA}">{"".join(partes)}</g>'


def linhasFicha(usuario: str, campos: list[tuple[str, str]]) -> tuple[str, float]:
  partes = []
  y = TOPO_CONTEUDO + 34
  inicio = .3
  comando = f"$ scan --perfil {usuario}"
  partes.append(linhaDigitada(0, comando, y, inicio, COR_VERDE_CLARO))
  for indice, (chave, valor) in enumerate(campos, start=1):
    y += 24
    texto = f"{chave:<11}{valor}"
    partes.append(linhaDigitada(indice, texto, y, inicio + indice * .22, COR_TEXTO, chave))
  return "".join(partes), y


def linhaDigitada(
  indice: int, texto: str, y: float, inicio: float, cor: str, chave: str = ""
) -> str:
  largura = len(texto) * 12 * .62 + 4
  recorte = recorteDigitado(f"recorteFicha{indice}", 408, y - 13, largura, 18, inicio, .35)
  if chave:
    valor = texto[11:]
    conteudo = (
      f'<tspan fill="{COR_TURQUESA}">{textoSvg(chave)}</tspan>'
      f'<tspan x="{numero(410 + 11 * 12 * .62)}" fill="{cor}">{textoSvg(valor)}</tspan>'
    )
  else:
    conteudo = textoSvg(texto)
  return (
    f'<defs>{recorte}</defs><text class="mono" x="410" y="{numero(y)}" font-size="12" '
    f'fill="{cor}" clip-path="url(#recorteFicha{indice})">{conteudo}</text>'
  )


def scannerHorizontal() -> str:
  return f"""<defs><linearGradient id="faixaScanner" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
<stop offset=".8" stop-color="{COR_TURQUESA}" stop-opacity=".2"/>
<stop offset="1" stop-color="{COR_VERDE_CLARO}" stop-opacity=".55"/>
</linearGradient></defs>
<g class="scanner so-animado">
<rect x="10" y="-46" width="{LARGURA_PAINEL - 20}" height="46" fill="url(#faixaScanner)"/>
<rect x="10" y="-1.5" width="{LARGURA_PAINEL - 20}" height="1.5" fill="{COR_VERDE_CLARO}" filter="url(#brilho)"/>
</g>"""


def estiloScan() -> str:
  return f"""
.scanner{{animation:descer {CICLO_SCANNER}s linear infinite}}
.linha-retrato{{animation:iluminar {CICLO_SCANNER}s linear infinite}}
.cursor-final{{animation:piscar 1s steps(1) infinite}}
@keyframes descer{{from{{transform:translateY({TOPO_CONTEUDO}px)}}to{{transform:translateY({ALTURA_SCAN}px)}}}}
@keyframes iluminar{{0%{{fill:{COR_TEXTO}}}6%{{fill:{COR_VERDE_CLARO}}}14%,100%{{fill:{COR_TURQUESA}}}}}
"""


def gerarScan(usuario: str, avatarJpeg: bytes, campos: list[tuple[str, str]]) -> str:
  fichaSvg, ultimoY = linhasFicha(usuario.lower(), campos)
  cursorY = ultimoY + 24
  inicioCursor = .3 + (len(campos) + 1) * .22
  cursor = (
    f'<g class="surgir" {atraso(inicioCursor)}><text class="mono" x="410" y="{numero(cursorY)}" font-size="12" '
    f'fill="{COR_VERDE_CLARO}">$ <tspan class="cursor-final">█</tspan></text></g>'
  )
  corpo = (
    barraJanela(usuario)
    + retratoAscii(gerarLinhasRetrato(avatarJpeg))
    + fichaSvg
    + cursor
    + scannerHorizontal()
  )
  titulo = f"Profile scan de @{usuario}: retrato ASCII e ficha técnica"
  return documentoSvg(LARGURA_PAINEL, ALTURA_SCAN, titulo, corpo, estiloScan())
