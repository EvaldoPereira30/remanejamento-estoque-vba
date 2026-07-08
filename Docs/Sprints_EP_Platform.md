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

## Sprint 3B - Segunda Rodada do Motor de Distribuicao

### Objetivo

Implementar somente a segunda rodada do algoritmo de distribuicao, utilizando o saldo restante apos a primeira rodada.

A Sprint 3B continua registrando distribuicoes em memoria. Ela nao gera remanejamento final, nao exporta TXT, nao arredonda quantidades, nao atualiza estoque de destino e nao recalcula capacidade.

### Escopo

O escopo da Sprint 3B contempla:

- executar a segunda rodada apos a primeira rodada;
- usar o saldo restante gerado pela primeira rodada;
- considerar somente destinos aptos com estoque atual maior que zero;
- respeitar a ordenacao preparada anteriormente: produto crescente e `MediaF` decrescente;
- enviar para cada destino o menor valor entre saldo restante e capacidade disponivel;
- reduzir o saldo restante apos cada envio;
- registrar cada envio da segunda rodada em memoria;
- apresentar no terminal o resumo da segunda rodada.

### Arquivos criados ou alterados

- `EP_Platform/motores/motor_segunda_rodada.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Regras implementadas

Para cada produto processado pela primeira rodada:

1. usa o saldo restante apos a primeira rodada;
2. percorre os destinos aptos ja preparados;
3. considera somente destinos com `QtEstoqueComercial > 0`;
4. calcula a quantidade a enviar:

```text
quantidadeEnviar = min(saldoRestante, capacidade)
```

5. registra o envio em memoria quando a quantidade calculada for maior que zero;
6. reduz o saldo restante;
7. interrompe a rodada quando o saldo restante chega a zero.

### Resultado esperado em terminal

A execucao de `EP_Platform/main.py` deve apresentar, para cada produto:

- produto;
- saldo apos primeira rodada;
- destino atendido na segunda rodada;
- quantidade enviada na segunda rodada;
- saldo restante apos o envio.

Quando nao houver envio para um produto na segunda rodada, a execucao informa que nenhum envio foi realizado.

### Limitacoes

- Nao gera `Sugestao_Remanejamento`.
- Nao gera `Final - Importar`.
- Nao exporta TXT.
- Nao altera estoque de origem.
- Nao altera estoque de destino.
- Nao recalcula capacidade.
- Nao arredonda quantidade enviada no motor.

### Regra de decimais

O motor mantem valores decimais quando a capacidade disponivel do destino ou o saldo restante forem decimais.

O arredondamento sera realizado apenas em etapa futura de Remanejamento Final, conforme a regra documentada da migracao.

### Proximos passos

- Integrar os resultados das duas rodadas em uma estrutura unica para geracao da sugestao.
- Implementar a `Sugestao_Remanejamento` em sprint futura.
- Manter o arredondamento fora do motor de distribuicao.

## Sprint 3C - Registro de Saldo Remanescente

### Objetivo

Registrar corretamente os produtos cujo saldo nao pode ser totalmente distribuido apos a primeira e a segunda rodada do motor.

A Sprint 3C nao distribui nenhuma unidade adicional. Ela apenas registra o saldo remanescente como pendencia operacional para auditoria, rastreabilidade e futura geracao da `Sugestao_Remanejamento`.

### Escopo

O escopo da Sprint 3C contempla:

- receber os resultados finais da segunda rodada;
- identificar produtos com saldo restante maior que zero;
- registrar exatamente um item de pendencia por produto com saldo remanescente;
- marcar o destino como `Sem loja destino`;
- preservar o produto, origem, quantidade original em excesso e saldo restante;
- manter quantidade sugerida como zero;
- manter dias do destino, capacidade e dias apos como nao aplicaveis;
- apresentar no terminal um resumo dos produtos com saldo remanescente.

### Arquivos criados ou alterados

- `EP_Platform/motores/tratador_saldo_restante.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Regras implementadas

Apos finalizar a primeira e a segunda rodada:

