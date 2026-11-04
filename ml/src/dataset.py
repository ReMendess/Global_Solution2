"""Descoberta, validação e divisão do dataset de imagens.

Estrutura esperada em `ml/data/raw` (uma pasta por classe, nomes exatos):

    ml/data/raw/REGULAR/...
    ml/data/raw/IRREGULAR/...

A divisão é estratificada e reprodutível (mesma semente → mesmo resultado) e o
resultado é gravado em `ml/data/processed/{train,val,test}/<CLASSE>`.
"""

from __future__ import annotations

import json
import math
import random
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from ml.src.config import (
    CLASSES,
    IMAGE_EXTENSIONS,
    PROCESSED_DIR,
    RAW_DIR,
    SEED,
    SPLITS,
    DatasetError,
)

# Mínimo para uma divisão com treino, validação e teste funcionais.
MIN_IMAGES_PER_CLASS = 10
# Abaixo disso o treinamento é possível, mas o resultado tende a ser fraco.
RECOMMENDED_IMAGES_PER_CLASS = 100


@dataclass(slots=True)
class DatasetSummary:
    """Resumo do dataset encontrado em disco."""

    counts: dict[str, int] = field(default_factory=dict)
    ignored_files: int = 0

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def as_dict(self) -> dict[str, object]:
        return {
            "counts": dict(self.counts),
            "total": self.total,
            "ignored_files": self.ignored_files,
        }


def list_images(directory: Path) -> list[Path]:
    """Lista as imagens suportadas de um diretório (busca não recursiva)."""
    if not directory.is_dir():
        return []
    return sorted(
        arquivo
        for arquivo in directory.iterdir()
        if arquivo.is_file() and arquivo.suffix.lower() in IMAGE_EXTENSIONS
    )


def discover(raw_dir: Path = RAW_DIR) -> DatasetSummary:
    """Valida o dataset bruto e devolve a contagem por classe.

    Levanta `DatasetError` com instrução clara quando o diretório não existe,
    quando falta alguma classe obrigatória ou quando há poucas imagens.
    """
    if not raw_dir.is_dir():
        raise DatasetError(
            f"Diretório do dataset não encontrado: {raw_dir}\n"
            f"Crie as pastas {', '.join(CLASSES)} dentro de ml/data/raw e adicione as imagens."
        )

    resumo = DatasetSummary()
    ausentes: list[str] = []

    for classe in CLASSES:
        pasta = raw_dir / classe
        imagens = list_images(pasta)
        resumo.counts[classe] = len(imagens)
        if not pasta.is_dir():
            ausentes.append(f"{classe} (pasta ausente)")
        elif not imagens:
            ausentes.append(f"{classe} (sem imagens)")

    if ausentes:
        raise DatasetError(
            "Dataset incompleto: " + "; ".join(ausentes) + ".\n"
            f"São necessárias as classes {', '.join(CLASSES)} com pelo menos "
            f"{MIN_IMAGES_PER_CLASS} imagens cada."
        )

    insuficientes = {
        classe: total for classe, total in resumo.counts.items() if total < MIN_IMAGES_PER_CLASS
    }
    if insuficientes:
        detalhe = ", ".join(f"{classe}={total}" for classe, total in insuficientes.items())
        raise DatasetError(
            f"Cada classe precisa de pelo menos {MIN_IMAGES_PER_CLASS} imagens. Recebido: {detalhe}."
        )

    # Arquivos sem extensão suportada ficam registrados para transparência.
    for classe in CLASSES:
        pasta = raw_dir / classe
        if pasta.is_dir():
            resumo.ignored_files += sum(
                1
                for arquivo in pasta.iterdir()
                if arquivo.is_file() and arquivo.suffix.lower() not in IMAGE_EXTENSIONS
            )

    return resumo


def warnings_for(summary: DatasetSummary) -> list[str]:
    """Lista avisos de qualidade do dataset (não impedem o treinamento)."""
    avisos: list[str] = []
    for classe, total in summary.counts.items():
        if total < RECOMMENDED_IMAGES_PER_CLASS:
            avisos.append(
                f"Classe {classe} tem {total} imagens; o recomendado é "
                f"{RECOMMENDED_IMAGES_PER_CLASS} ou mais."
            )
    if summary.ignored_files:
        avisos.append(f"{summary.ignored_files} arquivo(s) ignorado(s) por formato não suportado.")

    totais = list(summary.counts.values())
    if totais and max(totais) > 2 * min(totais):
        avisos.append("As classes estão desbalanceadas (mais de 2x de diferença entre elas).")
    return avisos


def _split_counts(total: int) -> dict[str, int]:
    """Distribui `total` entre treino, validação e teste garantindo 1 em cada."""
    treino = int(math.floor(total * SPLITS["train"]))
    validacao = int(math.floor(total * SPLITS["val"]))
    teste = total - treino - validacao

    # Garante pelo menos uma imagem em validação e teste quando possível.
    if total >= 3:
        if validacao == 0:
            validacao = 1
            treino -= 1
        if teste == 0:
            teste = 1
            treino -= 1
    return {"train": treino, "val": validacao, "test": teste}


def split_dataset(
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
    seed: int = SEED,
    clean: bool = True,
) -> dict[str, object]:
    """Divide o dataset bruto em treino/validação/teste e grava em disco.

    Devolve o manifesto com a contagem final por divisão e por classe.
    """
    resumo = discover(raw_dir)

    if clean and processed_dir.exists():
        shutil.rmtree(processed_dir)

    por_divisao: dict[str, dict[str, int]] = {"train": {}, "val": {}, "test": {}}
    manifesto: dict[str, object] = {
        "seed": seed,
        "splits": dict(SPLITS),
        "classes": list(CLASSES),
        "source_counts": dict(resumo.counts),
        "by_split": por_divisao,
    }

    for classe in CLASSES:
        imagens = list_images(raw_dir / classe)
        random.Random(seed).shuffle(imagens)
        quantidades = _split_counts(len(imagens))

        indice = 0
        for divisao in ("train", "val", "test"):
            destino = processed_dir / divisao / classe
            destino.mkdir(parents=True, exist_ok=True)
            selecionadas = imagens[indice : indice + quantidades[divisao]]
            indice += quantidades[divisao]
            for origem in selecionadas:
                shutil.copy2(origem, destino / origem.name)
            por_divisao[divisao][classe] = len(selecionadas)

    processed_dir.mkdir(parents=True, exist_ok=True)
    (processed_dir / "manifest.json").write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifesto


def count_split(processed_dir: Path, split: str) -> int:
    """Conta as imagens de uma divisão já processada."""
    base = processed_dir / split
    return sum(len(list_images(base / classe)) for classe in CLASSES)
