# Prompt médio — saída definida e padronizada

Mesmo ciclo do prompt pequeno, mas com o contrato de saída escrito: o
que deve existir no final, em que formato, com que nomes e regras de
desempate. Serve para mostrar que expressar "quando estiver pronto
sabe-se que está pronto" reduz retrabalho: o agente sai do "será que
atendeu?" e passa a validar contra a checklist que o próprio prompt
declara.

```
Leia o arquivo reclamacoes.csv nesta pasta e produza três entregas
usa os MCPs filesystem, sqlite e fetch. Não improvise formatos: a
saída mínima aceitável está definida abaixo em "Contrato de saída".

## Contrato de saída

1. resumo.md (na pasta atual), com esta estrutura exata:
   - Título em nível 1 e um parágrafo de contexto em 1-3 frases;
   - Tabela markdown com colunas | Categoria | Reclamações | % do total |,
     ordenada da maior para a menor contagem;
   - Linha de total ao fim da tabela;
   - Seção "Dado externo" com a cotação USD/BRL buscada na
     https://economia.awesomeapi.com.br/json/last/USD-BRL e a
     data/hora da coleta.
2. database podcast.sqlite: tabela top3 (colunas: categoria TEXT,
   contagem INTEGER, percentual REAL) com exatamente 3 linhas.
3. Resposta final no chat, com no máximo 3 linhas: a categoria líder
   com a contagem e o percentual das duas maiores somadas — sem
   despejar a tabela inteira no chat.

## Regras

- Categorias por frequência; empate -> ordem alfabética; registre a
  regra usada como comentário em resumo.md.
- Não eduque: se faltar dado, diga o que falta e pare.
- Lista final de MCPs usados na última linha da resposta.
```

O que a plateia espera ver: o mesmo ciclo, mas o pedido fecha em três
entregas verificáveis — bom momento para apontar "prompt como
especificação".

Saída esperada (com a base de 18 reclamações do projeto):

- `resumo.md` com a estrutura exata: título nível 1, parágrafo de
  contexto, tabela `| Categoria | Reclamações | % do total |`
  (cobranca 27,8%, entrega 22,2%, app 16,7%, atendimento 16,7%,
  produto 16,7%), linha de total, seção "Dado externo" com a cotação
  e data/hora, e a regra de desempate como comentário no arquivo.
- `podcast.sqlite`: tabela `top3 (categoria, contagem, percentual)`
  com exatamente 3 linhas — cobranca 5/27,78, entrega 4/22,22,
  app 3/16,67.
- No chat, no máximo 3 linhas: *"Categoria líder: cobrança, 5 de 18
  (27,8%). Somando a segunda, entrega: 50% dos registros em duas
  categorias. MCPs: filesystem, sqlite, fetch."* — sem despejar a
  tabela no chat.
