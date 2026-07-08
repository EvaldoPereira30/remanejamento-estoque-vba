from dataclasses import dataclass, field
from pathlib import Path


LinhaTabela = list[str]


@dataclass(frozen=True)
class ResultadoImportacao:
    origem: Path
    tipo: str
    linhas: list[LinhaTabela]
    avisos: list[str] = field(default_factory=list)

    @property
    def total_linhas(self) -> int:
        return len(self.linhas)


@dataclass(frozen=True)
class ResultadoValidacao:
    valido: bool
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    @classmethod
    def ok(cls, avisos: list[str] | None = None) -> "ResultadoValidacao":
        return cls(valido=True, avisos=avisos or [])

    @classmethod
    def falha(
        cls,
        erros: list[str],
        avisos: list[str] | None = None,
    ) -> "ResultadoValidacao":
        return cls(valido=False, erros=erros, avisos=avisos or [])


@dataclass(frozen=True)
class RegistroEstoque:
    cod_filial: str
    cod_produto: str
    ean: str
    descricao: str
    fabricante: str
    linha: str
    status_produto: str
    media_f: float
    qt_estoque_comercial: float
    linha_origem: int


@dataclass(frozen=True)
class RegistroEstoqueCalculado:
    estoque: RegistroEstoque
    dias_estoque_atual: float
    estoque_maximo: float
    capacidade: float
    status_absorcao: str


@dataclass(frozen=True)
class RegistroExcesso:
    origem: str
    produto: str
    descricao: str
    qtde_excesso: float
    linha_origem: int


@dataclass(frozen=True)
class DestinoApto:
    registro: RegistroEstoqueCalculado

    @property
    def filial(self) -> str:
        return self.registro.estoque.cod_filial

    @property
    def media_f(self) -> float:
        return self.registro.estoque.media_f

    @property
    def capacidade(self) -> float:
        return self.registro.capacidade


@dataclass(frozen=True)
class PreparacaoMotorProduto:
    excesso: RegistroExcesso
    registro_origem: RegistroEstoqueCalculado | None
    registros_produto: list[RegistroEstoqueCalculado]
    destinos_aptos: list[DestinoApto]

    @property
    def capacidade_total_disponivel(self) -> float:
        return sum(destino.capacidade for destino in self.destinos_aptos)
