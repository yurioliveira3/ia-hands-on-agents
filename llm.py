# Ponto único de integração dos notebooks: TODAS as chamadas ao LLM
# passam daqui, portanto trocar de provedor é mexer apenas no .env.
# Este é o coração da tese da demo: o modelo é uma peça substituível,
# a engenharia vale por si.
import os
import random
import time
import uuid
from pathlib import Path

from openai import OpenAI, RateLimitError


def _load_env(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


# Carregar o .env antes de calcular o session id: assim LLM_SESSION_ID
# do arquivo vale também no import direto (sem --env-file).
_load_env(os.path.join(os.path.dirname(__file__), ".env"))

# OpenCode Go exige um id de sessão estável por conversa (header
# x-opencode-session); é o mesmo princípio do session_id de qualquer
# gateway: sem ele a infraestrutura não sabe rotear as chamadas.
# Um id por processo cobre a demo inteira (cada notebook é tratado
# como uma conversa). Sobrescreva com LLM_SESSION_ID no .env se quiser
# agrupar as rodadas do seu jeito.
_SESSION_ID = os.environ.get("LLM_SESSION_ID") or str(uuid.uuid4())

# Os dois headers abaixo são específicos do OpenCode Go: o session id
# roteia a conversa e o User-Agent próprio evita ser tratado como
# tráfego genérico de SDK. Outros provedores os ignoram; se algum
# rejeitar headers desconhecidos, filtre aqui antes de criar o client.
_DEFAULT_HEADERS = {
    "User-Agent": "podcast-demo/1.0",
    "x-opencode-session": _SESSION_ID,
}


def chat(
    messages: list[dict],
    temperature: float | None = None,
    top_p: float | None = None,
    max_tokens: int = 800,
) -> str:
    """Chamada agnóstica: qualquer endpoint compatível com o padrão OpenAI.

    Variáveis de ambiente (arquivo .env junto do llm.py):
      LLM_API_KEY   - chave do provedor
      LLM_BASE_URL  - base do endpoint
      LLM_MODEL     - nome do modelo

    Provedores e quotas (OpenCode Go, OpenRouter, Gemini, OpenAI):
    fonte única no .env.example - copie da lá, não daqui.

    Parâmetros de amostragem (tema de discussão da demo; o código deixa
    de usá-los quando None):
      temperature: 0.0 a 2.0. Controla a aleatoriedade. Zero é o valor
                   de trabalho para comparar execuções; valores altos
                   trocam repetibilidade por variedade.
      top_p: nucleus sampling (0.0 a 1.0). Descarta as palavras menos
             prováveis fora do núcleo de candidatos.
      top_k: limita as k palavras mais prováveis por passo. Nativo do
             Gemini; muitos provedores OpenAI-compat não o expõem.
    """
    faltando = [var for var in ("LLM_API_KEY", "LLM_MODEL") if not os.environ.get(var)]
    if faltando:
        raise RuntimeError(
            "Variáveis faltando: " + ", ".join(faltando) + ". "
            "Copie .env.example para .env, preencha e tente de novo "
            "(o arquivo fica na mesma pasta do llm.py)."
        )

    params: dict = {
        "model": os.environ["LLM_MODEL"],
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if temperature is not None:
        params["temperature"] = temperature
    if top_p is not None:
        params["top_p"] = top_p

    client = OpenAI(
        base_url=os.environ.get("LLM_BASE_URL") or None,
        api_key=os.environ["LLM_API_KEY"],
        default_headers=_DEFAULT_HEADERS,
    )

    for attempt in range(4):
        try:
            response = client.chat.completions.create(**params)
            break
        except RateLimitError:
            # 429 no free tier é parte da vida da demo, não uma exceção.
            # O backoff absorve os 429 transitórios; se persistir após as
            # 4 tentativas, a exceção sobe para o chamador.
            if attempt == 3:
                raise
            wait = 15 * (attempt + 1) + random.uniform(0, 3)
            print(f"(rate limit; aguardando {wait:.0f}s antes de tentar de novo)")
            time.sleep(wait)

    choice = response.choices[0]
    content = choice.message.content
    if not content:
        # Modelos 'thinking' alocam parte de max_tokens para raciocínio
        # interno antes de escrever. Quando o orçamento estoura antes
        # da escrita, content volta vazio com finish_reason=length.
        raise RuntimeError(
            f"Resposta vazia do modelo (finish_reason={choice.finish_reason}). "
            "Provavelmente max_tokens baixo com modelo thinking: aumente o valor "
            "(ou use um modelo sem thinking)."
        )
    return content