1. para cada produto, verifica o saldo final do motor;
2. se o saldo restante for maior que zero, registra uma pendencia;
3. se o saldo restante for zero, nao registra pendencia;
4. o registro de pendencia possui:
   - destino: `Sem loja destino`;
   - produto;
   - origem;
   - quantidade em excesso original;
   - saldo restante;
   - quantidade sugerida: `0`;
   - dias do destino: nao aplicavel;
   - capacidade: nao aplicavel;
   - dias apos: nao aplicavel.

### Resultado esperado em terminal

A execucao de `EP_Platform/main.py` deve apresentar:

- quantidade de produtos totalmente distribuidos;
- quantidade de produtos com saldo remanescente;
- lista dos produtos registrados como `Sem loja destino`.

### Limitacoes

- Nao implementa Remanejamento Final.
- Nao exporta TXT.
- Nao arredonda quantidades.
- Nao altera distribuicoes da primeira rodada.
- Nao altera distribuicoes da segunda rodada.
- Nao altera estoque de origem.
- Nao altera estoque de destino.
- Nao recalcula capacidade.

### Regras para etapas futuras

Os registros `Sem loja destino` nao participam do Remanejamento Final.

Os registros `Sem loja destino` nao sao exportados no TXT.

Esses registros servem apenas para auditoria, rastreabilidade e futura composicao da `Sugestao_Remanejamento`.

## Sprint QA-1 - Suite de Validacao do Motor

### Objetivo

Criar uma suite de validacao para proteger o comportamento atual do Motor de Distribuicao.

A Sprint QA-1 nao implementa novas funcionalidades, nao altera regras de negocio e nao modifica o comportamento do motor. O objetivo e garantir que futuras alteracoes no codigo nao mudem o comportamento ja validado.

### Escopo

O escopo da Sprint QA-1 contempla:

- criar uma estrutura de testes em `EP_Platform/tests/`;
- utilizar os layouts reais do projeto;
- validar importacao dos layouts;
- validar calculo de capacidade;
- validar preparacao do motor;
- validar primeira rodada;
- validar segunda rodada;
- validar tratamento de saldo restante;
- validar registro `Sem loja destino`;
- apresentar um resumo da execucao dos testes.

### Arquivos criados ou alterados

- `EP_Platform/tests/__init__.py`
- `EP_Platform/tests/test_motor_distribuicao.py`
- `Docs/Sprints_EP_Platform.md`

### Validacoes implementadas

Importacao:

- confirma que os layouts reais sao lidos e validados;
- confirma a quantidade de registros normalizados de estoque e excesso.

Calculo de capacidade:

- valida `DiasEstoqueAtual`;
- valida `EstoqueMaximo`;
- valida `Capacidade`;
- valida `StatusAbsorcao`.

Preparacao do motor:

- confirma que a origem e localizada no estoque;
- confirma que destinos aptos nao incluem a origem;
- confirma que destinos aptos possuem status `Pode Absorver`;
- confirma que a capacidade dos destinos aptos permanece disponivel;
- confirma a ordenacao por maior `MediaF`.

Primeira rodada:

- considera somente lojas com estoque zero;
- limita a quantidade enviada a no maximo 1 unidade;
- respeita saldo restante;
- respeita capacidade disponivel.

Segunda rodada:

- considera somente lojas com estoque maior que zero;
- respeita prioridade por maior `MediaF`;
- envia o menor valor entre saldo restante e capacidade;
- atualiza saldo em memoria corretamente;
- preserva valores decimais.

Saldo restante:

- confirma que produtos totalmente distribuidos nao geram registro;
- confirma que produtos com saldo remanescente geram registro `Sem loja destino`;
- confirma que o saldo registrado e igual ao saldo final do motor;
- confirma que quantidade sugerida fica zero;
- confirma que dias do destino, capacidade e dias apos permanecem nao aplicaveis.

### Resultado esperado

A execucao da suite deve apresentar um resumo semelhante a:

```text
Motor de Distribuicao
Produtos analisados: 22
Aprovados: 22
Reprovados: 0
Divergencias: 0
Produtos totalmente distribuidos: 21
Produtos com saldo restante: 1
```

Se nao houver divergencias, a suite apresenta:

```text
A implementacao do Motor de Distribuicao permanece compativel com as regras de negocio documentadas.
```

### Limitacoes

- Nao altera o algoritmo.
- Nao cria novas regras de negocio.
- Nao gera remanejamento final.
- Nao exporta TXT.
- Usa os layouts reais do projeto como massa inicial de regressao.

## Sprint 4 - Geracao da Sugestao_Remanejamento

### Objetivo

Gerar a estrutura `Sugestao_Remanejamento` a partir dos resultados ja produzidos pelo Motor de Distribuicao.

A Sprint 4 nao implementa regra nova, nao recalcula capacidade, nao altera estoque, nao modifica o algoritmo e nao arredonda quantidades. Ela atua apenas como camada de transformacao da memoria de calculo do motor para uma estrutura equivalente a aba `Sugestao_Remanejamento` do VBA.

### Escopo

O escopo da Sprint 4 contempla:

- criar um gerador especifico para a `Sugestao_Remanejamento`;
- consumir os resultados da primeira rodada;
- consumir os resultados da segunda rodada;
- consumir os registros de saldo remanescente `Sem loja destino`;
- gerar uma lista padronizada de registros de sugestao;
- exibir resumo da quantidade de registros gerados;
- exibir os primeiros registros para conferencia.

### Arquivos criados ou alterados

- `EP_Platform/geradores/__init__.py`
- `EP_Platform/geradores/gerador_sugestao.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Estrutura gerada

Cada registro da `Sugestao_Remanejamento` contem:

- `Origem`
- `Produto`
- `Descricao`
- `Quantidade em excesso original`
- `Destino`
- `Dias atuais do destino`
- `Capacidade`
- `Quantidade sugerida`
- `Dias apos envio`
- `Saldo restante`

### Regras implementadas

- cada envio registrado pelo motor gera um registro na sugestao;
- envios da primeira rodada sao preservados sem alteracao;
- envios da segunda rodada sao preservados sem alteracao;
- quantidades decimais permanecem decimais;
- saldos remanescentes geram registros com destino `Sem loja destino`;
- registros `Sem loja destino` preservam quantidade sugerida igual a zero;
- campos nao aplicaveis em registros `Sem loja destino` permanecem sem valor;
- `Dias apos envio` e derivado apenas para compor a memoria de sugestao;
- o calculo de `Dias apos envio` nao atualiza estoque, capacidade ou saldo do motor;
- nenhum registro produzido pelo motor e filtrado ou removido.

### Limitacoes

- Nao gera Remanejamento Final.
- Nao exporta TXT.
- Nao arredonda quantidades.
- Nao altera o resultado produzido pelo motor.
- Nao atualiza estoque do destino.
- Nao recalcula capacidade.

### Proximos passos

- implementar a geracao do Remanejamento Final;
- aplicar as regras futuras de arredondamento apenas no Remanejamento Final;
- manter os registros `Sem loja destino` apenas como memoria de calculo e rastreabilidade;
- implementar exportacao TXT em sprint posterior.

## Sprint 5 - Geracao do Layout Final Operacional

### Objetivo

Gerar o Layout Final utilizado pela operacao a partir da `Sugestao_Remanejamento`.

A Sprint 5 nao implementa regra nova, nao altera o Motor de Distribuicao, nao modifica a `Sugestao_Remanejamento`, nao recalcula saldo e nao recalcula capacidade. Ela apenas transforma os dados ja produzidos pela sugestao no layout operacional equivalente ao `Remanejamento Final` do VBA.

### Escopo

O escopo da Sprint 5 contempla:

- criar um gerador especifico para o Layout Final;
- consumir os registros da `Sugestao_Remanejamento`;
- remover registros com destino `Sem loja destino`;
- remover registros cuja quantidade arredondada seja menor ou igual a zero;
- arredondar a quantidade sugerida somente nesta etapa final;
- gerar a estrutura operacional com os campos esperados;
- ordenar o resultado por destino e origem;
- exibir a quantidade de registros e os primeiros itens gerados.

### Arquivos criados ou alterados

- `EP_Platform/geradores/gerador_layout_final.py`
- `EP_Platform/modelos/schemas.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Estrutura gerada

