import unittest
from dataclasses import dataclass
from math import isclose
from pathlib import Path

from EP_Platform.calculadoras.calculadora_capacidade import (
    STATUS_NAO_ABSORVE,
    STATUS_PODE_ABSORVER,
    STATUS_SEM_MEDIA,
    calcular_capacidade_estoque,
)
from EP_Platform.importadores.importador_estoque import importar_estoque
from EP_Platform.importadores.importador_excesso import importar_excesso
from EP_Platform.motores.motor_primeira_rodada import executar_primeira_rodada
from EP_Platform.motores.motor_segunda_rodada import executar_segunda_rodada
from EP_Platform.motores.tratador_saldo_restante import (
    DESTINO_SEM_LOJA,
    registrar_saldos_remanescentes,
)
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


DIAS_ALVO = 90
TOLERANCIA = 1e-9


@dataclass(frozen=True)
class ResultadoEsperado:
    saldo_inicial: float
    envios_primeira: list[tuple[str, float, float]]
    saldo_apos_primeira: float
    envios_segunda: list[tuple[str, float, float]]
    saldo_final: float


class MotorDistribuicaoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        raiz = Path(__file__).resolve().parents[2]
        estoque_path = raiz / "Layout" / "Layout_Estoque.xls"
        excesso_path = raiz / "Layout" / "Layout_Excesso.xls"

        estoque_importado = importar_estoque(estoque_path)
        excesso_importado = importar_excesso(excesso_path)

        cls.estoque_limpo = limpar_estoque(estoque_importado.linhas)
        cls.excesso_limpo = limpar_excesso(excesso_importado.linhas)

        cls.validacao = consolidar_validacoes(
            validar_estoque(cls.estoque_limpo),
            validar_excesso(cls.excesso_limpo),
        )

        cls.estoque = normalizar_estoque(cls.estoque_limpo)
        cls.excessos = normalizar_excesso(cls.excesso_limpo)
        cls.estoque_calculado = calcular_capacidade_estoque(cls.estoque, DIAS_ALVO)
        cls.preparacoes = preparar_dados_motor(cls.estoque_calculado, cls.excessos)
        cls.resultados_primeira = executar_primeira_rodada(cls.preparacoes)
        cls.resultados_segunda = executar_segunda_rodada(cls.resultados_primeira)
        cls.saldos_remanescentes = registrar_saldos_remanescentes(
            cls.resultados_segunda
        )
        cls.esperados = {
            prep.excesso.produto: calcular_resultado_esperado(prep)
            for prep in cls.preparacoes
        }
        cls.divergencias: list[str] = []

    @classmethod
    def tearDownClass(cls) -> None:
        produtos_analisados = len(cls.preparacoes)
        reprovados = len({divergencia.split("|", 1)[0] for divergencia in cls.divergencias})
        aprovados = produtos_analisados - reprovados
        totalmente_distribuidos = sum(
            1 for resultado in cls.resultados_segunda if resultado.saldo_restante <= 0
        )
        com_saldo = len(cls.saldos_remanescentes)

        print()
        print("Motor de Distribuição")
        print(f"Produtos analisados: {produtos_analisados}")
        print(f"Aprovados: {aprovados}")
        print(f"Reprovados: {reprovados}")
        print(f"Divergências: {len(cls.divergencias)}")
        print(f"Produtos totalmente distribuídos: {totalmente_distribuidos}")
        print(f"Produtos com saldo restante: {com_saldo}")

        if cls.divergencias:
            print("Divergências encontradas:")
            for divergencia in cls.divergencias:
                produto, regra, esperado, obtido = divergencia.split("|", 3)
                print(f"- Produto {produto}; regra: {regra}; esperado: {esperado}; obtido: {obtido}")
        else:
            print(
                "A implementação do Motor de Distribuição permanece compatível "
                "com as regras de negócio documentadas."
            )

    def test_importacao_dos_layouts(self) -> None:
        self.assertTrue(self.validacao.valido, self.validacao.erros)
        self.assertEqual(len(self.estoque), 1892)
        self.assertEqual(len(self.excessos), 22)

    def test_calculo_de_capacidade(self) -> None:
        self.assertEqual(len(self.estoque_calculado), len(self.estoque))

        for registro in self.estoque_calculado:
            estoque = registro.estoque

            if estoque.media_f <= 0:
                self.assert_regra(
                    estoque.cod_produto,
                    registro.status_absorcao == STATUS_SEM_MEDIA,
                    "MediaF <= 0 gera Sem Media",
                    STATUS_SEM_MEDIA,
                    registro.status_absorcao,
                )
                continue

            dias = estoque.qt_estoque_comercial / (estoque.media_f / 30)
            estoque_maximo = (estoque.media_f / 30) * DIAS_ALVO
            capacidade = max(0.0, estoque_maximo - estoque.qt_estoque_comercial)

            self.assert_regra(
                estoque.cod_produto,
                mesmo_numero(registro.dias_estoque_atual, dias),
                "DiasEstoqueAtual calculado",
                f"{dias:.8f}",
                f"{registro.dias_estoque_atual:.8f}",
            )
            self.assert_regra(
                estoque.cod_produto,
                mesmo_numero(registro.estoque_maximo, estoque_maximo),
                "EstoqueMaximo calculado",
                f"{estoque_maximo:.8f}",
                f"{registro.estoque_maximo:.8f}",
            )
            self.assert_regra(
                estoque.cod_produto,
                mesmo_numero(registro.capacidade, capacidade),
                "Capacidade calculada",
                f"{capacidade:.8f}",
                f"{registro.capacidade:.8f}",
            )

            status_esperado = (
                STATUS_NAO_ABSORVE if dias >= DIAS_ALVO else STATUS_PODE_ABSORVER
            )
            self.assert_regra(
                estoque.cod_produto,
                registro.status_absorcao == status_esperado,
                "StatusAbsorcao calculado",
                status_esperado,
                registro.status_absorcao,
            )

    def test_preparacao_do_motor(self) -> None:
        self.assertEqual(len(self.preparacoes), len(self.excessos))

        for preparacao in self.preparacoes:
            produto = preparacao.excesso.produto
            self.assert_regra(
                produto,
                preparacao.registro_origem is not None,
                "Origem localizada no estoque",
                "registro origem",
                "ausente",
            )
            self.assertEqual(preparacao.excesso.origem, "63")

            medias = [destino.media_f for destino in preparacao.destinos_aptos]
            self.assertEqual(medias, sorted(medias, reverse=True))

            for destino in preparacao.destinos_aptos:
                self.assert_regra(
                    produto,
                    destino.filial != preparacao.excesso.origem,
                    "Destino diferente da origem",
                    "destino != origem",
                    destino.filial,
                )
                self.assert_regra(
                    produto,
                    destino.registro.status_absorcao == STATUS_PODE_ABSORVER,
                    "Destino apto",
                    STATUS_PODE_ABSORVER,
                    destino.registro.status_absorcao,
                )
                self.assert_regra(
                    produto,
                    destino.capacidade > 0,
                    "Capacidade positiva",
                    "> 0",
                    f"{destino.capacidade:.8f}",
                )

    def test_primeira_rodada(self) -> None:
        for resultado in self.resultados_primeira:
            produto = resultado.preparacao.excesso.produto
            esperado = self.esperados[produto]

            self.assert_regra(
                produto,
                mesmo_numero(resultado.saldo_inicial, esperado.saldo_inicial),
                "Saldo inicial correto",
                f"{esperado.saldo_inicial:.8f}",
                f"{resultado.saldo_inicial:.8f}",
            )
            self.assert_envios(
                produto,
                "Primeira rodada esperada",
                esperado.envios_primeira,
                [(e.destino, e.quantidade_enviada, e.saldo_restante) for e in resultado.envios],
            )

            for envio in resultado.envios:
                destino = destino_por_filial(resultado.preparacao, envio.destino)
                self.assert_regra(
                    produto,
                    mesmo_numero(destino.registro.estoque.qt_estoque_comercial, 0),
                    "Primeira rodada usa estoque zero",
                    "0",
                    f"{destino.registro.estoque.qt_estoque_comercial:.8f}",
                )
                self.assert_regra(
                    produto,
                    envio.quantidade_enviada <= 1 + TOLERANCIA,
                    "Primeira rodada maximo 1 unidade",
                    "<= 1",
                    f"{envio.quantidade_enviada:.8f}",
                )
                self.assert_regra(
                    produto,
                    envio.quantidade_enviada <= destino.capacidade + TOLERANCIA,
                    "Primeira rodada respeita capacidade",
                    f"<= {destino.capacidade:.8f}",
                    f"{envio.quantidade_enviada:.8f}",
                )

    def test_segunda_rodada(self) -> None:
        for resultado in self.resultados_segunda:
            produto = resultado.resultado_primeira_rodada.preparacao.excesso.produto
            esperado = self.esperados[produto]

            self.assert_regra(
                produto,
                mesmo_numero(
                    resultado.saldo_apos_primeira_rodada,
                    esperado.saldo_apos_primeira,
                ),
                "Saldo apos primeira rodada correto",
                f"{esperado.saldo_apos_primeira:.8f}",
                f"{resultado.saldo_apos_primeira_rodada:.8f}",
            )
            self.assert_envios(
                produto,
                "Segunda rodada esperada",
                esperado.envios_segunda,
                [(e.destino, e.quantidade_enviada, e.saldo_restante) for e in resultado.envios],
            )
            self.assert_regra(
                produto,
                mesmo_numero(resultado.saldo_restante, esperado.saldo_final),
                "Saldo final correto",
                f"{esperado.saldo_final:.8f}",
                f"{resultado.saldo_restante:.8f}",
            )

            for envio in resultado.envios:
                destino = destino_por_filial(
                    resultado.resultado_primeira_rodada.preparacao,
                    envio.destino,
                )
                self.assert_regra(
                    produto,
                    destino.registro.estoque.qt_estoque_comercial > 0,
                    "Segunda rodada usa estoque maior que zero",
                    "> 0",
                    f"{destino.registro.estoque.qt_estoque_comercial:.8f}",
                )
                self.assert_regra(
                    produto,
                    envio.quantidade_enviada <= destino.capacidade + TOLERANCIA,
                    "Segunda rodada respeita capacidade",
                    f"<= {destino.capacidade:.8f}",
                    f"{envio.quantidade_enviada:.8f}",
                )

    def test_tratamento_de_saldo_restante(self) -> None:
        saldos_por_produto = {saldo.produto: saldo for saldo in self.saldos_remanescentes}

        for resultado in self.resultados_segunda:
            produto = resultado.resultado_primeira_rodada.preparacao.excesso.produto

            if resultado.saldo_restante > 0:
                self.assertIn(produto, saldos_por_produto)
                saldo = saldos_por_produto[produto]
                self.assert_regra(
                    produto,
                    saldo.destino == DESTINO_SEM_LOJA,
                    "Registro Sem loja destino",
                    DESTINO_SEM_LOJA,
                    saldo.destino,
                )
                self.assert_regra(
                    produto,
                    mesmo_numero(saldo.saldo_restante, resultado.saldo_restante),
                    "Saldo remanescente registrado",
                    f"{resultado.saldo_restante:.8f}",
                    f"{saldo.saldo_restante:.8f}",
                )
                self.assertEqual(saldo.quantidade_sugerida, 0.0)
                self.assertIsNone(saldo.dias_destino)
                self.assertIsNone(saldo.capacidade)
                self.assertIsNone(saldo.dias_apos)
            else:
                self.assertNotIn(produto, saldos_por_produto)

    def assert_envios(
        self,
        produto: str,
        regra: str,
        esperado: list[tuple[str, float, float]],
        obtido: list[tuple[str, float, float]],
    ) -> None:
        condicao = len(esperado) == len(obtido)
        if condicao:
            for esperado_item, obtido_item in zip(esperado, obtido):
                condicao = (
                    esperado_item[0] == obtido_item[0]
                    and mesmo_numero(esperado_item[1], obtido_item[1])
                    and mesmo_numero(esperado_item[2], obtido_item[2])
                )
                if not condicao:
                    break

        self.assert_regra(produto, condicao, regra, repr(esperado), repr(obtido))

    def assert_regra(
        self,
        produto: str,
        condicao: bool,
        regra: str,
        esperado: str,
        obtido: str,
    ) -> None:
        if not condicao:
            self.divergencias.append(f"{produto}|{regra}|{esperado}|{obtido}")
        self.assertTrue(condicao)


