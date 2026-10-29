# Demo 3 — decisões tipadas com o juiz (System One)

Três notebooks auto-contidos sobre o mesmo CSV do demo-1 (18 reclamações,
5 categorias), com outro protocolo: em vez de prompt + parse de texto,
uma chamada ao Jev com perguntas tipadas (`choice`, `score`, `noul`) via
`../jev.py`. Cada resposta volta com valor, confiança e probabilidades —
o modelo mede, o código decide. O mapa completo das camadas está no
[README raiz](../README.md).

| Notebook | O que acontece |
|---|---|
| [01_triagem_jev.ipynb](01_triagem_jev.ipynb) | uma chamada, 4 perguntas por reclamação (categoria, irritação, urgência, dados faltando); placar 16/18 e a fila de revisão definida por threshold |
| `02_agente_juiz.ipynb` | (em construção) o laço do demo-1 com o juiz System One nos dois pontos de decisão: na ação e na resposta |
| `03_model_route.ipynb` | (em construção) o juiz escolhendo qual modelo responde cada passo |

## Antes de rodar

Requer o ambiente da raiz pronto (`.venv` + `.env`). A mesma `LLM_API_KEY`
serve: com `JEV_API_KEY` vazio, o `jev.py` reusa a chave do chat. Guia
completo: [Setup no README raiz](../README.md#setup).

```
make setup
make env        # preencher a chave
make test-jev   # caminho feliz (uma chamada pequena)
make notebooks  # abrir os notebooks
```

## O que você vai ver

Os números abaixo vêm do output salvo no notebook (modelo
`jev-1.13-free`, executado em 2026-10-28); os seus variam com o modelo —
o output registra qual foi usado.

- **Placar do 01: 16/18 (89%)** contra o gabarito do CSV, sem prompt e sem
  exemplos. Os erros caem nas armadilhas multimotivo do demo-1 (índices
  15 e 16).
- **Confiança em degraus, não numa curva:** a maioria volta com 1.0 e as
  linhas que fogem disso são justamente as que erram. Com threshold 0.9,
  17 das 18 resolvem sozinhas e uma vai para revisão humana — e é essa uma
  que erra; o outro erro (0.97) passou pelo gate.
- **Custo real:** `usage_total()` fecha a demo inteira (triagem +
  experimentos) em ~13k tokens de input e `cost: 0` no modelo `-free`. No
  `jev-1.13` pago, a US$0.042/M de input, isso dá ~US$0.0006.
- **Jagged edge do `score`:** o comportamento do upstream varia entre
  execuções. O notebook tenta a pergunta no formato `score` e registra o
  que aconteceu no dia (resposta ou erro), sem mock.

## Dicas desta pasta

- Os notebooks são auto-contidos: perguntas e pequenos trechos de código
  são duplicados de propósito. Ao mudar uma pergunta, replique nos outros
  para o placar continuar comparável.
- `JEV_MODEL` no `.env` manda: trocar de modelo não exige mexer no código.
  O `-free` é tempo limitado; `jev-1.13` é o fallback pago.
- O threshold é política, não modelo: mudar o número muda a fila de
  revisão sem uma chamada a mais ao gateway.
