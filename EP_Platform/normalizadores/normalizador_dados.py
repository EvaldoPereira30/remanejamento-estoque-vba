from EP_Platform.modelos.schemas import RegistroEstoque, RegistroExcesso


COLUNAS_ESTOQUE = [
    "CodFilial",
    "CodProduto",
    "EAN",
    "Descricao",
    "Fabricante",
    "Linha",
    "StatusProduto",
    "MediaF",
    "QtEstoqueComercial",
]

COLUNAS_EXCESSO = [
    "Origem",
    "Produto",
    "Descricao",
    "QtdeExcesso",
]


def limpar_estoque(linhas: list[list[str]]) -> list[list[str]]:
    """Reproduz a preparacao inicial do estoque feita pelo VBA."""
    linhas_limpas = [_normalizar_largura(linha, 9) for linha in linhas[2:]]
    linhas_limpas = _remover_rodapes(linhas_limpas)
    return _propagar_filial_em_branco(linhas_limpas)


def limpar_excesso(linhas: list[list[str]]) -> list[list[str]]:
    """Reproduz a preparacao inicial do excesso feita pelo VBA."""
    linhas_limpas = [_normalizar_largura(linha, 5) for linha in linhas]

    indice_cabecalho = _encontrar_linha_codfilial(linhas_limpas)
    if indice_cabecalho and indice_cabecalho > 0:
        linhas_limpas = linhas_limpas[indice_cabecalho:]

    linhas_limpas = _remover_rodapes(linhas_limpas)
    return _propagar_filial_em_branco(linhas_limpas)


def normalizar_estoque(linhas_limpas: list[list[str]]) -> list[RegistroEstoque]:
    registros: list[RegistroEstoque] = []

    for indice, linha in enumerate(linhas_limpas[1:], start=2):
        if not _valor(linha, 1):
            continue

        registros.append(
            RegistroEstoque(
                cod_filial=_valor(linha, 0),
                cod_produto=_valor(linha, 1),
                ean=_valor(linha, 2),
                descricao=_valor(linha, 3),
                fabricante=_valor(linha, 4),
                linha=_valor(linha, 5),
                status_produto=_valor(linha, 6),
                media_f=_para_float(_valor(linha, 7)),
                qt_estoque_comercial=_para_float(_valor(linha, 8)),
                linha_origem=indice,
            )
        )

    return registros


def normalizar_excesso(linhas_limpas: list[list[str]]) -> list[RegistroExcesso]:
    registros: list[RegistroExcesso] = []

    for indice, linha in enumerate(linhas_limpas[1:], start=2):
        if not _valor(linha, 1):
            continue

        registros.append(
            RegistroExcesso(
                origem=_valor(linha, 0),
                produto=_valor(linha, 1),
                descricao=_valor(linha, 2),
                qtde_excesso=_para_float(_valor(linha, 3)),
                linha_origem=indice,
            )
        )

    return registros


def _remover_rodapes(linhas: list[list[str]]) -> list[list[str]]:
    if not linhas:
        return []

    resultado = [linhas[0]]

    for linha in linhas[1:]:
        coluna_a = _valor(linha, 0)
        if "H:" in coluna_a or "Usuario:" in coluna_a or "Usuário:" in coluna_a:
            continue
        resultado.append(linha)

    return resultado


def _propagar_filial_em_branco(linhas: list[list[str]]) -> list[list[str]]:
    if not linhas:
        return []

    resultado = [linhas[0]]
    filial_atual = ""

    for linha in linhas[1:]:
        nova_linha = list(linha)
        filial = _valor(nova_linha, 0)

        if filial:
            filial_atual = filial
        elif filial_atual:
            nova_linha[0] = filial_atual

        resultado.append(nova_linha)

    return resultado


def _encontrar_linha_codfilial(linhas: list[list[str]]) -> int | None:
    for indice, linha in enumerate(linhas):
        if "CodFilial".lower() in _valor(linha, 0).lower():
            return indice
    return None


def _normalizar_largura(linha: list[str], largura_minima: int) -> list[str]:
    valores = ["" if valor is None else str(valor) for valor in linha]
    while len(valores) < largura_minima:
        valores.append("")
    return valores


def _valor(linha: list[str], indice: int) -> str:
    if indice >= len(linha):
        return ""
    return str(linha[indice]).strip()


def _para_float(valor: str) -> float:
    texto = valor.strip()
    if not texto:
        return 0.0

    try:
        return float(texto.replace(",", "."))
    except ValueError:
        return 0.0

