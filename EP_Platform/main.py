import tempfile
from pathlib import Path

from EP_Platform.calculadoras.calculadora_capacidade import (
    STATUS_NAO_ABSORVE,
    STATUS_PODE_ABSORVER,
    STATUS_SEM_MEDIA,
    calcular_capacidade_estoque,
    resumir_status_absorcao,
)
from EP_Platform.exportadores.exportador_txt import exportar_layout_final_txt
from EP_Platform.geradores.gerador_layout_final import gerar_layout_final
from EP_Platform.geradores.gerador_sugestao import gerar_sugestao_remanejamento
from EP_Platform.importadores.importador_estoque import importar_estoque
from EP_Platform.importadores.importador_excesso import importar_excesso
from EP_Platform.normalizadores.normalizador_dados import (
    limpar_estoque,
    limpar_excesso,
    normalizar_estoque,
    normalizar_excesso,
)
from EP_Platform.motores.motor_primeira_rodada import executar_primeira_rodada
from EP_Platform.motores.motor_segunda_rodada import executar_segunda_rodada
from EP_Platform.motores.tratador_saldo_restante import registrar_saldos_remanescentes
from EP_Platform.preparadores.preparador_motor import preparar_dados_motor
from EP_Platform.validadores.validador_layout import (
    consolidar_validacoes,
    validar_estoque,
    validar_excesso,
)


def executar_sprint_1(
    caminho_estoque: Path,
    caminho_excesso: Path,
) -> tuple[int, int]:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)

    print(f"Estoque importado: {len(estoque_normalizado)} linhas")
    print(f"Excesso importado: {len(excesso_normalizado)} linhas")
    print("Validacoes: OK")

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return len(estoque_normalizado), len(excesso_normalizado)


def executar_sprint_2a(
    caminho_estoque: Path,
    dias_alvo: float = 90,
) -> tuple[int, dict[str, int]]:
    estoque_importado = importar_estoque(caminho_estoque)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)

    if not validacao_estoque.valido:
        print("Validacoes: ERRO")
        for erro in validacao_estoque.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    resumo = resumir_status_absorcao(estoque_calculado)

    print(f"Total de registros: {len(estoque_calculado)}")
    print(f"Quantidade {STATUS_PODE_ABSORVER}: {resumo[STATUS_PODE_ABSORVER]}")
    print(f"Quantidade {STATUS_NAO_ABSORVE}: {resumo[STATUS_NAO_ABSORVE]}")
    print(f"Quantidade {STATUS_SEM_MEDIA}: {resumo[STATUS_SEM_MEDIA]}")

    for aviso in validacao_estoque.avisos:
        print(f"Aviso: {aviso}")

    return len(estoque_calculado), resumo


def executar_sprint_2b(
    caminho_estoque: Path,
    caminho_excesso: Path,
    dias_alvo: float = 90,
) -> int:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    preparacoes = preparar_dados_motor(estoque_calculado, excesso_normalizado)

    for preparacao in preparacoes:
        print(f"Produto: {preparacao.excesso.produto}")
        print(f"Origem: Loja {preparacao.excesso.origem}")
        print(f"Quantidade em excesso: {preparacao.excesso.qtde_excesso:g}")
        print(f"Destinos aptos encontrados: {len(preparacao.destinos_aptos)}")
        print(
            "Capacidade total disponível: "
            f"{preparacao.capacidade_total_disponivel:.2f}"
        )
        print()

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return len(preparacoes)


def executar_sprint_3a(
    caminho_estoque: Path,
    caminho_excesso: Path,
    dias_alvo: float = 90,
) -> int:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    preparacoes = preparar_dados_motor(estoque_calculado, excesso_normalizado)
    resultados = executar_primeira_rodada(preparacoes)

    total_envios = 0

    for resultado in resultados:
        print(f"Produto {resultado.preparacao.excesso.produto}")
        print(f"Saldo inicial: {resultado.saldo_inicial:g}")

        if not resultado.envios:
            print("Nenhum envio na primeira rodada")

        for envio in resultado.envios:
            total_envios += 1
            print(f"Destino {envio.destino}")
            print(f"Quantidade enviada: {envio.quantidade_enviada:g}")
            print(f"Saldo restante: {envio.saldo_restante:g}")

        print()

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return total_envios


