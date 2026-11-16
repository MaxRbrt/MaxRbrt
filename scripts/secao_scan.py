import io
import random

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
# 2. JANELA DE TERMINAL E RETRATO
# ============================================================

ALTURA_SCAN = 384
TOPO_CONTEUDO = 48
CICLO_SCANNER = 6.5
FIM_DESCIDA = .62
INICIO_APAGAR = .88
ALTURA_FAIXA_RUIDO = 22
VARIANTES_RUIDO = 3
COR_FUNDO_RETRATO = "#0A0F14"
CAIXA_RETRATO = (24, TOPO_CONTEUDO + 8, 360, ALTURA_SCAN - TOPO_CONTEUDO - 30)


def barraJanela(usuario: str) -> str:
  return f"""<circle cx="26" cy="22" r="5.5" fill="#FF5F57"/>
<circle cx="44" cy="22" r="5.5" fill="#FEBC2E"/>
<circle cx="62" cy="22" r="5.5" fill="#28C840"/>
<text class="mono" x="{LARGURA_PAINEL / 2}" y="26" font-size="11" text-anchor="middle" fill="{COR_TEXTO_2}">{textoSvg(usuario.lower())}@github — profile-scan</text>
<rect x="8" y="40" width="{LARGURA_PAINEL - 16}" height="1" fill="{COR_BORDA}"/>"""


def textoRetrato(linhas: list[str]) -> str:
  alturaLinha = 8.4
  topo = TOPO_CONTEUDO + 26
  partes = []
  for indice, linha in enumerate(linhas):
    y = topo + indice * alturaLinha
    partes.append(
      f'<text x="36" y="{numero(y)}" textLength="336" '
      f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{textoSvg(linha)}</text>'
    )
  return "".join(partes)


def embaralharLinhas(linhas: list[str], semente: int) -> list[str]:
  sorteio = random.Random(semente)
  caracteres = RAMPA_CARACTERES[1:]
  return [
    "".join(" " if caractere == " " else sorteio.choice(caracteres) for caractere in linha)
    for linha in linhas
  ]


# ============================================================
# 3. LINHA DO TEMPO DO SCANNER (SMIL, MESMO RELÓGIO PARA TUDO)
# ============================================================


def animacaoSmil(atributo: str, valores: list[float], tempos: list[float]) -> str:
  return (
    f'<animate attributeName="{atributo}" dur="{numero(CICLO_SCANNER)}s" '
    f'repeatCount="indefinite" values="{";".join(numero(valor) for valor in valores)}" '
    f'keyTimes="{";".join(numero(tempo) for tempo in tempos)}"/>'
  )


def posicoesScanner() -> tuple[float, float]:
  _, topo, _, altura = CAIXA_RETRATO
  return topo, topo + altura


def coberturaRetrato() -> str:
  x, topo, largura, altura = CAIXA_RETRATO
  fundo = topo + altura
  tempos = [0, FIM_DESCIDA, INICIO_APAGAR, INICIO_APAGAR, 1]
  tempoOpacidade = [0, INICIO_APAGAR, INICIO_APAGAR, 1]
  return (
    f'<rect class="so-animado" x="{x + 1}" y="{topo + 1}" width="{largura - 2}" '
    f'height="{altura - 2}" rx="9" fill="{COR_FUNDO_RETRATO}">'
    + animacaoSmil("y", [topo + 1, fundo, fundo, topo + 1, topo + 1], tempos)
    + animacaoSmil("height", [altura - 2, 0, 0, altura - 2, altura - 2], tempos)
    + animacaoSmil("opacity", [1, 1, 0, 1], tempoOpacidade)
    + "</rect>"
  )


def visibilidadeTemporaria() -> str:
  tempos = [0, .03, FIM_DESCIDA - .02, FIM_DESCIDA + .02, 1]
  return animacaoSmil("opacity", [0, 1, 1, 0, 0], tempos)


