from EP_Platform.normalizadores.normalizador_dados import COLUNAS_ESTOQUE
from EP_Platform.modelos.schemas import ResultadoValidacao


def validar_estoque(linhas_limpas: list[list[str]]) -> ResultadoValidacao:
    erros: list[str] = []
    avisos: list[str] = []

    if len(linhas_limpas) < 2:
        erros.append("O arquivo de estoque nao possui dados apos a limpeza.")
        return ResultadoValidacao.falha(erros)

    if not any(_valor(linha, 1) for linha in linhas_limpas[1:]):
        erros.append("O arquivo de estoque nao possui produtos validos na coluna B.")

    cabecalho = [_valor(linhas_limpas[0], indice) for indice in range(9)]
    if cabecalho != COLUNAS_ESTOQUE:
        avisos.append(
            "Cabecalho do estoque diferente do layout esperado; "
            "validacao mantida como aviso para preservar o comportamento atual do VBA."
        )

    if erros:
        return ResultadoValidacao.falha(erros, avisos)

    return ResultadoValidacao.ok(avisos)


def validar_excesso(linhas_limpas: list[list[str]]) -> ResultadoValidacao:
    erros: list[str] = []

    if len(linhas_limpas) < 2:
        return ResultadoValidacao.falha(
            ["O arquivo de excesso nao possui dados apos a limpeza."]
        )

    linha_2 = linhas_limpas[1]

    if not _valor(linha_2, 0) or not _eh_numero(_valor(linha_2, 0)):
        erros.append("Coluna A deve conter a filial numerica na linha 2.")

    if not _valor(linha_2, 1) or not _eh_numero(_valor(linha_2, 1)):
        erros.append("Coluna B deve conter o codigo do produto numerico na linha 2.")

    if not _valor(linha_2, 2) or _eh_numero(_valor(linha_2, 2)):
        erros.append("Coluna C deve conter a descricao textual do produto na linha 2.")

    if not _valor(linha_2, 3) or not _eh_numero(_valor(linha_2, 3)):
        erros.append("Coluna D deve conter a quantidade numerica na linha 2.")

    if _valor(linha_2, 4):
        erros.append(
            "Coluna E deve estar vazia; a quantidade pode ter sido deslocada."
        )

    if erros:
        return ResultadoValidacao.falha(erros)

    return ResultadoValidacao.ok()


def consolidar_validacoes(
    validacao_estoque: ResultadoValidacao,
    validacao_excesso: ResultadoValidacao,
) -> ResultadoValidacao:
    erros = [*validacao_estoque.erros, *validacao_excesso.erros]
    avisos = [*validacao_estoque.avisos, *validacao_excesso.avisos]

    if erros:
        return ResultadoValidacao.falha(erros, avisos)

    return ResultadoValidacao.ok(avisos)


def _valor(linha: list[str], indice: int) -> str:
    if indice >= len(linha):
        return ""
    return str(linha[indice]).strip()


def _eh_numero(valor: str) -> bool:
    try:
        float(valor.strip().replace(",", "."))
        return True
    except ValueError:
        return False

