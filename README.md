# IA Hands-on: da engenharia de prompt ao agente

Material prático, nascido de uma sessão ao vivo e pensado para ser
re-executado pelo dev: da engenharia de prompt ao agente, visto por
dentro, com dados de verdade.

**Atalhos:** [Setup](#setup) · [Passo a passo](#passo-a-passo) ·
[Síntese por camada](#síntese-por-camada) · [Referências](#referências)
— ou vá direto a uma demo:

| Demo | O que você encontra | Comece por |
|---|---|---|
| [Demo 1](demo-1/) — da engenharia de prompt ao agente | 4 notebooks: zero-shot, few-shot, laço do agente à mão e evals | [01_zero_shot.ipynb](demo-1/01_zero_shot.ipynb) |
| [Demo 2](demo-2/) — top-3 MCPs criando e lendo em destinos | roteiro guiado + prompts em 3 níveis: [simples](demo-2/prompts/prompt-simples.md), [médio](demo-2/prompts/prompt-medio.md) e [avançado](demo-2/prompts/prompt-avancado.md) | [roteiro-demo-2.md](demo-2/roteiro-demo-2.md) |

Tese central: o modelo é uma peça substituível - trocar de provedor é
editar três linhas do .env; a engenharia que permanece é prompt,
exemplos, ferramentas e avaliação.

Cada notebook é auto-contido: rode na ordem, pule para o que interessar
ou vá direto às intervenções "Experimente".

## O mapa das camadas

Todo o material cabe nestas caixas aninhadas (adaptado do diagrama
"agentic delivery system" do ecossistema de agentes; a versão à frente
usa os nomes das nossas camadas):

![Mapa de camadas do hands-on](diagramas/01-camadas.svg)

| Camada do desenho | Onde aparece | Arquivo |
|---|---|---|
| Engenharia de contexto (teal) | zero-shot (camada 1) e few-shot (camada 2): tudo que entra na janela do modelo | [demo-1/01](demo-1/01_zero_shot.ipynb), [demo-1/02](demo-1/02_few_shot.ipynb) |
| Laço do agente | o run_agent à mão: decidir, agir, observar, responder | [demo-1/03](demo-1/03_agent_loop.ipynb) |
| Orquestração | ferramentas coordenadas por um catálogo padrão (MCP): filesystem, sqlite, fetch | [demo-2](demo-2/roteiro-demo-2.md) |
| Armação (harness) | a CLI do agente que conecta tudo: Claude Code ou OpenCode, permissões, segredos | [demo-2/.mcp.json](demo-2/.mcp.json.example), [demo-2/opencode.json](demo-2/opencode.json.example), [.env](.env.example) |
| Envelope (evals, custo) | como saber que funciona sem achar: suíte com gabarito e tokens por execução | [demo-1/bonus_evals](demo-1/bonus_evals.ipynb) |

### A lógica de dentro para fora

1. **Contexto** é tudo que o dev escreve na janela: prompt, exemplos,
   parâmetros. As camadas 1 e 2 mostram o placar mudar só com isso.
2. **Laço** é o que o agente faz a cada volta: um JSON de ação, uma
   tool executada, o resultado voltando como mensagem, até o answer.
3. **Orquestração** é quando as ferramentas não são mais as suas: um
   catálogo padrão (MCP) entrega o filesystem, o banco e a rede.
4. **Armação** é a casa: a CLI do agente, as permissões, o .env com as
   chaves, o custo por chamada.
5. **Envelope** é o julgamento: avaliar contra um gabarito e repetir
   para medir repetibilidade (a camada bônus).

### O laço do agente (camada 3) em um grafo

![Laço do agente](diagramas/02-laco-do-agente.svg)

O `max_steps=6` do run_agent é a trava para nunca girar de verdade:
sem framework, mas com freio (aponta no desenho).

## Critério de parada: quando a chamada continua, quando para

Terminar no lugar certo é parte do design. No material, a parada
acontece em quatro níveis - e todos são visíveis (nenhum escondido
dentro de framework):

| Nível | Quem decide | Onde ler no código |
|---|---|---|
| O modelo decide acabou | o turno com `{"answer": ...}` encerra o laço; só uma `tool` gera a próxima volta | [demo-1/03](demo-1/03_agent_loop.ipynb), `run_agent`: `if 'answer' in acao: return` |
| O freio (guardrail) | o teto de voltas protege do agente perdido; estourou, devolve `'(limite de passos atingido)'` | [demo-1/03](demo-1/03_agent_loop.ipynb), `run_agent(..., max_steps=6)` |
| A resposta em si | `finish_reason` da API: `stop` concluiu; `length` = orçamento de tokens estourou (o `llm.py` levanta erro mesmo com conteúdo parcial) | [llm.py](llm.py), bloco `finish_reason` |
| A infraestrutura | 429 do free tier: até 4 tentativas com backoff; persistindo, o erro sobe | [llm.py](llm.py), bloco retry |

A intuição que vale levar: o custo da parada errada é assimétrico.
Parar cedo demais entrega resposta vazia; parar tarde demais entrega
conta (tokens e giros). O `max_steps` nunca é conveniência: é política
de custo.

### Um dado, dois destinos locais e um externo (demo 2)

![Um dado, dois destinos locais e um externo](diagramas/03-um-dado-tres-destinos.svg)

## Estrutura

```
podcast-ia-hands-on/
  Makefile                setup re-executavel: make setup/env/test/notebooks/evals/demo2-config
                          clean remove os artefatos gerados
  pyproject.toml          dependencias declaradas (gerenciadas pelo uv)
  uv.lock                 lock das dependencias (instalacao reprodutivel)
  llm.py                  helper agnóstico (padrão OpenAI-compat) + retry 429
  .env.example            template de credenciais -> copie para .env
  LICENSE                 MIT: replique, teste e faça fork à vontade
  data/reclamacoes.csv    dataset de demo (18 linhas, 5 categorias)
  diagramas/              os 3 SVGs deste README (mesmo padrão visual)
  demo-1/                 Demo 1 - da engenharia de prompt ao agente
    01_zero_shot.ipynb    camada 1: classificador zero-shot, falha ao vivo
    02_few_shot.ipynb     camada 2: poucos exemplos + tuning de amostragem
    03_agent_loop.ipynb   camada 3: o laço do agente escrito à mão
    bonus_evals.ipynb     camada 5 (bônus): eval-driven development
  demo-2/                 Demo 2 - top-3 MCPs criando e lendo em destinos
    .mcp.json.example     template dos 3 servers MCP para Claude Code
    opencode.json.example template equivalente para OpenCode
    roteiro-demo-2.md     passo a passo da demonstração ao vivo
    prompts/              o roteiro em 3 níveis: simples, medio e avancado
```

Todos os notebooks e arquivos citados estão linkados nas tabelas
[mapa de camadas](#o-mapa-das-camadas) e
[passo a passo](#passo-a-passo).

## Setup

### Chaves de API: onde criar e o que é free

O material aceita qualquer endpoint compatível com OpenAI. Para começar
sem custo, use uma chave free de OpenRouter ou Gemini; OpenAI e OpenCode
Go são opções pagas.

| Provedor | Onde criar a chave | Free? |
|---|---|---|
| OpenRouter | https://openrouter.ai/settings/keys | Sim: modelos com sufixo `:free`, sujeitos a rate limit |
| Gemini | https://aistudio.google.com/api-keys | Sim: free tier com quota; veja https://ai.google.dev/gemini-api/docs/rate-limits |
| OpenCode Go | https://opencode.ai/console | Não: o plano Go é pago (US$10/mês na data deste material); o modelo `-free` tem limite de uso |
| OpenAI | https://platform.openai.com/api-keys | Não: a API é cobrada por token |

Tudo via `make`, com dependências gerenciadas pelo `uv` (Python 3.10+
instalado automaticamente se necessário). Para instalar o `uv` (se não
tiver): `curl -LsSf https://astral.sh/uv/install.sh | sh`.

1. Preparar o ambiente (cria `.venv` e instala do lock):
   ```
   make setup
   ```
2. Criar o `.env` a partir do template (não sobrescreve um existente)
   e preencher:
   ```
   make env
   ```
   - `LLM_API_KEY` - chave do provedor
   - `LLM_MODEL` - nome do modelo
   - `LLM_BASE_URL` - base do endpoint (padrão OpenAI-compatible)
   - OpenCode Go (recomendado):
     `https://opencode.ai/inference/go/openai/v1/` com um modelo free
     (ex.: `minimax-m3.1-flash-free`). O plano Go é pago (US$10/mês na
     data deste material) e o modelo free tem limite de uso; confira a
     oferta atual no console.
   - OpenRouter: `https://openrouter.ai/api/v1/` com um modelo `:free`
     (a lista muda com frequência: ver https://openrouter.ai/models)
   - Gemini free: `https://generativelanguage.googleapis.com/v1beta/openai/`
     com `gemini-2.5-flash-lite` (~1.000 req/dia no free tier; evite os
     flash "padrão", ~20 req/dia e trava no meio do roteiro)
   - OpenAI: `https://api.openai.com/v1/`
3. Testar o caminho feliz (consome uma chamada pequena):
   ```
   make test
   ```
4. Abrir os notebooks (demo 1):
   ```
   make notebooks
   ```
5. Rodar a suíte de evals com gabarito (gasta chamadas da API por
   design; o alvo executa as duas suítes, 22 chamadas - 11 casos x 2
   prompts; sai em `export/bonus_evals.ipynb`):
   ```
   make evals
   ```
6. Para a demo 2: Node.js 20+ com npx (o server filesystem está
   pinado em `1.0.0`; a linha `2.0.0` exige Node 24) e os servers
   Python, um pacote por comando:
   ```
   uv tool install mcp-server-fetch
   uv tool install mcp-server-sqlite
   ```
   Os comandos `mcp-server-fetch` e `mcp-server-sqlite` precisam estar
   no PATH (o `uv tool` instala em `~/.local/bin`; confira com `which`).
   Gerar os configs e a cópia local do CSV:
   ```
   make demo2-config
   ```
   O target escreve `demo-2/.mcp.json` (Claude Code) e
   `demo-2/opencode.json` (OpenCode) com o caminho absoluto da sua
   pasta, e copia `data/reclamacoes.csv` para `demo-2/`.
   No Claude Code, confira com `/mcp`; no OpenCode, com
   `opencode mcp list`. Se já houver uma sessão OpenCode aberta na raiz
   do repo, inicie com `opencode --standalone` na pasta demo-2: o
   serviço compartilhado pode ficar ancorado na raiz e não carregar o
   `opencode.json` local.

## Passo a passo

Siga na ordem; cada passo depende só do setup e do `.env`.

| Passo | Notebook | O que acontece | Experimente |
|---|---|---|---|
| 1. Zero-shot | [demo-1/01](demo-1/01_zero_shot.ipynb) | classificador sem exemplos: erra as armadilhas | trocar o índice de uma linha no CSV e reexecutar |
| 2. Few-shot | [demo-1/02](demo-1/02_few_shot.ipynb) | 4 âncoras mudam o placar; o erro do índice 16 resiste | comentar uma âncora e comparar o placar |
| 2b. Tuning de amostragem | [demo-1/02](demo-1/02_few_shot.ipynb) | 2 configs x 3 rodadas: parâmetros não consertam | trocar temp=1.0 por top_p=0.5 e comparar |
| 2c. Exemplo novo | [demo-1/02](demo-1/02_few_shot.ipynb) | a intervenção que faltava: um quinto exemplo + regra para o índice 16 | comparar o placar de 15/16/17 |
| 3. Agente à mão | [demo-1/03](demo-1/03_agent_loop.ipynb) | o laço decidir/agir/observar sem framework | perguntar outra coisa que use a terceira tool (Wikipedia) |
| 4. Evals (bônus) | [demo-1/bonus_evals](demo-1/bonus_evals.ipynb) | suíte com gabarito: score por prompt | trocar uma âncora e comparar os dois scores |
| 5. MCP | [demo-2](demo-2/roteiro-demo-2.md) | o dado criado, gravado e relido; o fetch soma um externo | subir no Claude Code/OpenCode e trocar a pergunta |

Os índices citados são posições 0-based do DataFrame usado no notebook
(`df.iloc`). No arquivo CSV, a linha física é o índice + 2 (por causa do
cabeçalho); o índice 15, por exemplo, é a linha 17 do arquivo.

Resultado empírico observado (os números variam com o modelo; o output
do notebook registra o modelo usado):
- índices 15 e 16 do DataFrame: armadilhas multimotivo; zero-shot erra os dois;
- índices 15 e 17: consertam de forma estável com a regra e as 4 âncoras;
- índice 16: propositalmente sem âncora - o tuning de amostragem não
  salva (placar 6/9 em qualquer configuração). A intervenção é um
  exemplo novo e uma regra explícita; a seção "Intervenção: um
  exemplo novo para o índice 16", no notebook 02, deixa a comparação
  pronta para rodar no seu modelo. É a lição central da camada 2.
- suíte de evals: zero-shot 82%, few-shot 91% (11 casos); o índice 16
  segue errado nos dois.

## Dicas de execução

- O `llm.py` já faz retry com backoff no 429 - a mensagem de espera em
  tela é conteúdo, não bug ("quotas são reais").
- `exec_python` roda código gerado pelo modelo no seu processo, sem
  sandbox; use ambiente descartável e não deixe dados sensíveis ao
  alcance.
- O custo aparece em tokens: `last_usage()` mostra a última chamada e
  `usage_total()` o acumulado; multiplique pelo preço do provedor.
- Os prompts de `01`, `02` e `bonus_evals` são duplicados de propósito
  para cada notebook ser auto-contido; ao mudar um, replique nos outros
  para manter o placar comparável.
- Tudo roda localmente, exceto a API de LLM; a demo 1/03 consulta a
  Wikipédia e a demo 2 usa os servers MCP (filesystem via npx, fetch e
  sqlite locais).

## Síntese por camada

1. Zero-shot: o modelo não é mágica, é um prompt. Quando erra, o
   conserto não é trocar de modelo - é dar mais contexto.
2. Few-shot: quatro exemplos custam quatro linhas e mudam o placar.
   Dados de qualidade vencem modelo maior quase sempre.
3. Agente: o laço decidir, agir via ferramenta, observar, repetir é
   todo o segredo; qualquer framework é uma variação disso.
4. MCP: configurar em minutos o que à mão custa semanas; o protocolo
   padroniza a parte chata - inclusive o teste de integração.
5. Evals: como saber que funciona sem achismo? Rode a suíte: o TDD do
   mundo não-determinístico.

## Referências

- Anthropic. **Prompting best practices.**
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  Base para instruções claras, exemplos few-shot e tags XML usados nos notebooks 01 e 02.
- Anthropic. **Tool use with Claude.**
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
  Explica o ciclo `tool_use`/`tool_result` e o laço que o notebook 03 implementa à mão.
- OpenAI. **Function calling.**
  https://developers.openai.com/api/docs/guides/function-calling
  Referência para declarar ferramentas com JSON Schema e devolver o resultado ao modelo.

## Licença

MIT: use, replique, teste e faça fork à vontade. O aviso de copyright
da licença MIT deve ser mantido; créditos são bem-vindos.
