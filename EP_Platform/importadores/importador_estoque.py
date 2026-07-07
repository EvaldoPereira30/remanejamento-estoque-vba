from pathlib import Path
import xml.etree.ElementTree as ET

from EP_Platform.modelos.schemas import ResultadoImportacao


NAMESPACE_SS = "{urn:schemas-microsoft-com:office:spreadsheet}"


def importar_estoque(caminho: str | Path) -> ResultadoImportacao:
    """Le o arquivo de estoque e retorna linhas brutas da primeira planilha."""
    origem = Path(caminho)
    linhas = _ler_arquivo_planilha(origem)
    return ResultadoImportacao(origem=origem, tipo="estoque", linhas=linhas)


def _ler_arquivo_planilha(caminho: Path) -> list[list[str]]:
    texto_inicial = caminho.read_bytes()[:256].lstrip()

    if texto_inicial.startswith(b"<?xml") or texto_inicial.startswith(b"<Workbook"):
        return _ler_spreadsheetml(caminho)

    return _ler_texto_tabulado(caminho)


def _ler_spreadsheetml(caminho: Path) -> list[list[str]]:
    arvore = ET.parse(caminho)
    raiz = arvore.getroot()
    planilha = raiz.find(f"{NAMESPACE_SS}Worksheet")

    if planilha is None:
        return []

    tabela = planilha.find(f"{NAMESPACE_SS}Table")
    if tabela is None:
        return []

    linhas: list[list[str]] = []

    for linha_xml in tabela.findall(f"{NAMESPACE_SS}Row"):
        valores: list[str] = []
        indice_coluna = 1

        for celula in linha_xml.findall(f"{NAMESPACE_SS}Cell"):
            indice_attr = celula.attrib.get(f"{NAMESPACE_SS}Index")
            if indice_attr:
                indice_coluna = int(indice_attr)

            while len(valores) < indice_coluna - 1:
                valores.append("")

            dado = celula.find(f"{NAMESPACE_SS}Data")
            valores.append("" if dado is None or dado.text is None else str(dado.text))
            indice_coluna += 1

        linhas.append(valores)

    return linhas


def _ler_texto_tabulado(caminho: Path) -> list[list[str]]:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texto = caminho.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        texto = caminho.read_text()

    return [linha.split("\t") for linha in texto.splitlines()]

