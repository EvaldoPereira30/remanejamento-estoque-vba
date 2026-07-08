import tempfile
import unittest
from pathlib import Path

from EP_Platform.api import executar_remanejamento


class ApiPublicaRemanejamentoTest(unittest.TestCase):
    def test_executar_remanejamento_fluxo_completo(self) -> None:
        raiz = Path(__file__).resolve().parents[2]
        caminho_estoque = raiz / "Layout" / "Layout_Estoque.xls"
        caminho_excesso = raiz / "Layout" / "Layout_Excesso.xls"

        with tempfile.TemporaryDirectory() as pasta_saida:
            resultado = executar_remanejamento(
                caminho_estoque,
                caminho_excesso,
                pasta_saida,
            )

            self.assertTrue(resultado["sucesso"], resultado["mensagem"])
            self.assertEqual(resultado["divergencias"], [])
            self.assertEqual(resultado["quantidade_estoque"], 1892)
            self.assertEqual(resultado["quantidade_excesso"], 22)
            self.assertEqual(resultado["quantidade_sugestao"], 35)
            self.assertEqual(resultado["quantidade_layout_final"], 30)
            self.assertEqual(resultado["quantidade_txt_gerados"], 23)
            self.assertEqual(resultado["produtos_com_saldo_sem_destino"], ["60840"])
            self.assertEqual(Path(resultado["pasta_saida"]), Path(pasta_saida))

            arquivos_txt = [Path(caminho) for caminho in resultado["arquivos_txt"]]
            self.assertEqual(len(arquivos_txt), 23)
            self.assertTrue(all(arquivo.exists() for arquivo in arquivos_txt))
            self.assertTrue(
                all(arquivo.parent == Path(pasta_saida) for arquivo in arquivos_txt)
            )
            self.assertNotIn(
                "Remanejar Filial Sem loja destino.txt",
                [arquivo.name for arquivo in arquivos_txt],
            )

            primeiro_arquivo = Path(pasta_saida) / "Remanejar Filial 1.txt"
            self.assertIn(primeiro_arquivo, arquivos_txt)
            self.assertEqual(
                primeiro_arquivo.read_text(encoding="utf-8").splitlines(),
                ["63;34650;1"],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
