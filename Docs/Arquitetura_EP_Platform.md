# Arquitetura Logica - Remanejamento de Estoque na EP Platform

## 1. Objetivo da arquitetura

Definir a organizacao logica da solucao de Remanejamento de Estoque na EP Platform, orientando a implementacao em modulos, responsabilidades e fluxo de processamento.

Esta arquitetura deve preservar o comportamento atual do processo em Excel VBA na primeira versao da migracao, mas sem copiar a estrutura do Excel como modelo tecnico. O VBA deve ser usado como referencia de comportamento funcional, nao como referencia de arquitetura.

O desenho proposto busca separar claramente:

- interface de operacao;
- importacao e validacao de arquivos;
- normalizacao dos dados;
- regras de negocio;
- geracao das saidas;
- registro e auditoria da execucao.

## 2. Visao geral da solucao

A solucao na EP Platform deve executar um processo controlado de remanejamento a partir de dois arquivos de entrada:

- Estoque das filiais;
- Excesso por loja/produto.

O estoque e usado para calcular a capacidade de absorcao de cada loja por produto. O excesso indica os produtos e quantidades disponiveis para remanejamento a partir de uma loja de origem.

Com essas informacoes, o sistema executa o motor de distribuicao, gera uma sugestao detalhada, consolida o remanejamento final e exporta arquivos TXT por filial destino.

A primeira versao deve reproduzir o comportamento atual do VBA, inclusive a regra de nao atualizar o estoque do destino durante a distribuicao.

## 3. Fluxo macro do processo

Fluxo esperado na EP Platform:

```text
Importar Estoque
↓
Validar Estoque
↓
Normalizar Estoque
↓
Calcular Capacidade
↓
Importar Excesso
↓
Validar Excesso
↓
Normalizar Excesso
↓
Executar Motor de Distribuicao
↓
Gerar Sugestao
↓
Gerar Remanejamento Final
↓
Exportar TXT
↓
Registrar Execucao
```

O fluxo deve ser tratado como uma execucao unica, com parametros, arquivos de entrada, resultados, alertas e logs associados.

## 4. Separacao entre interface, regra de negocio e saida

A EP Platform nao deve copiar a estrutura do Excel. Abas, botoes, celulas e formatacoes devem ser entendidos apenas como a forma atual de operacao no VBA.

Na nova arquitetura:

- A interface deve permitir upload dos arquivos, definicao dos parametros e acompanhamento do resultado.
- A regra de negocio deve ficar em componentes independentes da interface.
- As saidas devem ser geradas por modulos proprios, a partir de dados estruturados.
- Logs e historico devem ser parte do processo, nao depender de mensagens visuais.

Separacao proposta:

| Camada | Responsabilidade |
| --- | --- |
| Interface | Receber arquivos, parametros e exibir resultados |
| Aplicacao | Orquestrar o fluxo da execucao |
| Dominio | Aplicar calculos, validacoes funcionais e distribuicao |
| Infraestrutura | Ler arquivos, gravar logs e exportar TXT |
| Saidas | Gerar sugestao, remanejamento final e arquivos por destino |

## 5. Modulos propostos

### 5.1 Importador de Estoque

Responsabilidade:

- Receber o arquivo de estoque das filiais.
- Ler a primeira planilha ou estrutura tabular equivalente.
- Converter o conteudo em uma colecao estruturada para processamento.

Entradas:

- Arquivo de estoque informado pelo usuario.
- Metadados da execucao.

Saidas:

- Dados brutos de estoque importados.
- Alertas tecnicos de leitura, quando houver.

Regras envolvidas:

- O arquivo pode conter linhas iniciais de relatorio antes do cabecalho real.
- A origem atual pode vir em formato Excel/SpreadsheetML, mesmo com extensao `.xls`.
- O importador nao deve executar regra de negocio; deve apenas ler e entregar os dados brutos.

Pontos de atencao:

- Nao assumir que a extensao define o formato real do arquivo.
- Preservar os valores originais para auditoria.
- Separar erro de leitura de erro de layout.

### 5.2 Importador de Excesso

Responsabilidade:

- Receber o arquivo de excesso.
- Ler a estrutura tabular com loja, produto, descricao e quantidade.
- Converter o conteudo em dados brutos para validacao.

Entradas:

- Arquivo de excesso informado pelo usuario.
- Metadados da execucao.

Saidas:

- Dados brutos de excesso importados.
- Alertas tecnicos de leitura, quando houver.

Regras envolvidas:

- O arquivo atual pode ser tabulado, mesmo usando extensao `.xls`.
- O importador deve preservar as colunas lidas para permitir validacao posterior.

Pontos de atencao:

- Nao corrigir layout automaticamente no importador.
- Nao aplicar filtros de negocio nesse modulo.
- Manter rastreabilidade entre linha original e linha processada.

### 5.3 Validador de Layout

Responsabilidade:

- Validar se os dados importados possuem estrutura minima para processamento.
- Separar erros impeditivos de alertas informativos.

