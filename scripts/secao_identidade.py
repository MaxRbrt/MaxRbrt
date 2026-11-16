from aurora import (
  COR_BORDA,
  COR_ESMERALDA,
  COR_TEXTO,
  COR_TEXTO_2,
  COR_TURQUESA,
  COR_VERDE_CLARO,
  LARGURA_PAINEL,
  atraso,
  cabecalhoPainel,
  documentoSvg,
  etiqueta,
  larguraEtiqueta,
  numero,
  quebrarTexto,
  textoSvg,
)

# ============================================================
# 1. CARTÃO DE IDENTIDADE (HERO)
# ============================================================

ESTILO_HERO = """
.anel{transform-origin:128px 130px;animation:girar 14s linear infinite}
.anel-inverso{transform-origin:128px 130px;animation:girar 22s linear infinite reverse}
.sinal{animation:piscar 1.6s ease-in-out infinite}
@keyframes girar{to{transform:rotate(360deg)}}
"""


def avatarCircular(avatarDataUri: str) -> str:
  return f"""<defs>
<clipPath id="recorteAvatar"><circle cx="128" cy="130" r="72"/></clipPath>
<radialGradient id="halo" cx="128" cy="130" r="110" gradientUnits="userSpaceOnUse">
<stop offset=".55" stop-color="{COR_TURQUESA}" stop-opacity=".22"/>
<stop offset="1" stop-color="{COR_TURQUESA}" stop-opacity="0"/>
</radialGradient>
</defs>
<circle cx="128" cy="130" r="108" fill="url(#halo)"/>
<g class="surgir">
<image href="{avatarDataUri}" x="56" y="58" width="144" height="144" clip-path="url(#recorteAvatar)" preserveAspectRatio="xMidYMid slice"/>
<circle cx="128" cy="130" r="72" fill="none" stroke="{COR_TURQUESA}" stroke-opacity=".7" stroke-width="1.5"/>
</g>
<circle class="anel so-animado" cx="128" cy="130" r="82" fill="none" stroke="url(#destaque)" stroke-width="2"
stroke-dasharray="46 22 8 22" stroke-linecap="round"/>
<circle class="anel-inverso so-animado" cx="128" cy="130" r="90" fill="none" stroke="{COR_TURQUESA}" stroke-opacity=".35"
stroke-dasharray="2 9"/>"""


def blocoApresentacao(usuario: str, nome: str, bio: str, foco: str) -> str:
  return f"""<text class="mono surgir" {atraso(.15)} x="240" y="66" font-size="14" fill="{COR_TURQUESA}">@{textoSvg(usuario.lower())}</text>
<text class="sans surgir" {atraso(.3)} x="238" y="106" font-size="36" font-weight="800" letter-spacing="-.6" fill="{COR_TEXTO}">{textoSvg(nome)}</text>
<text class="sans surgir" {atraso(.45)} x="240" y="134" font-size="13.5" fill="{COR_TEXTO_2}">{textoSvg(bio.replace(" | ", " · "))}</text>
<text class="mono surgir" {atraso(.6)} x="240" y="160" font-size="12" fill="{COR_ESMERALDA}">› {textoSvg(foco)}</text>"""


def linhaEtiquetas(rotulos: list[str]) -> str:
  partes = []
  cursorX = 240.0
  for indice, rotulo in enumerate(rotulos):
    largura = larguraEtiqueta(rotulo, 11)
    if cursorX + largura > 676:
      break
    partes.append(f'<g class="surgir" {atraso(.75 + indice * .09)}>{etiqueta(cursorX, 180, rotulo)}</g>')
    cursorX += largura + 7
  return "".join(partes)


