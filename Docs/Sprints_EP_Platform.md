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

## Sprint 2B - Preparacao de Dados para o Motor

### Objetivo

Preparar a estrutura de dados que sera usada pelo Motor de Distribuicao na Sprint 3.

A Sprint 2B organiza os dados importados, normalizados e calculados, deixando disponiveis as informacoes necessarias para o algoritmo futuro. Esta sprint nao executa distribuicao, nao gera sugestao, nao gera remanejamento final e nao exporta TXT.

### Escopo

O escopo da Sprint 2B contempla:

- agrupar registros de estoque por produto;
- identificar a filial de origem informada no arquivo de excesso;
- localizar o registro correspondente da origem no estoque;
- localizar todas as filiais que possuem o mesmo produto;
- excluir a filial de origem da lista de destinos;
- selecionar apenas filiais com `StatusAbsorcao = Pode Absorver`;
- manter disponivel a capacidade calculada de cada destino;
- ordenar os destinos por produto crescente e `MediaF` decrescente;
- apresentar no terminal um resumo por produto/excesso.

### Arquivos criados ou alterados

- `EP_Platform/preparadores/__init__.py`
- `EP_Platform/preparadores/preparador_motor.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Regras implementadas

Para cada linha de excesso normalizada, o preparador:

1. usa o codigo do produto para buscar os registros de estoque do mesmo produto;
2. identifica a filial de origem informada no excesso;
3. procura, dentro do estoque calculado, o registro da origem para o produto;
4. monta a lista de possiveis destinos com o mesmo produto;
5. remove a filial de origem da lista de destinos;
6. mantem apenas destinos com status `Pode Absorver`;
7. preserva a capacidade ja calculada na Sprint 2A;
8. ordena os destinos seguindo a regra atual do VBA: produto crescente e maior `MediaF` primeiro.

### Resultado esperado em terminal

A execucao de `EP_Platform/main.py` deve apresentar, para cada produto informado no excesso:

- produto;
- loja de origem;
- quantidade em excesso;
- quantidade de destinos aptos encontrados;
- capacidade total disponivel.

### Limitacoes

- Nao calcula quantidade a enviar.
- Nao reduz saldo de excesso.
- Nao altera estoque de origem.
- Nao altera estoque de destino.
- Nao executa rodadas de distribuicao.
- Nao gera `Sugestao_Remanejamento`.
- Nao gera `Final - Importar`.
- Nao exporta TXT.

### Proximos passos

- Implementar o Motor de Distribuicao na Sprint 3.
- Usar a estrutura preparada nesta sprint para aplicar as rodadas do algoritmo.
- Preservar na Sprint 3 a regra de nao atualizar estoque de destino durante a distribuicao inicial compativel com o VBA.

## Sprint 3A - Primeira Rodada do Motor de Distribuicao

### Objetivo

Implementar somente a primeira rodada do algoritmo de distribuicao, usando os dados preparados pela Sprint 2B.

A Sprint 3A registra distribuicoes em memoria para destinos aptos com estoque atual zerado. Esta sprint nao implementa segunda rodada, nao gera `Sugestao_Remanejamento` completa, nao gera remanejamento final e nao exporta TXT.

### Escopo

O escopo da Sprint 3A contempla:

- criar o modulo inicial do motor de distribuicao;
- receber a estrutura preparada pela Sprint 2B;
- calcular o saldo inicial do produto a partir do excesso e do estoque disponivel na origem;
- percorrer apenas destinos aptos;
- selecionar somente destinos cujo estoque atual seja igual a zero;
- enviar no maximo 1 unidade por destino;
- limitar o envio pelo saldo restante;
- limitar o envio pela capacidade disponivel;
- reduzir o saldo restante em memoria apos cada envio;
- registrar cada envio em memoria;
- apresentar no terminal o resumo dos envios da primeira rodada.

### Arquivos criados ou alterados

- `EP_Platform/motores/__init__.py`
- `EP_Platform/motores/motor_primeira_rodada.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Regras implementadas

Para cada produto preparado:

1. calcula o saldo inicial:

```text
saldoInicial = min(qtdExcesso, estoqueOrigem)
```

2. se a origem nao for encontrada no estoque ou nao possuir estoque disponivel, o saldo inicial e zero;
3. percorre os destinos aptos ja preparados;
4. considera somente destinos com `QtEstoqueComercial = 0`;
5. calcula a quantidade a enviar:

```text
quantidadeEnviar = min(saldoRestante, capacidade, 1)
```

6. se a quantidade calculada for maior que zero, registra o envio em memoria;
7. reduz o saldo restante;
8. interrompe a rodada quando o saldo restante chega a zero.

### Resultado esperado em terminal

A execucao de `EP_Platform/main.py` deve apresentar, para cada produto:

- produto;
- saldo inicial;
- destino atendido na primeira rodada;
- quantidade enviada;
- saldo restante apos o envio.

Quando nao houver envio para um produto na primeira rodada, a execucao informa que nenhum envio foi realizado.

### Limitacoes

- Nao executa segunda rodada.
- Nao atende destinos com estoque atual maior que zero.
- Nao altera estoque de origem.
- Nao altera estoque de destino.
- Nao recalcula capacidade.
- Nao gera `Sugestao_Remanejamento` completa.
- Nao gera `Final - Importar`.
- Nao exporta TXT.

### Proximos passos

- Implementar a segunda rodada do motor de distribuicao.
- Integrar as duas rodadas em uma estrutura unica de resultado.
- Gerar a sugestao detalhada somente apos o motor completo estar validado.
