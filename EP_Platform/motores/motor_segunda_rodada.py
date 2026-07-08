from EP_Platform.modelos.schemas import (
    EnvioSegundaRodada,
    ResultadoPrimeiraRodada,
    ResultadoSegundaRodada,
)


def executar_segunda_rodada(
    resultados_primeira_rodada: list[ResultadoPrimeiraRodada],
) -> list[ResultadoSegundaRodada]:
    return [
        _executar_produto(resultado_primeira_rodada)
        for resultado_primeira_rodada in resultados_primeira_rodada
    ]


def _executar_produto(
    resultado_primeira_rodada: ResultadoPrimeiraRodada,
) -> ResultadoSegundaRodada:
    preparacao = resultado_primeira_rodada.preparacao
    saldo_restante = resultado_primeira_rodada.saldo_restante
    saldo_apos_primeira_rodada = saldo_restante
    envios: list[EnvioSegundaRodada] = []

    if saldo_restante <= 0:
        return ResultadoSegundaRodada(
            resultado_primeira_rodada=resultado_primeira_rodada,
            saldo_apos_primeira_rodada=saldo_apos_primeira_rodada,
            saldo_restante=saldo_restante,
            envios=envios,
        )

    for destino in preparacao.destinos_aptos:
        if saldo_restante <= 0:
            break

        if destino.registro.estoque.qt_estoque_comercial <= 0:
            continue

        quantidade_enviar = min(saldo_restante, destino.capacidade)

        if quantidade_enviar <= 0:
            continue

        saldo_restante -= quantidade_enviar
        envios.append(
            EnvioSegundaRodada(
                produto=preparacao.excesso.produto,
                origem=preparacao.excesso.origem,
                destino=destino.filial,
                quantidade_enviada=quantidade_enviar,
                saldo_restante=saldo_restante,
            )
        )

    return ResultadoSegundaRodada(
        resultado_primeira_rodada=resultado_primeira_rodada,
        saldo_apos_primeira_rodada=saldo_apos_primeira_rodada,
        saldo_restante=saldo_restante,
        envios=envios,
    )
