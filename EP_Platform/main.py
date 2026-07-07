from pathlib import Path

from EP_Platform.importadores.importador_estoque import importar_estoque
from EP_Platform.importadores.importador_excesso import importar_excesso
from EP_Platform.normalizadores.normalizador_dados import (
    limpar_estoque,
    limpar_excesso,
    normalizar_estoque,
    normalizar_excesso,
)
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


def main() -> None:
    raiz_projeto = Path(__file__).resolve().parent.parent
    caminho_estoque = raiz_projeto / "Layout" / "Layout_Estoque.xls"
    caminho_excesso = raiz_projeto / "Layout" / "Layout_Excesso.xls"

    executar_sprint_1(caminho_estoque, caminho_excesso)


if __name__ == "__main__":
    main()
