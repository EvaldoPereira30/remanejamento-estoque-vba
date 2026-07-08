# Sprints EP Platform

## Sprint 1 - Importacao e Validacao

### Objetivo

Implementar a base inicial da migracao do Remanejamento de Estoque para a EP Platform, focando somente em importacao, limpeza, normalizacao e validacao dos arquivos de entrada.

A Sprint 1 nao implementa motor de distribuicao, nao gera sugestao de remanejamento, nao gera remanejamento final e nao exporta TXT.

### Escopo

O escopo da Sprint 1 contempla:

- importar o arquivo de estoque;
- importar o arquivo de excesso;
- limpar cabecalhos tecnicos e rodapes;
- propagar filial em branco conforme o comportamento atual do VBA;
- validar a existencia minima de dados;
- validar o layout do excesso conforme a regra atual;
- normalizar os dados para estruturas padronizadas;
- executar um fluxo simples em terminal usando os arquivos da pasta `Layout`.

### Arquivos criados

- `EP_Platform/__init__.py`
- `EP_Platform/importadores/__init__.py`
- `EP_Platform/importadores/importador_estoque.py`
- `EP_Platform/importadores/importador_excesso.py`
- `EP_Platform/validadores/__init__.py`
- `EP_Platform/validadores/validador_layout.py`
- `EP_Platform/normalizadores/__init__.py`
- `EP_Platform/normalizadores/normalizador_dados.py`
- `EP_Platform/modelos/__init__.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Regras implementadas

Importacao de estoque:

- leitura do arquivo `Layout/Layout_Estoque.xls`;
- suporte ao formato SpreadsheetML usado pelo layout atual;
- leitura da primeira planilha;
- remocao das duas primeiras linhas do relatorio original;
- remocao de rodapes contendo `H:`, `Usuario:` ou `Usuário:` na coluna A;
- propagacao do codigo da filial para linhas em que a coluna A esta vazia;
- validacao minima de existencia de dados;
- normalizacao das colunas:
  - `CodFilial`;
  - `CodProduto`;
  - `EAN`;
  - `Descricao`;
  - `Fabricante`;
  - `Linha`;
  - `StatusProduto`;
  - `MediaF`;
  - `QtEstoqueComercial`.

Importacao de excesso:

- leitura do arquivo `Layout/Layout_Excesso.xls`;
- suporte ao formato tabulado usado pelo layout atual;
- remocao de linhas anteriores ao cabecalho quando existir `CodFilial` na coluna A;
- remocao de rodapes contendo `H:`, `Usuario:` ou `Usuário:` na coluna A;
- propagacao do codigo da filial para linhas em que a coluna A esta vazia;
- validacao da linha 2:
  - coluna A numerica e nao vazia;
  - coluna B numerica e nao vazia;
  - coluna C texto nao vazio;
  - coluna D numerica e nao vazia;
  - coluna E vazia;
- normalizacao das colunas:
  - `Origem`;
  - `Produto`;
  - `Descricao`;
  - `QtdeExcesso`.

Execucao:

- `EP_Platform/main.py` executa a Sprint 1 usando:
  - `Layout/Layout_Estoque.xls`;
  - `Layout/Layout_Excesso.xls`.
- A saida esperada em terminal informa:
  - total de linhas de estoque normalizadas;
  - total de linhas de excesso normalizadas;
  - status das validacoes.

### Limitacoes

- Nao calcula capacidade.
- Nao identifica lojas aptas.
- Nao executa motor de distribuicao.
- Nao gera `Sugestao_Remanejamento`.
- Nao gera `Final - Importar`.
- Nao exporta arquivos TXT.
- A validacao do estoque permanece minima para manter compatibilidade com o comportamento atual do VBA.
- A validacao completa de duplicidades, produtos ausentes, quantidades negativas e consistencia cadastral fica fora desta sprint.

### Proximos passos

- Implementar a calculadora de capacidade.
- Calcular dias de estoque, estoque maximo, capacidade e status de absorcao.
- Criar testes automatizados comparando a massa de layout com o comportamento esperado.
- Preparar a base para o motor de distribuicao em sprint futura.
- Manter a regra de nao atualizar estoque de destino durante a distribuicao na primeira versao compativel.

## Sprint 2A - Calculos de Capacidade

### Objetivo

Implementar os calculos que preparam o estoque normalizado para o futuro motor de distribuicao.

A Sprint 2A calcula, para cada registro de estoque:

- `DiasEstoqueAtual`;
- `EstoqueMaximo`;
- `Capacidade`;
- `StatusAbsorcao`.

Esta sprint nao implementa motor de distribuicao, sugestao de remanejamento, remanejamento final ou exportacao TXT.

### Escopo

O escopo da Sprint 2A contempla:

- criar um modulo de calculo de capacidade;
- enriquecer cada registro de estoque com os quatro indicadores calculados;
- aplicar a regra de status de absorcao documentada;
- exibir em terminal um resumo por status;
- executar a validacao usando `Layout/Layout_Estoque.xls`.

### Arquivos criados ou alterados

- `EP_Platform/calculadoras/__init__.py`
- `EP_Platform/calculadoras/calculadora_capacidade.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Regras implementadas

Para cada registro de estoque:

```text
DiasEstoqueAtual = QtEstoqueComercial / (MediaF / 30)
EstoqueMaximo = (MediaF / 30) * DiasAlvo
Capacidade = max(0, EstoqueMaximo - QtEstoqueComercial)
```

Quando `MediaF <= 0`:

- `DiasEstoqueAtual = 0`;
- `EstoqueMaximo = 0`;
- `Capacidade = 0`;
- `StatusAbsorcao = Sem Media`.

Quando `MediaF > 0` e `DiasEstoqueAtual >= DiasAlvo`:

- `StatusAbsorcao = Nao Absorve`.

Quando `MediaF > 0` e `DiasEstoqueAtual < DiasAlvo`:

- `StatusAbsorcao = Pode Absorver`.

O valor padrao de `DiasAlvo` permanece 90, conforme o comportamento documentado.

### Resultado esperado em terminal

A execucao de `EP_Platform/main.py` deve apresentar:

- total de registros calculados;
- quantidade com status `Pode Absorver`;
- quantidade com status `Nao Absorve`;
- quantidade com status `Sem Media`.

### Limitacoes

- Nao executa distribuicao de excesso.
- Nao gera sugestao de remanejamento.
- Nao gera remanejamento final.
- Nao exporta TXT.
- Nao atualiza estoque de destino.
- Nao altera a regra de importacao e normalizacao da Sprint 1.

### Proximos passos

- Criar testes automatizados para a calculadora de capacidade.
- Preparar o motor de distribuicao em sprint futura usando os registros de estoque calculados.
- Preservar, na primeira versao do motor, a regra de nao atualizar estoque do destino durante a distribuicao.
