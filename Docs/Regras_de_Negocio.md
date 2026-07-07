# Regras de Negócio

## Objetivo

O objetivo do remanejamento de estoque é apoiar a redistribuição de produtos entre filiais, utilizando informações de estoque e excesso para sugerir movimentações operacionais.

A ferramenta busca identificar produtos com excesso em determinadas origens e lojas aptas a receber esses itens, reduzindo análise manual e padronizando a geração das sugestões.

## Entradas

### Importação Estoque

Base utilizada para representar a posição de estoque das filiais.

A macro possui rotina específica para importação e ajuste dessa base, identificada no VBA pelo procedimento `Importar_Estoque_Filiais` e por rotinas auxiliares de preparação dos dados.

As regras detalhadas de layout, colunas obrigatórias e tratamento de campos devem ser complementadas posteriormente a partir da especificação completa do arquivo de entrada ou da análise detalhada do código VBA.

### Importação Excesso

Base utilizada para representar os produtos ou saldos considerados em excesso.

A macro possui rotina específica para importação dessa base, identificada no VBA pelo procedimento `Importar_Excesso`, além de validação de layout e ajuste da base importada.

As regras detalhadas de layout, validações obrigatórias e critérios de identificação do excesso devem ser complementadas posteriormente a partir da especificação completa do arquivo de entrada ou da análise detalhada do código VBA.

## Processamento

### Cálculo da capacidade

A ferramenta calcula informações relacionadas à capacidade de absorção das filiais a partir da base de estoque importada.

O projeto possui rotina VBA específica para cálculo das colunas do estoque das filiais, identificada como `Calcular_Colunas_Estoque_Filiais`.

Os detalhes exatos da fórmula de capacidade devem ser complementados posteriormente a partir da regra operacional validada no VBA.

### Cálculo do excesso

A ferramenta utiliza a base de excesso importada para identificar itens disponíveis para remanejamento.

A descrição detalhada dos critérios que classificam um item como excesso deve ser complementada posteriormente, caso dependa exclusivamente do código VBA ou de regra operacional externa.

### Dias de estoque

O processo considera indicadores derivados do estoque para apoiar a decisão de remanejamento.

Caso o cálculo de dias de estoque seja utilizado diretamente pela macro, a fórmula exata deverá ser documentada posteriormente com base no código VBA e no layout das bases.

### Distribuição do excesso

A macro gera sugestões de remanejamento com base na relação entre origem com disponibilidade e filiais aptas a absorver produtos.

O procedimento VBA `Gerar_Sugestao_Remanejamento` indica a etapa responsável pela geração dessas sugestões.

A regra exata de distribuição, limites por filial e critérios de parada devem ser complementados posteriormente a partir da análise detalhada da macro.

### Priorização das filiais

A ferramenta identifica lojas aptas para absorção e gera uma sugestão estruturada.

Caso exista ordenação, ranqueamento ou prioridade específica entre filiais, essa regra deverá ser complementada posteriormente a partir do VBA, para evitar documentar critérios não confirmados.

### Geração da sugestão

A sugestão de remanejamento é gerada automaticamente após o processamento das bases.

A macro também possui etapa posterior para geração do remanejamento final, identificada pelo procedimento `Gerar_Remanejamento_Final`.

## Saídas

### Sugestão_Remanejamento

Resultado intermediário com as sugestões calculadas pela ferramenta para revisão operacional.

### Remanejamento_Final

Resultado final após a consolidação ou confirmação das sugestões de remanejamento.

### Exportação TXT

A ferramenta exporta arquivos TXT por filial para utilização operacional.

A etapa de exportação é indicada no VBA pelo procedimento `Exportar_Remanejamento_TXT`.

## Fluxograma

```text
Importar Estoque
↓
Importar Excesso
↓
Calcular Capacidade
↓
Gerar Sugestões
↓
Exportar TXT
```

## Pontos a complementar manualmente

As informações abaixo devem ser detalhadas futuramente quando houver documentação funcional completa ou revisão específica das regras no VBA:

- Layout completo da base de estoque.
- Layout completo da base de excesso.
- Fórmula exata de capacidade.
- Critério exato de excesso.
- Fórmula de dias de estoque, se aplicável.
- Critério de priorização das filiais.
- Limites de quantidade por origem e destino.
- Regras específicas de validação antes da exportação TXT.