# Regras de Negocio - Remanejamento de Estoque para EP Platform

## 1. Objetivo da migracao

Migrar o processo de Remanejamento de Estoque, atualmente executado em Excel VBA, para a EP Platform preservando integralmente o comportamento funcional existente em producao.

O objetivo da migracao nao e traduzir o codigo VBA, mas reproduzir corretamente as regras de negocio: importacao dos arquivos, normalizacao dos dados, calculo de capacidade das lojas, distribuicao do excesso, geracao do remanejamento final e exportacao dos arquivos TXT.

A primeira versao na EP Platform deve manter compatibilidade com o comportamento atual, inclusive eventuais limitacoes do algoritmo, para evitar diferencas operacionais em relacao ao processo vigente.

## 2. Visao geral do fluxo

O fluxo funcional do sistema e:

1. Importar o arquivo de estoque das filiais.
2. Normalizar o estoque importado.
3. Calcular dias de estoque, estoque maximo, capacidade e status de absorcao.
4. Importar o arquivo de excesso.
5. Normalizar e validar o excesso importado.
6. Gerar a sugestao de remanejamento.
7. Gerar o remanejamento final no layout operacional.
8. Exportar arquivos TXT por filial destino.

O parametro central do fluxo e `Dias Alvo`, com valor padrao de 90 dias. Esse parametro define o limite maximo de estoque desejado por filial/produto.

## 3. Entradas do sistema

O sistema utiliza duas entradas principais:

- Arquivo de Estoque Filiais: contem a posicao de estoque, media de venda e dados cadastrais dos produtos por filial.
- Arquivo de Excesso: contem a lista de produtos e quantidades em excesso em uma filial de origem.

Ambos os arquivos podem possuir linhas de cabecalho operacional, linhas de relatorio ou rodape. O processo atual remove essas linhas antes de executar os calculos.

## 4. Layout de Estoque

Apos a limpeza inicial, o estoque deve possuir as seguintes colunas:

| Coluna | Campo | Descricao |
| --- | --- | --- |
| A | CodFilial | Codigo da filial |
| B | CodProduto | Codigo do produto |
| C | EAN | Codigo EAN do produto |
| D | Descricao | Descricao do produto |
| E | Fabricante | Fabricante do produto |
| F | Linha | Linha/categoria do produto |
| G | StatusProduto | Status cadastral do produto |
| H | MediaF | Media de venda da filial para o produto |
| I | QtEstoqueComercial | Estoque comercial atual |

Depois da importacao, o sistema acrescenta colunas calculadas:

| Coluna | Campo | Descricao |
| --- | --- | --- |
| J | Dias Estoque Atual | Quantidade de dias coberta pelo estoque atual |
| K | Estoque Maximo | Estoque maximo permitido para o valor de Dias Alvo |
| L | Capacidade | Quantidade que a loja ainda pode receber ate o Dias Alvo |
| M | Status Absorcao | Indicador de aptidao da linha para absorver estoque |

No arquivo original de estoque, a filial pode aparecer somente na primeira linha de cada bloco. As linhas seguintes do mesmo bloco podem vir com a coluna de filial vazia. A regra atual preenche essas linhas com a ultima filial informada.

## 5. Layout de Excesso

O arquivo de excesso deve possuir as seguintes colunas:

| Coluna | Campo | Descricao |
| --- | --- | --- |
| A | Filial/Loja | Codigo da filial de origem do excesso |
| B | Produto | Codigo do produto em excesso |
| C | Descricao | Descricao do produto |
| D | Quantidade | Quantidade em excesso |
| E | Vazia | Deve permanecer vazia |

O layout atual analisado possui arquivo tabulado com cabecalho equivalente a:

- Loja
- codigo
- descricao
- quantidade

O validador atual nao depende rigidamente do nome do cabecalho. A validacao efetiva e feita sobre a linha 2, verificando se os tipos e posicoes dos dados estao corretos.

## 6. Validacoes obrigatorias

Validacoes existentes que devem ser preservadas:

- `Dias Alvo` deve ser maior que zero.
- O arquivo de estoque deve conter dados apos a importacao e limpeza.
- O arquivo de excesso deve conter dados apos a importacao e limpeza.
- No excesso, a coluna A da linha 2 deve conter filial numerica e nao vazia.
- No excesso, a coluna B da linha 2 deve conter codigo de produto numerico e nao vazio.
- No excesso, a coluna C da linha 2 deve conter descricao textual e nao vazia.
- No excesso, a coluna D da linha 2 deve conter quantidade numerica e nao vazia.
- No excesso, a coluna E da linha 2 deve estar vazia.
- A exportacao TXT so pode ocorrer quando houver dados no remanejamento final.

Normalizacoes obrigatorias:

- Remover linhas de cabecalho operacional antes do cabecalho real.
- Remover linhas de rodape que contenham `H:` ou `Usuario:` na coluna A.
- Preencher filial em branco com a ultima filial valida encontrada.

Ponto importante: no comportamento atual nao ha validacao explicita do layout completo do estoque, duplicidade de linhas, produto inexistente, quantidade negativa, status cadastral do produto ou consistencia entre produto e descricao.

## 7. Calculos

Para cada linha do estoque, o sistema calcula:

```text
diasAtual = estoqueAtual / (media30 / 30)
estoqueMaximo = (media30 / 30) * diasAlvo
capacidade = max(0, estoqueMaximo - estoqueAtual)
```

Onde:

- `media30` corresponde a `MediaF`.
- `estoqueAtual` corresponde a `QtEstoqueComercial`.
- `diasAlvo` corresponde ao parametro informado pelo usuario.

Se `media30 <= 0`, os valores calculados devem ser:

- `diasAtual = 0`
- `estoqueMaximo = 0`
- `capacidade = 0`
- `Status Absorcao = Sem Media`

Status de absorcao:

- `Sem Media`: media menor ou igual a zero.
- `Nao Absorve`: media positiva, mas dias atuais maior ou igual ao Dias Alvo.
- `Pode Absorver`: media positiva e dias atuais abaixo do Dias Alvo.

Durante a distribuicao, a capacidade do destino e recalculada a partir da media e do estoque atual, seguindo a mesma logica de Dias Alvo.

## 8. Regras de loja apta

Uma loja pode ser considerada apta em dois contextos.

Para indicadores gerenciais:

- A loja e contada como apta se possuir ao menos uma linha com `Status Absorcao = Pode Absorver`.

Para receber um produto especifico na distribuicao:

- A loja deve possuir o mesmo produto no estoque.
- A loja destino deve ser diferente da loja origem.
- A media de venda do produto na loja deve ser maior que zero.
- A capacidade calculada para o produto deve ser positiva.
- A loja deve atender a regra da rodada de distribuicao em execucao.

## 9. Regras de excesso

O excesso e informado pelo arquivo de Excesso, coluna D.

Antes de distribuir, o sistema verifica o estoque atual da filial origem para o produto informado. A quantidade efetivamente distribuivel e limitada pelo estoque disponivel na origem:

```text
saldoInicial = min(qtdExcesso, estoqueOrigem)
```

Se o estoque da origem nao for encontrado, ou se for menor ou igual a zero, nenhuma sugestao e gerada para aquela linha de excesso.

Se a quantidade de excesso for maior que o estoque atual da origem, o sistema distribui somente ate o limite do estoque atual encontrado.

## 10. Regras de distribuicao

Antes de distribuir, a base de estoque e ordenada por:

1. Produto em ordem crescente.
2. Media de venda em ordem decrescente.

Para cada linha de excesso, o sistema percorre as lojas candidatas em duas rodadas.

Rodada 1:

- Considera somente lojas com estoque atual menor ou igual a zero para o produto.
- Cada loja pode receber no maximo 1 unidade nessa rodada.
- A quantidade enviada e limitada por saldo restante, capacidade e limite de 1 unidade.

Formula conceitual:

```text
qtdEnviar = min(saldoRestante, capacidade, 1)
```

Rodada 2:

- Considera somente lojas com estoque atual maior que zero para o produto.
- Prioriza lojas com maior media de venda.
- A quantidade enviada e limitada por saldo restante e capacidade.

Formula conceitual:

```text
qtdEnviar = min(saldoRestante, capacidade)
```

Apos cada envio sugerido:

- o saldo restante do excesso e reduzido;
- os dias apos envio sao calculados para o destino;
- uma linha e registrada na sugestao.

Formula de dias apos:

```text
diasApos = (estoqueAtualDestino + qtdEnviar) / (mediaDestino / 30)
```

Se, ao final das duas rodadas, ainda existir saldo, o sistema registra uma linha de sugestao com destino `Sem loja destino`.

### Ponto de atencao obrigatorio

No comportamento atual do VBA, o estoque do destino nao e atualizado durante a distribuicao.

Isso significa que, se houver mais de uma linha de excesso para o mesmo produto ou se uma loja receber sugestoes em momentos diferentes da mesma execucao, a capacidade do destino continua sendo calculada com base no estoque original importado, e nao no estoque acrescido das sugestoes anteriores.

Essa regra deve ser preservada na primeira versao da migracao para garantir compatibilidade com o resultado atual em producao.

Uma eventual correcao para atualizar o estoque virtual do destino durante a distribuicao deve ser tratada como evolucao futura controlada, com validacao de impacto, homologacao e aceite do negocio.

## 11. Saidas geradas