def executar_sprint_3b(
    caminho_estoque: Path,
    caminho_excesso: Path,
    dias_alvo: float = 90,
) -> int:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    preparacoes = preparar_dados_motor(estoque_calculado, excesso_normalizado)
    resultados_primeira = executar_primeira_rodada(preparacoes)
    resultados_segunda = executar_segunda_rodada(resultados_primeira)

    total_envios = 0

    for resultado in resultados_segunda:
        produto = resultado.resultado_primeira_rodada.preparacao.excesso.produto
        print(f"Produto {produto}")
        print(
            "Saldo após primeira rodada: "
            f"{resultado.saldo_apos_primeira_rodada:g}"
        )

        if not resultado.envios:
            print("Nenhum envio na segunda rodada")

        for envio in resultado.envios:
            total_envios += 1
            print(f"Destino {envio.destino}")
            print(
                "Quantidade enviada segunda rodada: "
                f"{envio.quantidade_enviada:g}"
            )
            print(f"Saldo restante: {envio.saldo_restante:g}")

        print()

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return total_envios


def executar_sprint_3c(
    caminho_estoque: Path,
    caminho_excesso: Path,
    dias_alvo: float = 90,
) -> tuple[int, int]:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    preparacoes = preparar_dados_motor(estoque_calculado, excesso_normalizado)
    resultados_primeira = executar_primeira_rodada(preparacoes)
    resultados_segunda = executar_segunda_rodada(resultados_primeira)
    saldos_remanescentes = registrar_saldos_remanescentes(resultados_segunda)

    produtos_totalmente_distribuidos = (
        len(resultados_segunda) - len(saldos_remanescentes)
    )

    print(
        "Quantidade de produtos totalmente distribuídos: "
        f"{produtos_totalmente_distribuidos}"
    )
    print(
        "Quantidade de produtos com saldo remanescente: "
        f"{len(saldos_remanescentes)}"
    )

    if saldos_remanescentes:
        print("Lista dos produtos registrados como Sem loja destino:")

    for saldo in saldos_remanescentes:
        print(f"Produto {saldo.produto}")
        print(f"Saldo restante: {saldo.saldo_restante:g}")
        print("Status:")
        print(saldo.destino)
        print()

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return produtos_totalmente_distribuidos, len(saldos_remanescentes)


def executar_sprint_4(
    caminho_estoque: Path,
    caminho_excesso: Path,
    dias_alvo: float = 90,
) -> tuple[int, int]:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    preparacoes = preparar_dados_motor(estoque_calculado, excesso_normalizado)
    resultados_primeira = executar_primeira_rodada(preparacoes)
    resultados_segunda = executar_segunda_rodada(resultados_primeira)
    saldos_remanescentes = registrar_saldos_remanescentes(resultados_segunda)
    sugestoes = gerar_sugestao_remanejamento(
        resultados_segunda,
        saldos_remanescentes,
    )

    registros_sem_loja = [
        sugestao
        for sugestao in sugestoes
        if sugestao.destino == "Sem loja destino"
    ]

    print(f"Quantidade total de registros gerados: {len(sugestoes)}")
    print(
        'Quantidade de registros "Sem loja destino": '
        f"{len(registros_sem_loja)}"
    )
    print("Primeiros registros gerados:")

    for sugestao in sugestoes[:10]:
        print(
            f"Origem: {sugestao.origem} | "
            f"Produto: {sugestao.produto} | "
            f"Destino: {sugestao.destino} | "
            f"Quantidade sugerida: {sugestao.quantidade_sugerida:g} | "
            f"Saldo restante: {sugestao.saldo_restante:g}"
        )
        print(
            "Dias atuais destino: "
            f"{_formatar_valor_opcional(sugestao.dias_atuais_destino)} | "
            f"Capacidade: {_formatar_valor_opcional(sugestao.capacidade)} | "
            "Dias apos envio: "
            f"{_formatar_valor_opcional(sugestao.dias_apos_envio)}"
        )

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return len(sugestoes), len(registros_sem_loja)


