from EP_Platform.modelos.schemas import (
    EnvioPrimeiraRodada,
    PreparacaoMotorProduto,
    ResultadoPrimeiraRodada,
)


def executar_primeira_rodada(
    preparacoes: list[PreparacaoMotorProduto],
) -> list[ResultadoPrimeiraRodada]:
    return [_executar_produto(preparacao) for preparacao in preparacoes]


def _executar_produto(
    preparacao: PreparacaoMotorProduto,
) -> ResultadoPrimeiraRodada:
    saldo_restante = _calcular_saldo_inicial(preparacao)
    saldo_inicial = saldo_restante
    envios: list[EnvioPrimeiraRodada] = []

    if saldo_restante <= 0:
        return ResultadoPrimeiraRodada(
            preparacao=preparacao,
            saldo_inicial=saldo_inicial,
            saldo_restante=saldo_restante,
            envios=envios,
        )

    for destino in preparacao.destinos_aptos:
        if saldo_restante <= 0:
            break

        if destino.registro.estoque.qt_estoque_comercial != 0:
            continue

        quantidade_enviar = min(saldo_restante, destino.capacidade, 1)

        if quantidade_enviar <= 0:
            continue

        saldo_restante -= quantidade_enviar
        envios.append(
            EnvioPrimeiraRodada(
                produto=preparacao.excesso.produto,
                origem=preparacao.excesso.origem,
                destino=destino.filial,
                quantidade_enviada=quantidade_enviar,
                saldo_restante=saldo_restante,
            )
        )

    return ResultadoPrimeiraRodada(
        preparacao=preparacao,
        saldo_inicial=saldo_inicial,
        saldo_restante=saldo_restante,
        envios=envios,
    )


def _calcular_saldo_inicial(preparacao: PreparacaoMotorProduto) -> float:
    if preparacao.registro_origem is None:
        return 0.0

    estoque_origem = preparacao.registro_origem.estoque.qt_estoque_comercial
    if estoque_origem <= 0:
        return 0.0

    return min(preparacao.excesso.qtde_excesso, estoque_origem)