def faixaRuido(linhas: list[str]) -> str:
  x, topo, largura, _ = CAIXA_RETRATO
  _, fundo = posicoesScanner()
  recorte = (
    f'<clipPath id="recorteRuido"><rect x="{x}" y="{topo}" width="{largura}" '
    f'height="{ALTURA_FAIXA_RUIDO}">'
    + animacaoSmil(
      "y", [topo - ALTURA_FAIXA_RUIDO, fundo - ALTURA_FAIXA_RUIDO, fundo - ALTURA_FAIXA_RUIDO],
      [0, FIM_DESCIDA, 1],
    )
    + "</rect></clipPath>"
  )
  variantes = [quadroRuido(linhas, indice) for indice in range(VARIANTES_RUIDO)]
  return (
    f'<defs>{recorte}</defs><g class="so-animado" clip-path="url(#recorteRuido)">'
    + visibilidadeTemporaria()
    + f'<rect x="{x}" y="{topo}" width="{largura}" height="{fundo - topo}" '
    + f'fill="{COR_FUNDO_RETRATO}"/>'
    + f'<g class="mono" font-size="8.6" fill="{COR_VERDE_CLARO}">{"".join(variantes)}</g></g>'
  )


def quadroRuido(linhas: list[str], indice: int) -> str:
  passo = 1 / VARIANTES_RUIDO
  valores = ";".join("1" if quadro == indice else "0" for quadro in range(VARIANTES_RUIDO))
  tempos = ";".join(numero(quadro * passo) for quadro in range(VARIANTES_RUIDO))
  return (
    f'<g opacity="0"><animate attributeName="opacity" dur=".24s" repeatCount="indefinite" '
    f'calcMode="discrete" values="{valores}" keyTimes="{tempos}"/>'
    f'{textoRetrato(embaralharLinhas(linhas, indice))}</g>'
  )


def laserScanner() -> str:
  x, topo, largura, altura = CAIXA_RETRATO
  _, fundo = posicoesScanner()
  return f"""<defs><linearGradient id="faixaScanner" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
<stop offset=".8" stop-color="{COR_TURQUESA}" stop-opacity=".2"/>
<stop offset="1" stop-color="{COR_VERDE_CLARO}" stop-opacity=".55"/>
</linearGradient>
<clipPath id="recorteLaser">
<rect x="{x}" y="{topo}" width="{largura}" height="{altura}" rx="10"/>
</clipPath>
</defs>
<g class="so-animado" clip-path="url(#recorteLaser)">{visibilidadeTemporaria()}<g>
<animateTransform attributeName="transform" type="translate" dur="{numero(CICLO_SCANNER)}s"
repeatCount="indefinite" values="0 {numero(topo)};0 {numero(fundo)};0 {numero(fundo)}"
keyTimes="0;{numero(FIM_DESCIDA)};1"/>
<rect x="{x}" y="-46" width="{largura}" height="46" fill="url(#faixaScanner)"/>
<rect x="{x}" y="-1.5" width="{largura}" height="1.5" fill="{COR_VERDE_CLARO}"
filter="url(#brilho)"/>
</g></g>"""


def retratoAscii(linhas: list[str]) -> str:
  x, topo, largura, altura = CAIXA_RETRATO
  moldura = (
    f'<rect x="{x}" y="{topo}" width="{largura}" height="{altura}" rx="10" '
    f'fill="{COR_FUNDO_RETRATO}" stroke="{COR_BORDA}"/>'
  )
  retrato = f'<g class="mono" font-size="8.6" fill="{COR_TURQUESA}">{textoRetrato(linhas)}</g>'
  return (
    f'<g class="surgir">{moldura}{retrato}{coberturaRetrato()}{faixaRuido(linhas)}'
    f'{laserScanner()}</g>'
  )


# ============================================================
# 4. FICHA DIGITADA E MONTAGEM DO PAINEL
# ============================================================


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


def estiloScan() -> str:
  return """
.cursor-final{animation:piscar 1s steps(1) infinite}
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
  )
  titulo = f"Profile scan de @{usuario}: retrato ASCII e ficha técnica"
  return documentoSvg(LARGURA_PAINEL, ALTURA_SCAN, titulo, corpo, estiloScan())