O processo gera duas saidas intermediarias/principais.

### Sugestao de Remanejamento

Estrutura:

| Campo | Descricao |
| --- | --- |
| Origem | Filial de origem do excesso |
| Produto | Codigo do produto |
| Descricao | Descricao do produto |
| Qtde Excesso | Quantidade original informada no excesso |
| Destino | Filial destino sugerida ou `Sem loja destino` |
| Dias Atual Destino | Dias de estoque antes do envio |
| Capacidade Dias Alvo | Capacidade calculada para o destino |
| Qtde Sugerida | Quantidade sugerida para envio |
| Dias Apos | Dias de estoque apos o envio sugerido |
| Saldo Restante | Saldo ainda nao distribuido apos a sugestao |

### Remanejamento Final

Estrutura:

| Campo | Descricao |
| --- | --- |
| Destino | Filial que recebera o produto |
| Origem | Filial que enviara o produto |
| Produto | Codigo do produto |
| Descricao | Descricao do produto |
| Qtde Enviar | Quantidade final arredondada |

Regras do remanejamento final:

- Excluir linhas com destino `Sem loja destino`.
- Incluir apenas sugestoes com quantidade arredondada maior que zero.
- Arredondar a quantidade sugerida para inteiro.
- Ordenar por destino e origem.

## 12. Exportacao TXT

A exportacao TXT gera um arquivo separado para cada filial destino.

Padrao do nome:

```text
Remanejar Filial <destino>.txt
```

Cada arquivo contem somente as linhas referentes ao destino correspondente.

Formato de cada linha:

```text
origem;produto;quantidade
```

A descricao do produto nao e exportada. O destino fica implicito no nome do arquivo.

## 13. Regras obrigatorias a preservar na EP Platform

Devem ser preservadas na primeira versao da migracao:

- Uso do parametro `Dias Alvo`, com padrao 90.
- Calculo de dias de estoque, estoque maximo e capacidade.
- Classificacao de absorcao em `Sem Media`, `Nao Absorve` e `Pode Absorver`.
- Preenchimento de filial em branco usando a ultima filial valida.
- Remocao de linhas de relatorio e rodape.
- Validacao do layout do excesso com base nas posicoes e tipos da linha 2.
- Limitacao da quantidade distribuivel pelo estoque disponivel da origem.
- Proibicao de enviar produto da origem para ela mesma.
- Priorizacao por produto e maior media.
- Distribuicao em duas rodadas.
- Rodada 1 para lojas zeradas, com limite de 1 unidade por loja.
- Rodada 2 para lojas com estoque positivo.
- Registro do saldo sem destino quando nao houver capacidade suficiente.
- Geracao da sugestao detalhada.
- Geracao do remanejamento final no layout operacional.
- Arredondamento da quantidade no remanejamento final.
- Exportacao TXT por destino no formato `origem;produto;quantidade`.
- Nao atualizacao do estoque do destino durante a distribuicao, para compatibilidade inicial com o VBA.

## 14. Pontos de atencao

- O estoque do destino nao e atualizado durante a distribuicao no comportamento atual do VBA.
- Essa regra deve ser preservada na primeira versao da migracao para garantir compatibilidade.
- Eventual correcao deve ser tratada como evolucao futura controlada.
- O estoque nao possui validacao explicita completa de layout no comportamento atual.
- O status cadastral do produto existe no arquivo de estoque, mas nao e usado como filtro pelo algoritmo atual.
- A validacao do excesso verifica somente a linha 2.
- Quantidades finais sao arredondadas apenas na etapa do remanejamento final.
- A sugestao pode conter quantidades fracionarias antes do arredondamento final.
- O saldo `Sem loja destino` nao e exportado no TXT.
- A ordenacao da base de estoque altera a prioridade de atendimento e deve ser reproduzida logicamente na EP Platform.
- A EP Platform deve registrar claramente os saldos nao atendidos para auditoria operacional.

## 15. Melhorias futuras

As melhorias abaixo podem ser avaliadas apos a primeira versao compativel:

- Atualizar estoque virtual dos destinos durante a distribuicao.
- Validar o layout completo do estoque.
- Validar duplicidades de filial/produto.
- Validar quantidades negativas ou inconsistentes.
- Tratar produtos existentes no excesso, mas ausentes no estoque.
- Parametrizar o limite de 1 unidade da primeira rodada.
- Parametrizar a base de media de 30 dias.
- Criar logs de importacao, validacao, calculo e exportacao.
- Registrar historico de execucoes com usuario, data, arquivos importados e parametros.
- Gerar relatorio de itens sem destino.
- Separar claramente motor de regras, importadores, validadores e exportadores.
- Criar testes automatizados com massa de dados homologada contra o resultado do VBA.