def metricaContribuicoes(totalContribuicoes: int) -> str:
  return f"""<rect x="690" y="56" width="1.2" height="148" fill="{COR_BORDA}"/>
<g class="surgir" {atraso(.5)}>
<circle class="sinal" cx="742" cy="82" r="3.5" fill="{COR_VERDE_CLARO}"/>
<text class="mono" x="752" y="86" font-size="10.5" letter-spacing="2" fill="{COR_TEXTO_2}">SINAL</text>
<text class="mono" x="775" y="142" font-size="46" font-weight="800" text-anchor="middle" fill="url(#destaque)" filter="url(#brilho)">{totalContribuicoes}</text>
<text class="mono" x="775" y="168" font-size="11" text-anchor="middle" fill="{COR_TEXTO_2}">contribuições</text>
<text class="mono" x="775" y="184" font-size="11" text-anchor="middle" fill="{COR_TEXTO_2}">no último ano</text>
</g>"""


def gerarHero(
  usuario: str,
  nome: str,
  bio: str,
  foco: str,
  etiquetas: list[str],
  totalContribuicoes: int,
  avatarDataUri: str,
) -> str:
  corpo = (
    avatarCircular(avatarDataUri)
    + blocoApresentacao(usuario, nome, bio, foco)
    + linhaEtiquetas(etiquetas)
    + metricaContribuicoes(totalContribuicoes)
  )
  titulo = f"Cartão de perfil de {nome} (@{usuario})"
  return documentoSvg(LARGURA_PAINEL, 260, titulo, corpo, ESTILO_HERO)


# ============================================================
# 2. DESTAQUES (HIGHLIGHTS)
# ============================================================

ESTILO_DESTAQUES = """
.brilho-topo{animation:passarBrilho 5s ease-in-out infinite}
@keyframes passarBrilho{0%{transform:translateX(-120px);opacity:0}20%{opacity:1}60%,100%{transform:translateX(260px);opacity:0}}
"""


def cartaoDestaque(indice: int, x: float, titulo: str, texto: str, largura: float) -> str:
  linhas = quebrarTexto(texto, int(largura / 7.1))[:3]
  textoLinhas = "".join(
    f'<tspan x="{numero(x + 18)}" dy="{0 if posicao == 0 else 18}">{textoSvg(linha)}</tspan>'
    for posicao, linha in enumerate(linhas)
  )
  return f"""<g class="surgir" {atraso(.2 + indice * .18)}>
<rect x="{numero(x)}" y="88" width="{numero(largura)}" height="112" rx="12" fill="{COR_TURQUESA}" fill-opacity=".045" stroke="{COR_BORDA}"/>
<g clip-path="url(#recorteDestaque{indice})"><rect class="brilho-topo so-animado" {atraso(indice * .6)} x="{numero(x)}" y="88" width="90" height="1.5" fill="url(#linhaTopo)"/></g>
<clipPath id="recorteDestaque{indice}"><rect x="{numero(x)}" y="88" width="{numero(largura)}" height="4"/></clipPath>
<text class="mono" x="{numero(x + 18)}" y="116" font-size="11" letter-spacing="2" fill="{COR_TURQUESA}">0{indice + 1}</text>
<text class="sans" x="{numero(x + 18)}" y="142" font-size="18" font-weight="700" fill="{COR_TEXTO}">{textoSvg(titulo)}</text>
<text class="sans" x="{numero(x + 18)}" y="166" font-size="12.5" fill="{COR_TEXTO_2}">{textoLinhas}</text>
</g>"""


def gerarDestaques(destaques: list[dict[str, str]]) -> str:
  quantidade = len(destaques)
  espaco = 16
  largura = (LARGURA_PAINEL - 80 - espaco * (quantidade - 1)) / quantidade
  cartoes = "".join(
    cartaoDestaque(indice, 40 + indice * (largura + espaco), item["titulo"], item["texto"], largura)
    for indice, item in enumerate(destaques)
  )
  cabecalho = cabecalhoPainel("DESTAQUES", "Onde eu mais trabalho hoje", "> highlights --top 3", LARGURA_PAINEL)
  titulos = ", ".join(item["titulo"] for item in destaques)
  return documentoSvg(LARGURA_PAINEL, 228, f"Destaques: {titulos}", cabecalho + cartoes, ESTILO_DESTAQUES)
