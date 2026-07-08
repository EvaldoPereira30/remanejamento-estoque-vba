from dataclasses import dataclass
from pathlib import Path

from EP_Platform.modelos.schemas import RegistroLayoutFinal


@dataclass(frozen=True)
class ArquivoTXTExportado:
    destino: str
    caminho: Path
    quantidade_linhas: int
    linhas: list[str]


def exportar_layout_final_txt(
    layout_final: list[RegistroLayoutFinal],
    pasta_destino: Path,
) -> list[ArquivoTXTExportado]:
    pasta_destino.mkdir(parents=True, exist_ok=True)
    registros_por_destino = _agrupar_por_destino(layout_final)
    arquivos: list[ArquivoTXTExportado] = []

    for destino, registros in registros_por_destino.items():
        linhas = [_formatar_linha(registro) for registro in registros]
        caminho = pasta_destino / f"Remanejar Filial {destino}.txt"
        conteudo = "\r\n".join(linhas)

        if conteudo:
            conteudo += "\r\n"

        caminho.write_text(conteudo, encoding="utf-8", newline="")
        arquivos.append(
            ArquivoTXTExportado(
                destino=destino,
                caminho=caminho,
                quantidade_linhas=len(linhas),
                linhas=linhas,
            )
        )

    return arquivos


def _agrupar_por_destino(
    layout_final: list[RegistroLayoutFinal],
) -> dict[str, list[RegistroLayoutFinal]]:
    registros_por_destino: dict[str, list[RegistroLayoutFinal]] = {}

    for registro in layout_final:
        if registro.destino not in registros_por_destino:
            registros_por_destino[registro.destino] = []

        registros_por_destino[registro.destino].append(registro)

    return registros_por_destino


def _formatar_linha(registro: RegistroLayoutFinal) -> str:
    return (
        f"{registro.origem};"
        f"{registro.produto};"
        f"{registro.quantidade_enviar}"
    )
