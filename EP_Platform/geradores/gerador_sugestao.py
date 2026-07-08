from EP_Platform.modelos.schemas import (
    DestinoApto,
    EnvioPrimeiraRodada,
    EnvioSegundaRodada,
    PreparacaoMotorProduto,
    RegistroSugestaoRemanejamento,
    ResultadoSegundaRodada,
    SaldoRemanescente,
)


def gerar_sugestao_remanejamento(
    resultados_segunda_rodada: list[ResultadoSegundaRodada],
    saldos_remanescentes: list[SaldoRemanescente],
) -> list[RegistroSugestaoRemanejamento]:
    saldos_disponiveis = list(saldos_remanescentes)
    sugestoes: list[RegistroSugestaoRemanejamento] = []

    for resultado in resultados_segunda_rodada:
        preparacao = resultado.resultado_primeira_rodada.preparacao

        for envio in resultado.resultado_primeira_rodada.envios:
            sugestoes.append(_criar_registro_envio(preparacao, envio))

        for envio in resultado.envios:
            sugestoes.append(_criar_registro_envio(preparacao, envio))

        saldo = _localizar_saldo_remanescente(
            preparacao,
            resultado.saldo_restante,
            saldos_disponiveis,
        )
        if saldo is not None:
            sugestoes.append(_criar_registro_saldo(preparacao, saldo))
            saldos_disponiveis.remove(saldo)

    return sugestoes


def _criar_registro_envio(
    preparacao: PreparacaoMotorProduto,
    envio: EnvioPrimeiraRodada | EnvioSegundaRodada,
) -> RegistroSugestaoRemanejamento:
    destino = _localizar_destino(preparacao.destinos_aptos, envio.destino)

    return RegistroSugestaoRemanejamento(
        origem=envio.origem,
        produto=envio.produto,
        descricao=preparacao.excesso.descricao,
        quantidade_excesso_original=preparacao.excesso.qtde_excesso,
        destino=envio.destino,
        dias_atuais_destino=destino.registro.dias_estoque_atual,
        capacidade=destino.registro.capacidade,
        quantidade_sugerida=envio.quantidade_enviada,
        dias_apos_envio=_calcular_dias_apos_envio(
            destino,
            envio.quantidade_enviada,
        ),
        saldo_restante=envio.saldo_restante,
    )


def _criar_registro_saldo(
    preparacao: PreparacaoMotorProduto,
    saldo: SaldoRemanescente,
) -> RegistroSugestaoRemanejamento:
    return RegistroSugestaoRemanejamento(
        origem=saldo.origem,
        produto=saldo.produto,
        descricao=preparacao.excesso.descricao,
        quantidade_excesso_original=saldo.quantidade_excesso_original,
        destino=saldo.destino,
        dias_atuais_destino=saldo.dias_destino,
        capacidade=saldo.capacidade,
        quantidade_sugerida=saldo.quantidade_sugerida,
        dias_apos_envio=saldo.dias_apos,
        saldo_restante=saldo.saldo_restante,
    )


def _localizar_saldo_remanescente(
    preparacao: PreparacaoMotorProduto,
    saldo_restante: float,
    saldos: list[SaldoRemanescente],
) -> SaldoRemanescente | None:
    excesso = preparacao.excesso

    for saldo in saldos:
        if (
            saldo.origem == excesso.origem
            and saldo.produto == excesso.produto
            and saldo.quantidade_excesso_original == excesso.qtde_excesso
            and saldo.saldo_restante == saldo_restante
        ):
            return saldo

    return None


def _localizar_destino(
    destinos: list[DestinoApto],
    filial: str,
) -> DestinoApto:
    for destino in destinos:
        if destino.filial == filial:
            return destino

    raise ValueError(f"Destino {filial} nao encontrado na preparacao do motor.")


def _calcular_dias_apos_envio(
    destino: DestinoApto,
    quantidade_enviada: float,
) -> float | None:
    media = destino.registro.estoque.media_f
    if media <= 0:
        return None

    estoque_apos_envio = (
        destino.registro.estoque.qt_estoque_comercial + quantidade_enviada
    )
    return estoque_apos_envio / (media / 30)