def executar_sprint_5(
    caminho_estoque: Path,
    caminho_excesso: Path,
    dias_alvo: float = 90,
) -> int:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    preparacoes = preparar_dados_motor(estoque_calculado, excesso_normalizado)
    resultados_primeira = executar_primeira_rodada(preparacoes)
    resultados_segunda = executar_segunda_rodada(resultados_primeira)
    saldos_remanescentes = registrar_saldos_remanescentes(resultados_segunda)
    sugestoes = gerar_sugestao_remanejamento(
        resultados_segunda,
        saldos_remanescentes,
    )
    layout_final = gerar_layout_final(sugestoes)

    print(f"Quantidade de registros do Layout Final: {len(layout_final)}")
    print("Primeiros registros gerados:")

    for registro in layout_final[:10]:
        print(
            f"Destino: {registro.destino} | "
            f"Origem: {registro.origem} | "
            f"Produto: {registro.produto} | "
            f"Descricao: {registro.descricao} | "
            f"Quantidade Enviar: {registro.quantidade_enviar}"
        )

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return len(layout_final)


def executar_sprint_6(
    caminho_estoque: Path,
    caminho_excesso: Path,
    dias_alvo: float = 90,
) -> int:
    estoque_importado = importar_estoque(caminho_estoque)
    excesso_importado = importar_excesso(caminho_excesso)

    estoque_limpo = limpar_estoque(estoque_importado.linhas)
    excesso_limpo = limpar_excesso(excesso_importado.linhas)

    validacao_estoque = validar_estoque(estoque_limpo)
    validacao_excesso = validar_excesso(excesso_limpo)
    validacao = consolidar_validacoes(validacao_estoque, validacao_excesso)

    if not validacao.valido:
        print("Validacoes: ERRO")
        for erro in validacao.erros:
            print(f"- {erro}")
        raise SystemExit(1)

    estoque_normalizado = normalizar_estoque(estoque_limpo)
    excesso_normalizado = normalizar_excesso(excesso_limpo)
    estoque_calculado = calcular_capacidade_estoque(estoque_normalizado, dias_alvo)
    preparacoes = preparar_dados_motor(estoque_calculado, excesso_normalizado)
    resultados_primeira = executar_primeira_rodada(preparacoes)
    resultados_segunda = executar_segunda_rodada(resultados_primeira)
    saldos_remanescentes = registrar_saldos_remanescentes(resultados_segunda)
    sugestoes = gerar_sugestao_remanejamento(
        resultados_segunda,
        saldos_remanescentes,
    )
    layout_final = gerar_layout_final(sugestoes)
    pasta_saida = Path(
        tempfile.mkdtemp(prefix="remanejamento_estoque_sprint6_")
    )
    arquivos = exportar_layout_final_txt(layout_final, pasta_saida)

    print(f"Pasta de exportacao: {pasta_saida}")
    print(f"Quantidade de arquivos TXT gerados: {len(arquivos)}")
    print("Arquivos gerados:")

    for arquivo in arquivos:
        print(f"{arquivo.caminho.name}: {arquivo.quantidade_linhas} linhas")

    if arquivos:
        primeiro_arquivo = arquivos[0]
        print(f"Conteudo completo do primeiro arquivo gerado:")
        print(primeiro_arquivo.caminho.name)

        for linha in primeiro_arquivo.linhas:
            print(linha)

    for aviso in validacao.avisos:
        print(f"Aviso: {aviso}")

    return len(arquivos)


def _formatar_valor_opcional(valor: float | None) -> str:
    if valor is None:
        return "nao aplicavel"

    return f"{valor:g}"


def main() -> None:
    raiz_projeto = Path(__file__).resolve().parent.parent
    caminho_estoque = raiz_projeto / "Layout" / "Layout_Estoque.xls"
    caminho_excesso = raiz_projeto / "Layout" / "Layout_Excesso.xls"

    executar_sprint_6(caminho_estoque, caminho_excesso)


if __name__ == "__main__":
    main()
