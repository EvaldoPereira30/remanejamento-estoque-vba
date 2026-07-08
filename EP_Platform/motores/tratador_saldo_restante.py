from EP_Platform.modelos.schemas import ResultadoSegundaRodada, SaldoRemanescente


DESTINO_SEM_LOJA = "Sem loja destino"


def registrar_saldos_remanescentes(
    resultados_segunda_rodada: list[ResultadoSegundaRodada],
) -> list[SaldoRemanescente]:
    saldos: list[SaldoRemanescente] = []

    for resultado in resultados_segunda_rodada:
        if resultado.saldo_restante <= 0:
            continue

        excesso = resultado.resultado_primeira_rodada.preparacao.excesso
        saldos.append(
            SaldoRemanescente(
                destino=DESTINO_SEM_LOJA,
                produto=excesso.produto,
                origem=excesso.origem,
                quantidade_excesso_original=excesso.qtde_excesso,
                saldo_restante=resultado.saldo_restante,
                quantidade_sugerida=0.0,
                dias_destino=None,
                capacidade=None,
                dias_apos=None,
            )
        )

    return saldos
