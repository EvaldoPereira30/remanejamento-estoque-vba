# Release Notes

## v2.0 - Migracao para EP Platform concluida

### Objetivo

Esta release registra a conclusao da migracao do Remanejamento de Estoque da versao Excel VBA para a arquitetura inicial da EP Platform.

O objetivo da migracao foi preservar o comportamento funcional existente em producao, organizar as regras de negocio em modulos separados e preparar a solucao para evolucoes futuras sem depender da estrutura de abas, celulas e macros do Excel.

### Principais funcionalidades implementadas

- Importacao dos layouts de Estoque e Excesso.
- Validacao dos arquivos importados.
- Limpeza de cabecalhos e rodapes.
- Propagacao de filial conforme comportamento atual do VBA.
- Normalizacao dos dados para estruturas padronizadas.
- Calculo de dias de estoque, estoque maximo, capacidade e status de absorcao.
- Preparacao dos dados para o motor de distribuicao.
- Primeira rodada de distribuicao.
- Segunda rodada de distribuicao.
- Tratamento de saldo restante com registro `Sem loja destino`.
- Testes automatizados de regressao do motor.
- Geracao da `Sugestao_Remanejamento`.
- Geracao do Layout Final operacional.
- Exportacao TXT por filial destino.

### Arquitetura

A solucao foi organizada em modulos com responsabilidades separadas:

- Importadores: leitura dos arquivos de Estoque e Excesso.
- Validadores: verificacao dos layouts e das condicoes minimas obrigatorias.
- Normalizadores: limpeza, propagacao de filial e conversao para estruturas padronizadas.
- Calculadoras: calculo de capacidade e classificacao de absorcao.
- Preparadores: organizacao dos dados para execucao do motor.
- Motores: execucao da primeira rodada, segunda rodada e tratamento de saldo restante.
- Geradores: criacao da `Sugestao_Remanejamento` e do Layout Final.
- Exportadores: geracao dos arquivos TXT operacionais.
- Testes: suite automatizada para proteger o comportamento do motor de distribuicao.

### Garantia de qualidade

A suite de regressao permanece aprovada.

As regras de negocio documentadas foram preservadas na implementacao da migracao.

O comportamento funcional foi validado com os layouts reais do projeto:

- `Layout/Layout_Estoque.xls`
- `Layout/Layout_Excesso.xls`

As validacoes confirmaram a compatibilidade do motor, da sugestao, do layout final e da exportacao TXT com o comportamento esperado.

### Resultado

A migracao do Remanejamento de Estoque do VBA para a nova arquitetura da EP Platform foi finalizada com sucesso.

A versao v2.0 passa a representar a base funcional migrada, com importacao, validacao, calculo, distribuicao, geracao da sugestao, layout final e exportacao TXT implementados e validados.

### Proximos passos

Futuras versoes passam a representar evolucao do produto, nao mais migracao.

Melhorias futuras devem ser tratadas como evolucoes controladas, com validacao de impacto, homologacao e preservacao da compatibilidade quando aplicavel.