def calcular_resultado_esperado(preparacao) -> ResultadoEsperado:
    registro_origem = preparacao.registro_origem

    if registro_origem is None or registro_origem.estoque.qt_estoque_comercial <= 0:
        saldo = 0.0
    else:
        saldo = min(
            preparacao.excesso.qtde_excesso,
            registro_origem.estoque.qt_estoque_comercial,
        )

    saldo_inicial = saldo
    envios_primeira: list[tuple[str, float, float]] = []

    for destino in preparacao.destinos_aptos:
        if saldo <= 0:
            break
        if not mesmo_numero(destino.registro.estoque.qt_estoque_comercial, 0):
            continue

        quantidade = min(saldo, destino.capacidade, 1.0)
        if quantidade <= 0:
            continue

        saldo -= quantidade
        envios_primeira.append((destino.filial, quantidade, saldo))

    saldo_apos_primeira = saldo
    envios_segunda: list[tuple[str, float, float]] = []

    for destino in preparacao.destinos_aptos:
        if saldo <= 0:
            break
        if destino.registro.estoque.qt_estoque_comercial <= 0:
            continue

        quantidade = min(saldo, destino.capacidade)
        if quantidade <= 0:
            continue

        saldo -= quantidade
        envios_segunda.append((destino.filial, quantidade, saldo))

    return ResultadoEsperado(
        saldo_inicial=saldo_inicial,
        envios_primeira=envios_primeira,
        saldo_apos_primeira=saldo_apos_primeira,
        envios_segunda=envios_segunda,
        saldo_final=saldo,
    )


def mesmo_numero(valor_a: float, valor_b: float) -> bool:
    return isclose(valor_a, valor_b, rel_tol=TOLERANCIA, abs_tol=TOLERANCIA)


def destino_por_filial(preparacao, filial: str):
    for destino in preparacao.destinos_aptos:
        if destino.filial == filial:
            return destino
    raise AssertionError(f"Destino {filial} nao encontrado para {preparacao.excesso.produto}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
