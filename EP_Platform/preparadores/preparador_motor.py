from collections import defaultdict

from EP_Platform.calculadoras.calculadora_capacidade import STATUS_PODE_ABSORVER
from EP_Platform.modelos.schemas import (
    DestinoApto,
    PreparacaoMotorProduto,
    RegistroEstoqueCalculado,
    RegistroExcesso,
)


def preparar_dados_motor(
    estoque_calculado: list[RegistroEstoqueCalculado],
    excessos: list[RegistroExcesso],
) -> list[PreparacaoMotorProduto]:
    estoque_por_produto = agrupar_estoque_por_produto(estoque_calculado)
    preparacoes: list[PreparacaoMotorProduto] = []

    for excesso in sorted(excessos, key=lambda item: item.produto):
        registros_produto = estoque_por_produto.get(excesso.produto, [])
        registro_origem = localizar_registro_origem(registros_produto, excesso)
        destinos_aptos = localizar_destinos_aptos(registros_produto, excesso.origem)

        preparacoes.append(
            PreparacaoMotorProduto(
                excesso=excesso,
                registro_origem=registro_origem,
                registros_produto=registros_produto,
                destinos_aptos=destinos_aptos,
            )
        )

    return preparacoes


def agrupar_estoque_por_produto(
    estoque_calculado: list[RegistroEstoqueCalculado],
) -> dict[str, list[RegistroEstoqueCalculado]]:
    agrupado: dict[str, list[RegistroEstoqueCalculado]] = defaultdict(list)

    for registro in estoque_calculado:
        agrupado[registro.estoque.cod_produto].append(registro)

    return {
        produto: sorted(
            registros,
            key=lambda item: (item.estoque.cod_produto, -item.estoque.media_f),
        )
        for produto, registros in sorted(agrupado.items())
    }


def localizar_registro_origem(
    registros_produto: list[RegistroEstoqueCalculado],
    excesso: RegistroExcesso,
) -> RegistroEstoqueCalculado | None:
    for registro in registros_produto:
        if registro.estoque.cod_filial == excesso.origem:
            return registro
    return None


def localizar_destinos_aptos(
    registros_produto: list[RegistroEstoqueCalculado],
    origem: str,
) -> list[DestinoApto]:
    destinos = [
        DestinoApto(registro=registro)
        for registro in registros_produto
        if registro.estoque.cod_filial != origem
        and registro.status_absorcao == STATUS_PODE_ABSORVER
    ]

    return sorted(
        destinos,
        key=lambda destino: (
            destino.registro.estoque.cod_produto,
            -destino.media_f,
        ),
    )
