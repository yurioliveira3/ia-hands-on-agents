# Ponto único de integração dos notebooks: TODAS as chamadas ao LLM
# passam daqui, portanto trocar de provedor é mexer apenas no .env.
# Este é o coração da tese da demo: o modelo é uma peça substituível,
# a engenharia vale por si.
import os
import random
import time
import uuid
from pathlib import Path

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    NotFoundError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)


def _limpar_valor(valor: str) -> str:
    valor = valor.strip()
    if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
        return valor[1:-1]
    return valor


def _load_env(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), _limpar_valor(value))


def _env(nome: str) -> str:
    return _limpar_valor(os.environ.get(nome, ""))


# Carregar o .env antes de calcular o session id: assim LLM_SESSION_ID
# do arquivo vale também no import direto (sem --env-file).
_load_env(os.path.join(os.path.dirname(__file__), ".env"))

# OpenCode Go exige um id de sessão estável por conversa (header
# x-opencode-session); é o mesmo princípio do session_id de qualquer
# gateway: sem ele a infraestrutura não sabe rotear as chamadas.
# Um id por processo cobre a demo inteira (cada notebook é tratado
# como uma conversa). Sobrescreva com LLM_SESSION_ID no .env se quiser
# agrupar as rodadas do seu jeito.
_SESSION_ID = _env("LLM_SESSION_ID") or str(uuid.uuid4())

# Os dois headers abaixo são específicos do OpenCode Go: o session id
# roteia a conversa e o User-Agent próprio evita ser tratado como
# tráfego genérico de SDK. Outros provedores os ignoram; se algum
# rejeitar headers desconhecidos, filtre aqui antes de criar o client.
_DEFAULT_HEADERS = {
    "User-Agent": "podcast-demo/1.0",
    "x-opencode-session": _SESSION_ID,
}

_USAGE_TOTAL = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
_LAST_USAGE: dict | None = None


def _registrar_uso(usage) -> None:
    global _LAST_USAGE
    if usage is None:
        _LAST_USAGE = None
        return
    _LAST_USAGE = {
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
        "total_tokens": getattr(usage, "total_tokens", 0) or 0,
    }
    for chave, valor in _LAST_USAGE.items():
        _USAGE_TOTAL[chave] += valor


def last_usage() -> dict | None:
    """Tokens da última chamada, ou None se o provedor não informou."""
    return dict(_LAST_USAGE) if _LAST_USAGE else None


def usage_total() -> dict:
    """Tokens acumulados neste processo (todas as chamadas de chat)."""
    return dict(_USAGE_TOTAL)


def chat(
    messages: list[dict],
    temperature: float | None = None,
    top_p: float | None = None,
    max_tokens: int = 1200,
) -> str:
    """Chamada agnóstica: qualquer endpoint compatível com o padrão OpenAI.

    Variáveis de ambiente (arquivo .env junto do llm.py):
      LLM_API_KEY   - chave do provedor
      LLM_BASE_URL  - base do endpoint
      LLM_MODEL     - nome do modelo

    Provedores e quotas (OpenCode Go, OpenRouter, Gemini, OpenAI):
    detalhes no .env.example e na seção "Chaves de API" do README.

    Parâmetros de amostragem (tema de discussão da demo; o código deixa
    de usá-los quando None):
      temperature: 0.0 a 2.0. Controla a aleatoriedade. Zero é o valor
                   de trabalho para comparar execuções; valores altos
                   trocam repetibilidade por variedade.
      top_p: nucleus sampling (0.0 a 1.0). Descarta as palavras menos
             prováveis fora do núcleo de candidatos. top_k não é
             parâmetro desta função: o endpoint OpenAI-compat não o
             expõe; a discussão fica no notebook 02.

    O consumo fica disponível em last_usage() (última chamada) e em
    usage_total() (acumulado do processo); ambos vêm do campo usage da
    resposta, quando o provedor o envia.
    """
    faltando = [var for var in ("LLM_API_KEY", "LLM_MODEL") if not _env(var)]
    if faltando:
        raise RuntimeError(
            "Variáveis faltando: " + ", ".join(faltando) + ". "
            "Copie .env.example para .env, preencha e tente de novo "
            "(o arquivo fica na mesma pasta do llm.py). "
            "Para criar uma chave free, veja 'Chaves de API' no README."
        )

    params: dict = {
        "model": _env("LLM_MODEL"),
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if temperature is not None:
        params["temperature"] = temperature
    if top_p is not None:
        params["top_p"] = top_p

    client = OpenAI(
        base_url=_env("LLM_BASE_URL") or None,
        api_key=_env("LLM_API_KEY"),
        default_headers=_DEFAULT_HEADERS,
    )

    for attempt in range(4):
        try:
            response = client.chat.completions.create(**params)
            break
        except RateLimitError as exc:
            # 429 no free tier é parte da vida da demo, não uma exceção.
            # O backoff absorve os 429 transitórios; se persistir após as
            # 4 tentativas, vira um RuntimeError com orientação.
            if attempt == 3:
                raise RuntimeError(
                    "Rate limit persistente após 4 tentativas. Aguarde e "
                    "tente de novo ou troque de modelo/provedor (as opções "
                    "free estão no .env.example)."
                ) from exc
            wait = 15 * (attempt + 1) + random.uniform(0, 3)
            print(f"(rate limit; aguardando {wait:.0f}s antes de tentar de novo)")
            time.sleep(wait)
        except AuthenticationError as exc:
            raise RuntimeError(
                "Chave recusada pelo provedor (401). Confira LLM_API_KEY no "
                ".env e se ela pertence ao provedor de LLM_BASE_URL."
            ) from exc
        except PermissionDeniedError as exc:
            raise RuntimeError(
                "A chave foi aceita, mas não tem permissão para este modelo "
                "(403). Confira LLM_MODEL e as permissões da conta no provedor."
            ) from exc
        except APIConnectionError as exc:
            raise RuntimeError(
                "Não foi possível conectar ao provedor. Confira LLM_BASE_URL "
                "no .env (inclua o path /v1 quando o provedor exigir) e sua "
                "conexão."
            ) from exc
        except NotFoundError as exc:
            raise RuntimeError(
                "Endpoint ou modelo não encontrado (404). Confira LLM_BASE_URL "
                "e LLM_MODEL no .env; o path do endpoint muda entre provedores."
            ) from exc
        except APIStatusError as exc:
            raise RuntimeError(
                f"O provedor respondeu HTTP {exc.status_code}. Confira "
                "LLM_BASE_URL, LLM_MODEL e LLM_API_KEY no .env; a mensagem "
                "original do provedor está na causa desta exceção."
            ) from exc

    _registrar_uso(getattr(response, "usage", None))

    choice = response.choices[0]
    content = choice.message.content
    finish = choice.finish_reason
    if finish == "length":
        # Modelos 'thinking' alocam parte de max_tokens para raciocínio
        # interno antes de escrever. O content pode vir vazio ou
        # parcial; nos dois casos a resposta está truncada e não serve
        # para o laço (um JSON de ação pela metade, por exemplo).
        raise RuntimeError(
            f"Resposta truncada (finish_reason=length, max_tokens={max_tokens}). "
            "Aumente max_tokens ou use um modelo sem thinking."
        )
    if not content:
        raise RuntimeError(
            f"Resposta vazia do modelo (finish_reason={finish}). "
            "Confira o provedor e tente de novo."
        )
    return content
