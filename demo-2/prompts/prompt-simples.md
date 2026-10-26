# Prompt pequeno — o ciclo completo em uma linha

Instrução única, sem formatação definida: o agente decide tudo sozinho.
Serve para mostrar o básico do MCP em menos de um minuto: um pedido, os
três servers, o resultado.

```
Leia reclamacoes.csv (nesta pasta) e faça o ciclo completo usando os
três MCPs — filesystem, sqlite e fetch:
1. escreva um resumo.md em markdown (com tabela) contendo as
   categorias, suas contagens e o total;
2. crie em demo.sqlite uma tabela top3 com as três categorias mais
   frequentes e suas contagens; em caso de empate, ordene
   alfabeticamente e registre a decisão;
3. busque em https://economia.awesomeapi.com.br/json/last/USD-BRL a
   cotação do dólar e acrescente esse dado externo ao resumo.md;
4. leia de volta o resumo.md e a tabela top3 e responda em uma frase
   qual é a categoria com mais reclamações, citando os números;
5. ao final, liste quais MCPs você usou.
```

O que a plateia espera ver: o agente planejando a sequência sozinho
(escrever → gravar → buscar externo → reabrir os artefatos e concluir).
O item 5 é a prova visual de que os três servers entraram no fluxo.

Saída esperada (com a base de 18 reclamações do projeto):

- No chat, algo como: *"A categoria com mais reclamações é cobrança,
  com 5 dos 18 registros — mais que entrega (4) e o triplo de app,
  atendimento e produto (3 cada)."* + a lista dos três MCPs usados.
- `resumo.md` criado: título, parágrafo de contexto e tabela de
  categorias (cobranca 5, entrega 4, app/atendimento/produto 3),
  com a cotação USD/BRL buscada no fetch (~5,02 na coleta de
  referência).
- `demo.sqlite` com a tabela `top3`: cobranca (5), entrega (4) e
  a primeira categoria em ordem alfabética entre as que têm 3.
