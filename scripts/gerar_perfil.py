import json
from pathlib import Path

from dados_github import PerfilGithub, buscarPerfilGithub
from secao_heatmap import gerarHeatmapJato
from secao_scan import gerarScan
from secao_stack import gerarStack
from secao_wordmark import gerarWordmark

RAIZ = Path(__file__).resolve().parent.parent
PASTA_ASSETS = RAIZ / "assets"
ARQUIVO_CONFIG = RAIZ / "config" / "perfil.json"

# ============================================================
# 1. CONFIGURAÇÃO
# ============================================================


def carregarConfig() -> dict:
  with ARQUIVO_CONFIG.open(encoding="utf-8") as arquivo:
    return json.load(arquivo)


def gravarSvg(nome: str, conteudo: str) -> None:
  caminho = PASTA_ASSETS / nome
  caminho.write_text(conteudo, encoding="utf-8", newline="\n")
  print(f"gerado {caminho.relative_to(RAIZ)} ({len(conteudo) // 1024} KB)")


# ============================================================
# 2. CAMPOS DO PROFILE SCAN
# ============================================================


def montarCamposScan(config: dict, perfil: PerfilGithub) -> list[tuple[str, str]]:
  return [
    ("usuário", f"@{perfil.usuario.lower()}"),
    ("nome", perfil.nome),
    ("função", "Desenvolvedor Full Stack"),
    ("formação", config["formacao"]),
    ("local", config["local"]),
    ("repos", f"{perfil.repositoriosPublicos} públicos"),
    ("atividade", f"{perfil.totalContribuicoes} contribuições no último ano"),
    ("estrelas", f"{perfil.estrelasRecebidas} recebidas"),
    ("seguidores", str(perfil.seguidores)),
    ("site", config["site"].replace("https://", "").rstrip("/")),
    ("status", config["status"]),
  ]


# ============================================================
# 3. GERAÇÃO DE TODAS AS SEÇÕES
# ============================================================


def gerarPaineis(config: dict, perfil: PerfilGithub) -> None:
  wordmark = gerarWordmark(perfil.usuario, perfil.nome, config["subtitulo"], False)
  wordmarkMobile = gerarWordmark(perfil.usuario, perfil.nome, config["subtitulo"], True)
  scan = gerarScan(perfil.usuario, perfil.avatarJpeg, montarCamposScan(config, perfil))
  gravarSvg("wordmark.svg", wordmark)
  gravarSvg("wordmark-mobile.svg", wordmarkMobile)
  gravarSvg("scan.svg", scan)
  gravarSvg("heatmap-jato.svg", gerarHeatmapJato(perfil.semanas, perfil.totalContribuicoes))
  gravarSvg("stack.svg", gerarStack(perfil.linguagens, config["stack"]))


def main() -> None:
  config = carregarConfig()
  perfil = buscarPerfilGithub(config["usuario"])
  PASTA_ASSETS.mkdir(exist_ok=True)
  gerarPaineis(config, perfil)


if __name__ == "__main__":
  main()
