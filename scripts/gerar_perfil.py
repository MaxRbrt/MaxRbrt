import json
from pathlib import Path

from dados_github import PerfilGithub, avatarComoDataUri, buscarPerfilGithub
from secao_heatmap import gerarHeatmapBorracha, gerarHeatmapCobra, gerarHeatmapJato
from secao_identidade import gerarDestaques, gerarHero
from secao_metricas import gerarSinais, gerarStack
from secao_projetos import gerarProjeto
from secao_scan import gerarScan
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
  principais = " · ".join(
    f"{linguagem.nome} {round(linguagem.percentual)}%" for linguagem in perfil.linguagens[:2]
  )
  return [
    ("usuário", f"@{perfil.usuario.lower()}"),
    ("nome", perfil.nome),
    ("função", "Desenvolvedor Full Stack"),
    ("formação", config["formacao"]),
    ("local", config["local"]),
    ("stack", " · ".join(config["etiquetas"][:5])),
    ("linguagens", principais),
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


def gerarSecoesIdentidade(config: dict, perfil: PerfilGithub) -> None:
  gravarSvg("wordmark.svg", gerarWordmark(perfil.usuario, perfil.nome, config["subtitulo"], False))
  gravarSvg("wordmark-mobile.svg", gerarWordmark(perfil.usuario, perfil.nome, config["subtitulo"], True))
  avatar = avatarComoDataUri(perfil.avatarJpeg, 192)
  hero = gerarHero(
    perfil.usuario,
    perfil.nome,
    perfil.bio,
    config["foco"],
    config["etiquetas"],
    perfil.totalContribuicoes,
    avatar,
  )
  gravarSvg("hero.svg", hero)
  gravarSvg("destaques.svg", gerarDestaques(config["destaques"]))


def gerarSecoesMetricas(config: dict, perfil: PerfilGithub) -> None:
  sinais = gerarSinais(
    perfil.totalContribuicoes,
    perfil.repositoriosPublicos,
    perfil.seguidores,
    perfil.estrelasRecebidas,
    perfil.semanas,
  )
  gravarSvg("sinais.svg", sinais)
  gravarSvg("stack.svg", gerarStack(perfil.linguagens, config["stack"]))
  gravarSvg("heatmap-jato.svg", gerarHeatmapJato(perfil.semanas, perfil.totalContribuicoes))
  gravarSvg("heatmap-cobra.svg", gerarHeatmapCobra(perfil.semanas, perfil.totalContribuicoes))
  gravarSvg("heatmap-borracha.svg", gerarHeatmapBorracha(perfil.semanas, perfil.totalContribuicoes))
  gravarSvg("scan.svg", gerarScan(perfil.usuario, perfil.avatarJpeg, montarCamposScan(config, perfil)))


def gerarSecoesProjetos(config: dict, perfil: PerfilGithub) -> None:
  for posicao, nome in enumerate(config["projetos"], start=1):
    repositorio = perfil.repositorios.get(nome)
    if repositorio is None:
      raise ValueError(f"Projeto \"{nome}\" não está entre os repositórios públicos de {perfil.usuario}")
    gravarSvg(f"projeto-{nome.lower()}.svg", gerarProjeto(posicao, repositorio))


def main() -> None:
  config = carregarConfig()
  perfil = buscarPerfilGithub(config["usuario"])
  PASTA_ASSETS.mkdir(exist_ok=True)
  gerarSecoesIdentidade(config, perfil)
  gerarSecoesMetricas(config, perfil)
  gerarSecoesProjetos(config, perfil)


if __name__ == "__main__":
  main()