Cada registro do Layout Final contem exatamente:

- `Destino`
- `Origem`
- `Produto`
- `Descricao`
- `Quantidade Enviar`

### Regras implementadas

- registros com destino `Sem loja destino` nao entram no Layout Final;
- a quantidade sugerida e arredondada conforme o comportamento do Excel/VBA;
- apenas registros com quantidade arredondada maior que zero entram no Layout Final;
- a `Sugestao_Remanejamento` permanece inalterada;
- o Motor de Distribuicao permanece inalterado;
- saldos, capacidades e dias nao sao recalculados;
- o resultado final e ordenado por destino crescente e origem crescente.

### Limitacoes

- Nao exporta TXT.
- Nao altera a memoria de calculo da sugestao.
- Nao altera distribuicoes ja calculadas.
- Nao atualiza estoque do destino.

### Proximos passos

- implementar a exportacao TXT por filial destino;
- validar o conteudo gerado contra o padrao operacional de importacao;
- manter o Layout Final como fonte unica da exportacao TXT.

## Sprint 6 - Exportacao TXT Operacional

### Objetivo

Exportar o Layout Final em arquivos TXT operacionais, mantendo exatamente o formato utilizado pelo VBA.

A Sprint 6 nao implementa regra de negocio nova, nao altera o Motor de Distribuicao, nao modifica a `Sugestao_Remanejamento`, nao recalcula saldo, nao recalcula capacidade e nao altera o Layout Final. Ela apenas grava os registros finais em arquivos TXT por filial destino.

### Escopo

O escopo da Sprint 6 contempla:

- criar um exportador especifico para arquivos TXT;
- consumir exclusivamente o Layout Final;
- agrupar os registros por destino;
- criar um arquivo TXT para cada destino;
- gravar cada linha no formato operacional esperado;
- exibir a quantidade de arquivos gerados;
- exibir o nome dos arquivos gerados;
- exibir a quantidade de linhas de cada arquivo;
- exibir o conteudo completo do primeiro arquivo gerado para conferencia.

### Arquivos criados ou alterados

- `EP_Platform/exportadores/__init__.py`
- `EP_Platform/exportadores/exportador_txt.py`
- `EP_Platform/main.py`
- `Docs/Sprints_EP_Platform.md`

### Estrutura dos arquivos TXT

Nome do arquivo:

```text
Remanejar Filial <Destino>.txt
```

Cada linha contem exatamente:

```text
Origem;Produto;Quantidade
```

Os arquivos nao possuem cabecalho.

### Regras implementadas

- o exportador recebe apenas registros do Layout Final;
- os registros sao agrupados por `Destino`;
- cada destino gera exatamente um arquivo TXT;
- o destino nao e escrito dentro do arquivo;
- a descricao nao e exportada;
- cada linha e gravada como `Origem;Produto;Quantidade`;
- os arquivos sao gravados sem cabecalho;
- a exportacao preserva a ordem recebida do Layout Final dentro de cada destino.

### Restricoes preservadas

O exportador TXT nao acessa:

- Motor de Distribuicao;
- `Sugestao_Remanejamento`;
- Calculadora de Capacidade;
- Preparador do Motor.

### Limitacoes

- Nao cria interface de selecao de pasta.
- Nao implementa logs persistentes.
- Nao altera os dados que recebe do Layout Final.

### Proximos passos

- integrar a escolha do local de exportacao na interface da EP Platform;
- registrar a execucao e os arquivos gerados em logs;
- validar o consumo dos TXT pelo processo operacional definitivo.