Entradas:

- Dados brutos de estoque.
- Dados brutos de excesso.
- Parametros da execucao, especialmente `Dias Alvo`.

Saidas:

- Resultado de validacao.
- Lista de erros impeditivos.
- Lista de alertas nao impeditivos.

Regras envolvidas:

- `Dias Alvo` deve ser maior que zero.
- O estoque deve conter dados apos importacao e limpeza.
- O excesso deve conter dados apos importacao e limpeza.
- No excesso, a linha 2 deve conter:
  - coluna A numerica e nao vazia;
  - coluna B numerica e nao vazia;
  - coluna C textual e nao vazia;
  - coluna D numerica e nao vazia;
  - coluna E vazia.

Pontos de atencao:

- A primeira versao deve preservar a validacao atual do VBA, que valida o excesso pela linha 2.
- O estoque nao possui validacao completa no comportamento atual.
- Validacoes adicionais devem ser registradas como melhoria futura, salvo se forem apenas tecnicas e nao alterarem o resultado.

### 5.4 Normalizador de Dados

Responsabilidade:

- Transformar os dados brutos em estruturas padronizadas para as regras de negocio.
- Remover linhas de relatorio e rodape.
- Preencher filiais em branco.
- Padronizar tipos de dados usados no calculo.

Entradas:

- Dados brutos de estoque validado.
- Dados brutos de excesso validado.

Saidas:

- Estoque normalizado.
- Excesso normalizado.

Regras envolvidas:

- Remover linhas de cabecalho operacional anteriores ao cabecalho real.
- Remover linhas cujo conteudo de controle contenha `H:` ou `Usuario:`.
- Preencher filial em branco com a ultima filial valida encontrada.
- Preservar codigos de filial e produto como identificadores.

Pontos de atencao:

- A normalizacao deve reproduzir a forma como o VBA prepara os dados antes dos calculos.
- A descricao do produto deve ser preservada a partir do excesso para as saidas.
- A linha original deve permanecer rastreavel para auditoria.

### 5.5 Calculadora de Capacidade

Responsabilidade:

- Calcular indicadores de estoque e capacidade por filial/produto.
- Classificar o status de absorcao.

Entradas:

- Estoque normalizado.
- Parametro `Dias Alvo`.

Saidas:

- Estoque enriquecido com dias de estoque, estoque maximo, capacidade e status de absorcao.

Regras envolvidas:

```text
diasAtual = estoqueAtual / (media30 / 30)
estoqueMaximo = (media30 / 30) * diasAlvo
capacidade = max(0, estoqueMaximo - estoqueAtual)
```

Quando `media30 <= 0`:

- `diasAtual = 0`;
- `estoqueMaximo = 0`;
- `capacidade = 0`;
- status = `Sem Media`.

Classificacao:

- `Sem Media`: media menor ou igual a zero.
- `Nao Absorve`: media positiva e dias atuais maior ou igual ao Dias Alvo.
- `Pode Absorver`: media positiva e dias atuais abaixo do Dias Alvo.

Pontos de atencao:

- A base de media e fixa em 30 dias na regra atual.
- O status cadastral do produto nao e usado como filtro pelo comportamento atual.
- A capacidade deve ser recalculavel pelo motor de distribuicao com os mesmos criterios.

### 5.6 Motor de Distribuicao

Responsabilidade:

- Distribuir o saldo de excesso entre lojas destino aptas.
- Aplicar as prioridades e rodadas do comportamento atual.
- Produzir eventos de distribuicao para posterior geracao da sugestao.

Entradas:

- Estoque calculado.
- Excesso normalizado.
- Parametro `Dias Alvo`.

Saidas:

- Alocacoes sugeridas por origem, produto e destino.
- Saldos nao atendidos.

Regras envolvidas:

- A quantidade distribuivel e limitada pelo estoque disponivel da origem:

```text
saldoInicial = min(qtdExcesso, estoqueOrigem)
```

- Se a origem nao tiver estoque disponivel, nenhuma sugestao e criada.
- A loja origem nao pode ser destino.
- A base de estoque deve ser priorizada por produto crescente e media decrescente.
- A distribuicao ocorre em duas rodadas.

Rodada 1:

- Somente lojas com estoque atual menor ou igual a zero.
- Maximo de 1 unidade por loja.

```text
qtdEnviar = min(saldoRestante, capacidade, 1)
```

Rodada 2:

- Somente lojas com estoque atual maior que zero.
- Prioridade para maiores medias.

```text
qtdEnviar = min(saldoRestante, capacidade)
```

Pontos de atencao:

- Na primeira versao, o estoque do destino nao deve ser atualizado durante a distribuicao.
- Essa preservacao e obrigatoria para manter compatibilidade com o VBA.
- Atualizar estoque virtual do destino deve ser tratado somente como evolucao futura controlada.
- O motor deve registrar saldos sem destino quando nao houver capacidade suficiente.

### 5.7 Gerador de Sugestao

