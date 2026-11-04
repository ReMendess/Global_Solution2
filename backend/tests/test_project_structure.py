"""Testes da FASE 0 — validação da estrutura e da documentação do repositório.

Estes testes não exercitam regra de negócio: eles garantem que o esqueleto criado na fase de
planejamento está íntegro e que a configuração de lint/testes do projeto funciona.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

# Raiz do repositório: este arquivo está em <raiz>/backend/tests/.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DIRETORIOS_OBRIGATORIOS = [
    "backend/app/api/routes",
    "backend/app/core",
    "backend/app/db",
    "backend/app/models",
    "backend/app/schemas",
    "backend/app/services",
    "backend/tests",
    "frontend",
    "ml/notebooks",
    "ml/src",
    "ml/data/raw",
    "ml/data/processed",
    "ml/models",
    "ml/reports",
    "simulator/core",
    "simulator/sensors",
    "rpa/bot",
    "rpa/portal",
    "rpa/screenshots",
    "rpa/reports",
    "data/uploads",
    "docs",
]

ARQUIVOS_OBRIGATORIOS = [
    ".gitignore",
    ".editorconfig",
    ".env.example",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "README.md",
]

DOCUMENTOS_DE_PLANEJAMENTO = [
    "docs/PROJECT_CONTEXT.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_MODEL.md",
    "docs/API_SPEC.md",
    "docs/BUSINESS_RULES.md",
    "docs/ROADMAP.md",
    "docs/DECISIONS.md",
    "docs/ENVIRONMENT.md",
]


@pytest.mark.unit
@pytest.mark.parametrize("caminho", DIRETORIOS_OBRIGATORIOS)
def test_diretorio_obrigatorio_existe(caminho: str) -> None:
    """Cada diretório do esqueleto planejado deve existir no repositório."""
    assert (PROJECT_ROOT / caminho).is_dir(), f"diretório ausente: {caminho}"


@pytest.mark.unit
@pytest.mark.parametrize("caminho", ARQUIVOS_OBRIGATORIOS)
def test_arquivo_obrigatorio_existe(caminho: str) -> None:
    """Arquivos de governança do projeto devem estar presentes e não vazios."""
    arquivo = PROJECT_ROOT / caminho
    assert arquivo.is_file(), f"arquivo ausente: {caminho}"
    assert arquivo.stat().st_size > 0, f"arquivo vazio: {caminho}"


@pytest.mark.unit
@pytest.mark.parametrize("caminho", DOCUMENTOS_DE_PLANEJAMENTO)
def test_documento_de_planejamento_existe(caminho: str) -> None:
    """A FASE 0 só é concluída com a documentação de planejamento completa."""
    documento = PROJECT_ROOT / caminho
    assert documento.is_file(), f"documento ausente: {caminho}"
    assert len(documento.read_text(encoding="utf-8").strip()) > 200, (
        f"documento com conteúdo insuficiente: {caminho}"
    )


@pytest.mark.unit
def test_diretorios_vazios_sao_versionaveis() -> None:
    """Diretórios sem conteúdo real precisam de .gitkeep para irem para o git."""
    vazios_sem_marcador = [
        caminho
        for caminho in DIRETORIOS_OBRIGATORIOS
        if not any((PROJECT_ROOT / caminho).iterdir())
    ]
    marcados = [
        caminho
        for caminho in vazios_sem_marcador
        if (PROJECT_ROOT / caminho / ".gitkeep").is_file()
    ]
    assert vazios_sem_marcador == marcados


@pytest.mark.unit
def test_pyproject_configura_pytest_e_ruff() -> None:
    """O pyproject.toml deve concentrar a configuração de testes e lint."""
    conteudo = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "pytest" in conteudo["tool"], "seção [tool.pytest.ini_options] ausente"
    assert "ruff" in conteudo["tool"], "seção [tool.ruff] ausente"

    pytest_opcoes = conteudo["tool"]["pytest"]["ini_options"]
    assert "backend/tests" in pytest_opcoes["testpaths"], "backend/tests ausente em testpaths"
    assert "simulator/tests" in pytest_opcoes["testpaths"], "simulator/tests ausente em testpaths"
    assert "--strict-markers" in pytest_opcoes["addopts"]
    assert conteudo["tool"]["ruff"]["line-length"] > 0


@pytest.mark.unit
def test_env_example_nao_contem_segredo_real() -> None:
    """O arquivo de exemplo não pode carregar credenciais verdadeiras."""
    texto = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    assert "DATABASE_URL" in texto
    assert "CONFIDENCE_THRESHOLD" in texto
    for proibido in ("BEGIN PRIVATE KEY", "AKIA", "ghp_"):
        assert proibido not in texto


@pytest.mark.unit
def test_gitignore_protege_artefatos() -> None:
    """Banco, uploads, pesos de modelo e .env não devem ser versionados."""
    linhas = {
        linha.strip()
        for linha in (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if linha.strip() and not linha.strip().startswith("#")
    }
    for esperado in (".env", "__pycache__/", "node_modules/", "*.keras", "data/*.db"):
        assert esperado in linhas, f"regra ausente no .gitignore: {esperado}"
