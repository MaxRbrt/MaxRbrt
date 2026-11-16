from dados_github import Linguagem
from aurora import (
  COR_BORDA,
  COR_TEXTO,
  COR_TEXTO_2,
  COR_TURQUESA,
  LARGURA_PAINEL,
  atraso,
  cabecalhoPainel,
  documentoSvg,
  fluxoEtiquetas,
  numero,
  textoSvg,
)

# ============================================================
# 1. PAINEL TECH STACK
# ============================================================

ESTILO_STACK = """
.barra-tile{transform-box:fill-box;transform-origin:left center;animation:crescer 1.6s cubic-bezier(.2,.8,.2,1) both}
@keyframes crescer{from{transform:scaleX(0)}to{transform:scaleX(1)}}
"""


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
  return documentoSvg(LARGURA_PAINEL, round(altura), titulo, corpo, ESTILO_STACK)