Responsabilidade:

- Transformar as alocacoes do motor de distribuicao em uma sugestao detalhada e auditavel.
- Registrar os dados intermediarios necessarios para conferencia operacional.

Entradas:

- Alocacoes geradas pelo motor de distribuicao.
- Saldos nao atendidos.
- Dados de estoque e excesso usados na execucao.

Saidas:

- Sugestao de remanejamento detalhada.

Regras envolvidas:

A sugestao deve conter:

- origem;
- produto;
- descricao;
- quantidade original de excesso;
- destino ou `Sem loja destino`;
- dias atuais do destino;
- capacidade do destino;
- quantidade sugerida;
- dias apos envio;
- saldo restante.

Calculo de dias apos:

```text
diasApos = (estoqueAtualDestino + qtdEnviar) / (mediaDestino / 30)
```

Pontos de atencao:

- A sugestao pode conter quantidades fracionarias antes do remanejamento final.
- Linhas sem destino devem aparecer na sugestao, mas nao devem ir para o TXT.
- A sugestao deve permitir auditoria do motivo de sobra.

### 5.8 Gerador de Remanejamento Final

Responsabilidade:

- Consolidar a sugestao em layout operacional final.
- Preparar os dados que serao exportados.

Entradas:

- Sugestao de remanejamento.

Saidas:

- Remanejamento final com destino, origem, produto, descricao e quantidade.

Regras envolvidas:

- Excluir linhas com destino `Sem loja destino`.
- Incluir apenas sugestoes com quantidade arredondada maior que zero.
- Arredondar a quantidade sugerida para inteiro.
- Ordenar por destino e origem.

Pontos de atencao:

- O arredondamento ocorre nesta etapa, nao no motor de distribuicao.
- A descricao deve permanecer disponivel para conferencia, mesmo nao sendo exportada no TXT.
- O layout final deve ser independente de abas ou celulas do Excel.

### 5.9 Exportador TXT

Responsabilidade:

- Gerar arquivos TXT por filial destino.
- Aplicar o formato exigido para importacao operacional.

Entradas:

- Remanejamento final.
- Local ou mecanismo de armazenamento da exportacao.

Saidas:

- Um arquivo TXT para cada filial destino.

Regras envolvidas:

Nome do arquivo:

```text
Remanejar Filial <destino>.txt
```

Formato de cada linha:

```text
origem;produto;quantidade
```

Pontos de atencao:

- O destino nao aparece dentro do arquivo, apenas no nome.
- A descricao nao e exportada.
- Linhas sem destino nao devem ser exportadas.
- A exportacao deve ser rastreavel pela execucao que a gerou.

### 5.10 Registro de Execucao / Logs

Responsabilidade:

- Registrar historico, parametros, arquivos processados, resultados e alertas.
- Permitir auditoria e suporte operacional.

Entradas:

- Metadados da execucao.
- Parametros utilizados.
- Resultado dos importadores, validadores, calculos, distribuicao e exportacao.

Saidas:

- Registro de execucao.
- Logs tecnicos e funcionais.
- Resumo de resultado.

Regras envolvidas:

- Registrar valor de `Dias Alvo`.
- Registrar arquivos de entrada utilizados.
- Registrar quantidade de linhas importadas, normalizadas e descartadas.
- Registrar quantidade de sugestoes geradas.
- Registrar saldos sem destino.
- Registrar arquivos TXT gerados.

Pontos de atencao:

- Logs nao devem substituir validacoes.
- Erros impeditivos devem encerrar a execucao de forma controlada.
- Alertas devem ficar disponiveis para analise sem alterar o comportamento compativel com o VBA.

## 6. Principios da migracao

A migracao para a EP Platform deve seguir estes principios:

- A EP Platform nao deve copiar a estrutura do Excel.
- A regra de negocio deve ficar separada da interface.
- O VBA deve ser usado como referencia de comportamento, nao como modelo de arquitetura.
- A primeira versao deve preservar o comportamento atual do VBA.
- Melhorias devem ser tratadas como evolucoes futuras controladas.
- O estoque do destino nao deve ser atualizado durante a distribuicao na primeira versao, para manter compatibilidade com o comportamento atual.
- O processo deve ser auditavel de ponta a ponta.
- As saidas devem ser reproduziveis a partir dos mesmos arquivos de entrada e parametros.

## 7. Consideracoes para implementacao

A implementacao deve priorizar componentes pequenos, testaveis e independentes da interface. O motor de regras deve receber dados estruturados e devolver resultados estruturados, sem depender de arquivos Excel, abas, botoes ou celulas.

Recomendacoes:

- Criar testes automatizados com massas comparadas ao resultado atual do VBA.
- Manter fixtures de estoque e excesso para homologacao.
- Separar erros tecnicos de erros funcionais.
- Preservar rastreabilidade entre entrada, sugestao, remanejamento final e TXT.
- Tratar qualquer mudanca de comportamento como evolucao planejada, nao como ajuste implicito da migracao.
