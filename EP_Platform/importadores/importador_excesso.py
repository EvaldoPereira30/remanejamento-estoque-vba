from pathlib import Path

from EP_Platform.importadores.importador_estoque import _ler_arquivo_planilha
from EP_Platform.modelos.schemas import ResultadoImportacao


def importar_excesso(caminho: str | Path) -> ResultadoImportacao:
    """Le o arquivo de excesso e retorna linhas brutas."""
    origem = Path(caminho)
    linhas = _ler_arquivo_planilha(origem)
    return ResultadoImportacao(origem=origem, tipo="excesso", linhas=linhas)

