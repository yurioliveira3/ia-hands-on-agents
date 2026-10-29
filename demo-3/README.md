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
| [02_agente_juiz.ipynb](02_agente_juiz.ipynb) | o laço do demo-1 com o juiz nos dois pontos de decisão: `Choice` na ação e `Noul` na resposta; 3 execuções |
| [03_model_route.ipynb](03_model_route.ipynb) | o juiz escolhendo qual modelo responde cada passo; economia ≈80% com concordância 5/5 entre os pares roteados |

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

Para executar os três de uma vez e gravar a saída em `export/demo3/`
(gitignored):

```
make demo3-run
```

Variáveis do juiz no `.env` (os defaults do `jev.py` já apontam para o
`-free`): `JEV_API_KEY` (vazio reusa a `LLM_API_KEY`), `JEV_BASE_URL` e
`JEV_MODEL`. O notebook 03 usa ainda `LLM_MINI_MODEL` (default
`glm-5.3-flash`, do plano Go) — o `LLM_MODEL` segue sendo o modelo
"forte" e os dois precisam ser do mesmo provedor.

## O que você vai ver

Os números abaixo vêm do output salvo nos notebooks. A execução de
referência é de **2026-10-28**, com `jev-1.13-free` no juiz,
`deepseek-v4.1-flash` como forte e `glm-5.3-flash` como mini; os seus
variam com o modelo — o output registra qual foi usado.

- **01 — triagem: 16/18 (89%)** contra o gabarito do CSV, sem prompt e
  sem exemplos. Os erros caem nas armadilhas multimotivo do demo-1
  (índices 15 e 16).
- **Confiança em degraus, não numa curva:** a maioria volta com 1.0 e as
  linhas que fogem disso são justamente as que erram. Com threshold 0.9,
  **94% (17 de 18) resolvem sozinhas** e uma vai para revisão humana —
  e é essa uma que erra (confiança 0.52); o outro erro (0.97) passou
  pelo gate. Abaixo de 0.52 o threshold aceita tudo: a fila some, o
  erro fica.
- **Custo real:** `usage_total()` fecha a triagem e os experimentos em
  ~13k tokens de entrada e `cost: 0` no modelo `-free`. No `jev-1.13`
  pago, a US$0.042/M de entrada, isso dá menos de um décimo de centavo.
- **02 — agente com juiz, 3 execuções:** o caminho feliz passa com o
  juiz aprovando (`p_interromper=0.00`) e encerrando a resposta (nota
  0.98); no pedido destrutivo o próprio modelo recusa **antes** de propor
  a ação, e o juiz chamado **fora do laço** sobre ela devolve interromper
  (`p_interromper=0.90`); e a resposta apressada termina no **teto de
  passos**, depois de o `gate_answer` devolver quatro vezes e o
  `gate_tool` barrar a ferramenta que resolveria a pergunta. O laço gastou
  7.474 tokens e o juiz 6.821 de entrada (163% do prompt do laço) em 9
  chamadas — o freio não é de graça, mas aqui custou `US$ 0.000000`.
- **03 — model-route: economia ≈80%** de custo no mix de 6 prompts
  (varia ~65–80% conforme o mix) com **concordância 5/5 entre os pares
  roteados**; o 6/6 geral inclui 1 par em que o juiz escalou para o
  forte×forte. O mini respondeu 5/6, e os gates de rota mais o juiz de
  concordância custaram 0. É uma execução de referência: reexecute para
  os seus números.
- **Jagged edge do `score`:** o comportamento do upstream varia entre
  execuções. O notebook tenta a pergunta no formato `score` e registra o
  que aconteceu no dia (resposta ou erro), sem mock. No `-free`, o
  caminho estável é `choice` e `noul`.

## Limitações reais (Jev e modelos free)

- **O Jev é pay-as-you-go do console.** A assinatura Go/Go Plus não o
  inclui; crie a chave e confira os créditos em
  https://opencode.ai/console.
- **O `-free` é tempo limitado e tem quota diária.** Ele devolve
  `cost: 0` e `billing_source: free`, mas pode responder 429 (rate
  limit) — o `jev.py` tenta de novo com backoff e, persistindo, o erro
  sobe. O fallback é `jev-1.13` (~US$0.042/M de entrada, saída grátis),
  que exige créditos na conta.
- **Os modelos de chat `-free` do OpenCode exigem o cliente OpenCode.**
  Fora dele, a mesma chamada costuma voltar 429 ou 400 (o `-free` é do
  pay-as-you-go e responde 400 no path do plano Go). Por isso o mini do
  model-route é `glm-5.3-flash`, um id pago do Go (~US$0.15/M de
  entrada e US$0.50/M de saída no console em 2026-10-28).
- **Alternativa: Jev via OpenRouter.** Troque no `.env`:
  `JEV_BASE_URL=https://openrouter.ai/api/v1/systemone`,
  `JEV_MODEL=typesafe/jev-1.13` e `JEV_API_KEY=<sua chave OpenRouter>`.
  Não há Jev free no OpenRouter: confira preço e disponibilidade no dia.

## Dicas desta pasta

- Os notebooks são auto-contidos: perguntas e pequenos trechos de código
  são duplicados de propósito. Ao mudar uma pergunta, replique nos outros
  para o placar continuar comparável.
- `JEV_MODEL` no `.env` manda: trocar de modelo não exige mexer no código.
  O `-free` é tempo limitado; `jev-1.13` é o fallback pago.
- O threshold é política, não modelo: mudar o número muda a fila de
  revisão sem uma chamada a mais ao gateway.
- No notebook 03, o modelo "mini" é o `LLM_MINI_MODEL`; trocar esse id
  muda a conta e a qualidade, não o roteiro.
