from pathlib import Path
from typing import Any

from EP_Platform.calculadoras.calculadora_capacidade import calcular_capacidade_estoque
from EP_Platform.exportadores.exportador_txt import exportar_layout_final_txt
from EP_Platform.geradores.gerador_layout_final import gerar_layout_final
from EP_Platform.geradores.gerador_sugestao import gerar_sugestao_remanejamento
from EP_Platform.importadores.importador_estoque import importar_estoque
from EP_Platform.importadores.importador_excesso import importar_excesso
from EP_Platform.motores.motor_primeira_rodada import executar_primeira_rodada
from EP_Platform.motores.motor_segunda_rodada import executar_segunda_rodada
from EP_Platform.motores.tratador_saldo_restante import registrar_saldos_remanescentes
from EP_Platform.normalizadores.normalizador_dados import (
    limpar_estoque,
    limpar_excesso,
    normalizar_estoque,
    normalizar_excesso,
)
from EP_Platform.preparadores.preparador_motor import preparar_dados_motor
from EP_Platform.validadores.validador_layout import (
    consolidar_validacoes,
    validar_estoque,
    validar_excesso,
)


def executar_remanejamento(
    caminho_estoque: str | Path,
    caminho_excesso: str | Path,
    pasta_saida: str | Path,
    dias_alvo: float = 90,
) -> dict[str, Any]:
    try:
        caminho_estoque = Path(caminho_estoque)
        caminho_excesso = Path(caminho_excesso)
        pasta_saida = Path(pasta_saida)

        estoque_importado = importar_estoque(caminho_estoque)
        excesso_importado = importar_excesso(caminho_excesso)

        estoque_limpo = limpar_estoque(estoque_importado.linhas)
        excesso_limpo = limpar_excesso(excesso_importado.linhas)

        validacao_estoque = validar_estoque(estoque_limpo)
        validacao_excesso = validar_excesso(excesso_limpo)
        validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

        if not validacao.valido:
            return _resultado_falha(
                "Validacao dos arquivos falhou.",
                validacao.erros,
                pasta_saida,
            )

        estoque_normalizado = normalizar_estoque(estoque_limpo)
        excesso_normalizado = normalizar_excesso(excesso_limpo)
        estoque_calculado = calcular_capacidade_estoque(
            estoque_normalizado,
            dias_alvo,
        )
        preparacoes = preparar_dados_motor(
            estoque_calculado,
            excesso_normalizado,
        )
        resultados_primeira = executar_primeira_rodada(preparacoes)
        resultados_segunda = executar_segunda_rodada(resultados_primeira)
        saldos_remanescentes = registrar_saldos_remanescentes(resultados_segunda)
        sugestoes = gerar_sugestao_remanejamento(
            resultados_segunda,
            saldos_remanescentes,
        )
        layout_final = gerar_layout_final(sugestoes)
        arquivos_txt = exportar_layout_final_txt(layout_final, pasta_saida)

        return {
            "sucesso": True,
            "mensagem": "Remanejamento executado com sucesso.",
            "quantidade_estoque": len(estoque_normalizado),
            "quantidade_excesso": len(excesso_normalizado),
            "quantidade_sugestao": len(sugestoes),
            "quantidade_layout_final": len(layout_final),
            "quantidade_txt_gerados": len(arquivos_txt),
            "arquivos_txt": [str(arquivo.caminho) for arquivo in arquivos_txt],
            "produtos_com_saldo_sem_destino": [
                saldo.produto for saldo in saldos_remanescentes
            ],
            "divergencias": [],
            "pasta_saida": str(pasta_saida),
        }
    except Exception as exc:  # noqa: BLE001 - API publica retorna falha controlada.
        return _resultado_falha(
            f"Erro ao executar remanejamento: {exc}",
            [str(exc)],
            Path(pasta_saida),
        )


def _resultado_falha(
    mensagem: str,
    divergencias: list[str],
    pasta_saida: Path,
) -> dict[str, Any]:
    return {
        "sucesso": False,
        "mensagem": mensagem,
        "quantidade_estoque": 0,
        "quantidade_excesso": 0,
        "quantidade_sugestao": 0,
        "quantidade_layout_final": 0,
        "quantidade_txt_gerados": 0,
        "arquivos_txt": [],
        "produtos_com_saldo_sem_destino": [],
        "divergencias": divergencias,
        "pasta_saida": str(pasta_saida),
    }
