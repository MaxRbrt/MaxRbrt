from urllib.parse import urlparse

from dados_github import Repositorio
from aurora import (
  COR_TEXTO,
  COR_TEXTO_2,
  COR_TURQUESA,
  COR_VERDE_CLARO,
  LARGURA_PAINEL,
  atraso,
  documentoSvg,
  fluxoEtiquetas,
  quebrarTexto,
  textoSvg,
)

# ============================================================
# 1. CARTÃO DE PROJETO
# ============================================================

ALTURA_PROJETO = 176

ESTILO_PROJETO = """
.trilho{transform-box:fill-box;transform-origin:center top;animation:crescerTrilho 1s cubic-bezier(.2,.8,.2,1) both}
@keyframes crescerTrilho{from{transform:scaleY(0)}to{transform:scaleY(1)}}
"""


def enderecoCurto(url: str) -> str:
  partes = urlparse(url)
  return (partes.netloc + partes.path).rstrip("/")


def cabecalhoProjeto(posicao: int, repositorio: Repositorio) -> str:
  linguagem = (
    f'<circle cx="{LARGURA_PAINEL - 150}" cy="40" r="5" fill="{repositorio.corLinguagem}"/>'
    f'<text class="mono" x="{LARGURA_PAINEL - 140}" y="44" font-size="11.5" fill="{COR_TEXTO_2}">'
    f"{textoSvg(repositorio.linguagem)}</text>"
  )
  return f"""<g class="surgir" {atraso(.1)}>
<text class="mono" x="44" y="45" font-size="11" letter-spacing="2" fill="{COR_TURQUESA}">0{posicao} /</text>
<text class="sans" x="82" y="46" font-size="21" font-weight="800" fill="{COR_TEXTO}">{textoSvg(repositorio.nome)}</text>
{linguagem}
</g>"""


def corpoProjeto(repositorio: Repositorio) -> str:
  linhas = quebrarTexto(repositorio.descricao, 108)[:2]
  descricao = "".join(
    f'<tspan x="44" dy="{0 if indice == 0 else 19}">{textoSvg(linha)}</tspan>'
    for indice, linha in enumerate(linhas)
  )
  etiquetas, _ = fluxoEtiquetas(repositorio.topicos[:7], 44, 112, LARGURA_PAINEL - 88, 10)
  demo = ""
  if repositorio.demo:
    demo = (
      f'<text class="mono" x="{LARGURA_PAINEL - 44}" y="153" font-size="11" text-anchor="end" '
      f'fill="{COR_VERDE_CLARO}">demo ↗ {textoSvg(enderecoCurto(repositorio.demo))}</text>'
    )
  return f"""<g class="surgir" {atraso(.25)}>
<text class="sans" x="44" y="76" font-size="13.5" fill="{COR_TEXTO_2}">{descricao}</text>
</g>
<g class="surgir" {atraso(.4)}>{etiquetas}{demo}</g>"""


def gerarProjeto(posicao: int, repositorio: Repositorio) -> str:
  trilho = (
    f'<rect class="trilho" x="22" y="26" width="2.5" height="{ALTURA_PROJETO - 52}" rx="1.25" '
    f'fill="url(#destaque)" filter="url(#brilho)"/>'
  )
  corpo = trilho + cabecalhoProjeto(posicao, repositorio) + corpoProjeto(repositorio)
  titulo = f"Projeto {repositorio.nome}: {repositorio.descricao}"
  return documentoSvg(LARGURA_PAINEL, ALTURA_PROJETO, titulo, corpo, ESTILO_PROJETO)
