import io
import json
import os
import urllib.request
from dataclasses import dataclass

from PIL import Image

# ============================================================
# 1. MODELOS DOS DADOS PÚBLICOS
# ============================================================


@dataclass
class DiaContribuicao:
  data: str
  diaSemana: int
  quantidade: int
  nivel: int


@dataclass
class Linguagem:
  nome: str
  percentual: float


@dataclass
class PerfilGithub:
  usuario: str
  nome: str
  avatarJpeg: bytes
  seguidores: int
  repositoriosPublicos: int
  estrelasRecebidas: int
  totalContribuicoes: int
  semanas: list[list[DiaContribuicao]]
  linguagens: list[Linguagem]


# ============================================================
# 2. CONSULTA GRAPHQL
# ============================================================

URL_GRAPHQL = "https://api.github.com/graphql"

NIVEIS_CONTRIBUICAO = {
  "NONE": 0,
  "FIRST_QUARTILE": 1,
  "SECOND_QUARTILE": 2,
  "THIRD_QUARTILE": 3,
  "FOURTH_QUARTILE": 4,
}

CONSULTA_PERFIL = """
query($login: String!) {
  user(login: $login) {
    login
    name
    avatarUrl(size: 400)
    followers { totalCount }
    publicos: repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER) {
      totalCount
      nodes {
        isFork
        stargazerCount
        languages(first: 10) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date weekday contributionCount contributionLevel }
        }
      }
    }
  }
}
"""


def lerTokenGithub() -> str:
  token = os.environ.get("GITHUB_TOKEN", "").strip()
  if not token:
    raise RuntimeError("GITHUB_TOKEN vazio: esperado um token com leitura de dados públicos")
  return token


def executarConsultaGraphql(token: str, usuario: str) -> dict[str, object]:
  corpo = json.dumps({"query": CONSULTA_PERFIL, "variables": {"login": usuario}}).encode()
  requisicao = urllib.request.Request(URL_GRAPHQL, data=corpo, method="POST")
  requisicao.add_header("Authorization", f"Bearer {token}")
  requisicao.add_header("Content-Type", "application/json")
  requisicao.add_header("User-Agent", "gerador-perfil-readme")
  with urllib.request.urlopen(requisicao, timeout=30) as resposta:
    resultado = json.loads(resposta.read())
  if resultado.get("errors"):
    raise RuntimeError(f"GraphQL respondeu erro para \"{usuario}\": {resultado['errors']}")
  usuarioEncontrado = resultado["data"]["user"]
  if usuarioEncontrado is None:
    raise RuntimeError(f"Usuário \"{usuario}\" não encontrado no GitHub")
  return usuarioEncontrado


# ============================================================
# 3. AVATAR EMBUTIDO
# ============================================================


def baixarAvatarJpeg(url: str) -> bytes:
  requisicao = urllib.request.Request(url, headers={"User-Agent": "gerador-perfil-readme"})
  with urllib.request.urlopen(requisicao, timeout=30) as resposta:
    original = resposta.read()
  imagem = Image.open(io.BytesIO(original)).convert("RGB")
  imagem = imagem.resize((400, 400), Image.LANCZOS)
  saida = io.BytesIO()
  imagem.save(saida, format="JPEG", quality=88)
  return saida.getvalue()


# ============================================================
# 4. CONVERSÃO PARA O MODELO
# ============================================================


def converterSemanas(calendario: dict) -> list[list[DiaContribuicao]]:
  semanas = []
  for semana in calendario["weeks"]:
    dias = [
      DiaContribuicao(
        data=dia["date"],
        diaSemana=dia["weekday"],
        quantidade=dia["contributionCount"],
        nivel=NIVEIS_CONTRIBUICAO[dia["contributionLevel"]],
      )
      for dia in semana["contributionDays"]
    ]
    semanas.append(dias)
  return semanas


def calcularLinguagens(repos: list[dict]) -> list[Linguagem]:
  bytesPorLinguagem: dict[str, int] = {}
  for repo in repos:
    if repo["isFork"]:
      continue
    for aresta in repo["languages"]["edges"]:
      nome = aresta["node"]["name"]
      bytesPorLinguagem[nome] = bytesPorLinguagem.get(nome, 0) + aresta["size"]
  total = sum(bytesPorLinguagem.values()) or 1
  ordenadas = sorted(bytesPorLinguagem.items(), key=lambda item: -item[1])
  return [Linguagem(nome, round(tamanho * 100 / total, 1)) for nome, tamanho in ordenadas]


def buscarPerfilGithub(usuario: str) -> PerfilGithub:
  dados = executarConsultaGraphql(lerTokenGithub(), usuario)
  repos = dados["publicos"]["nodes"]
  calendario = dados["contributionsCollection"]["contributionCalendar"]
  return PerfilGithub(
    usuario=dados["login"],
    nome=dados["name"] or dados["login"],
    avatarJpeg=baixarAvatarJpeg(dados["avatarUrl"]),
    seguidores=dados["followers"]["totalCount"],
    repositoriosPublicos=dados["publicos"]["totalCount"],
    estrelasRecebidas=sum(repo["stargazerCount"] for repo in repos),
    totalContribuicoes=calendario["totalContributions"],
    semanas=converterSemanas(calendario),
    linguagens=calcularLinguagens(repos),
  )
