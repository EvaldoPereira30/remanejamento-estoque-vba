from EP_Platform.modelos.schemas import RegistroEstoque, RegistroEstoqueCalculado


STATUS_SEM_MEDIA = "Sem Média"
STATUS_NAO_ABSORVE = "Não Absorve"
STATUS_PODE_ABSORVER = "Pode Absorver"


def calcular_capacidade_estoque(
    registros: list[RegistroEstoque],
    dias_alvo: float,
) -> list[RegistroEstoqueCalculado]:
    if dias_alvo <= 0:
        raise ValueError("Dias Alvo deve ser maior que zero.")

    return [_calcular_registro(registro, dias_alvo) for registro in registros]


def resumir_status_absorcao(
    registros: list[RegistroEstoqueCalculado],
) -> dict[str, int]:
    resumo = {
        STATUS_PODE_ABSORVER: 0,
        STATUS_NAO_ABSORVE: 0,
        STATUS_SEM_MEDIA: 0,
    }

    for registro in registros:
        resumo[registro.status_absorcao] = resumo.get(registro.status_absorcao, 0) + 1

    return resumo


def _calcular_registro(
    registro: RegistroEstoque,
    dias_alvo: float,
) -> RegistroEstoqueCalculado:
    media_30 = registro.media_f
    estoque_atual = registro.qt_estoque_comercial

    if media_30 <= 0:
        return RegistroEstoqueCalculado(
            estoque=registro,
            dias_estoque_atual=0.0,
            estoque_maximo=0.0,
            capacidade=0.0,
            status_absorcao=STATUS_SEM_MEDIA,
        )

    dias_estoque_atual = estoque_atual / (media_30 / 30)
    estoque_maximo = (media_30 / 30) * dias_alvo
    capacidade = max(0.0, estoque_maximo - estoque_atual)

    if dias_estoque_atual >= dias_alvo:
        status_absorcao = STATUS_NAO_ABSORVE
    else:
        status_absorcao = STATUS_PODE_ABSORVER

    return RegistroEstoqueCalculado(
        estoque=registro,
        dias_estoque_atual=dias_estoque_atual,
        estoque_maximo=estoque_maximo,
        capacidade=capacidade,
        status_absorcao=status_absorcao,
    )
