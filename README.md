# Remanejamento de Estoque

## Visão Geral

O **Remanejamento de Estoque** é uma ferramenta em Microsoft Excel com automação VBA para apoiar a redistribuição de estoque entre filiais.

A solução auxilia na análise de produtos com excesso em determinadas lojas e necessidade em outras, gerando sugestões de remanejamento e arquivos TXT para execução operacional.

## Problema

O processo manual de redistribuição de estoque entre filiais pode ser demorado, repetitivo e sujeito a erros de análise, digitação e priorização.

Sem automação, a identificação de lojas com excesso, lojas aptas a receber produtos e geração dos arquivos finais exige conferências manuais em planilhas, aumentando o tempo operacional e o risco de inconsistências.

## Solução

A ferramenta automatiza a análise de excesso e necessidade entre filiais, calculando informações operacionais e sugerindo remanejamentos de forma estruturada.

O fluxo foi desenvolvido em VBA para ser executado diretamente no Excel, mantendo um painel operacional para importação das bases, geração das sugestões, revisão dos resultados e exportação dos arquivos TXT por filial.

## Funcionalidades

- Importação da base de estoque.
- Importação da base de excesso.
- Cálculo automático da capacidade das filiais.
- Identificação de lojas aptas para absorção.
- Geração automática das sugestões de remanejamento.
- Exportação dos arquivos TXT por filial.
- Painel operacional em Excel.

## Fluxo de utilização

1. Importar Estoque.
2. Importar Excesso.
3. Gerar Sugestões.
4. Revisar resultados.
5. Exportar arquivos TXT.

## Estrutura do Projeto

```text
Remanejamento_Estoque/
├── VBA/
│   ├── Módulo1.bas
│   └── Módulo2.bas
├── Docs/
│   └── Regras_de_Negocio.md
├── Imagens/
│   └── README.md
├── Layout/
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

| Pasta/arquivo | Finalidade |
|---|---|
| `VBA/` | Contém os módulos VBA exportados do Excel. |
| `Docs/` | Documentação funcional e regras de negócio. |
| `Imagens/` | Local reservado para capturas de tela da ferramenta. |
| `Layout/` | Pasta reservada para arquivos de layout, exemplos ou referências operacionais do projeto. |
| `README.md` | Documento principal para apresentação no GitHub. |
| `CHANGELOG.md` | Histórico de versões publicadas. |
| `LICENSE` | Licença do projeto. |
| `.gitignore` | Arquivos que não devem ser versionados. |

## Tecnologias

- Microsoft Excel.
- VBA (Visual Basic for Applications).

## Possíveis Evoluções

- Persistência em banco de dados.
- Dashboard com indicadores de remanejamento.
- Histórico de remanejamentos realizados.
- Controle de execução por usuário e data.
- Geração de relatórios consolidados.
- Migração futura para Python.

## Observações

Os módulos VBA foram mantidos como a fonte funcional da automação. Esta publicação não altera a lógica existente, os nomes dos procedimentos ou a estrutura do código.

Detalhes específicos de fórmulas, critérios de priorização e validações internas podem ser complementados futuramente na documentação técnica a partir de uma análise detalhada do VBA.