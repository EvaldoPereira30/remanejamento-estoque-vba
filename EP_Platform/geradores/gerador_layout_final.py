from decimal import Decimal, ROUND_HALF_UP

from EP_Platform.motores.tratador_saldo_restante import DESTINO_SEM_LOJA
from EP_Platform.modelos.schemas import (
    RegistroLayoutFinal,
    RegistroSugestaoRemanejamento,
)


def gerar_layout_final(
    sugestoes: list[RegistroSugestaoRemanejamento],
) -> list[RegistroLayoutFinal]:
    registros = [
        registro
        for sugestao in sugestoes
        if (registro := _converter_sugestao(sugestao)) is not None
    ]

    return sorted(
        registros,
        key=lambda registro: (
            _chave_ordenacao_filial(registro.destino),
            _chave_ordenacao_filial(registro.origem),
        ),
    )


def _converter_sugestao(
    sugestao: RegistroSugestaoRemanejamento,
) -> RegistroLayoutFinal | None:
    if sugestao.destino == DESTINO_SEM_LOJA:
        return None

    quantidade_enviar = _arredondar_quantidade(sugestao.quantidade_sugerida)
    if quantidade_enviar <= 0:
        return None

    return RegistroLayoutFinal(
        destino=sugestao.destino,
        origem=sugestao.origem,
        produto=sugestao.produto,
        descricao=sugestao.descricao,
        quantidade_enviar=quantidade_enviar,
    )


def _arredondar_quantidade(quantidade: float) -> int:
    return int(
        Decimal(str(quantidade)).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


def _chave_ordenacao_filial(filial: str) -> tuple[int, int | str]:
    if filial.isdigit():
        return 0, int(filial)

    return 1, filial
