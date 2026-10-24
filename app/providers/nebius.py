"""Nebius chat-completions transport, implemented independently for MatterGate."""
import hashlib
import asyncio
import html
import json
import time

import httpx

from app.config import ROOT
from app.domain import DISCLOSURE, CitedDraft, parse_draft
from app.providers.base import DraftResult, ModelUnavailable, validate_context
from app.providers.diagnostics import safe_diagnostics

SYSTEM = (ROOT / "providers/prompt.txt").read_text()
PROMPT_HASH = hashlib.sha256(SYSTEM.encode()).hexdigest()


def messages(request, scope, evidence):
    validate_context(request, scope, evidence)
    excerpts = "\n".join(f'<evidence chunk_id="{html.escape(item.chunk_id,quote=True)}" source_id="{html.escape(item.source_id,quote=True)}" classification="{html.escape(item.classification,quote=True)}">\nUNTRUSTED REFERENCE CONTENT START\n{html.escape(item.text)}\nUNTRUSTED REFERENCE CONTENT END\n</evidence>' for item in evidence)
    system = SYSTEM+"\nSCHEMA: "+json.dumps(CitedDraft.model_json_schema())+"\nDISCLAIMER: "+DISCLOSURE
    user = json.dumps({"question":request.question,"jurisdiction":request.jurisdiction,"matter":request.matter_id})+"\n"+excerpts
    return [{"role":"system","content":system},{"role":"user","content":user}]


class NebiusProvider:
    def __init__(self, settings, transport=None):
        self.settings = settings
        self.transport = transport

    def generate_draft(self, *, request, scope, evidence, on_attempt=None):
        prompt = messages(request,scope,evidence)
        if not self.settings.live_ready:
            raise ModelUnavailable("PROVIDER_NOT_CONFIGURED")
        diagnostics = {}
        started = time.monotonic()
        try:
            return asyncio.run(self._within_deadline(prompt, diagnostics, on_attempt))
        except (TimeoutError, httpx.TimeoutException):
            diagnostics["latency_ms"] = int((time.monotonic()-started)*1000)
            raise ModelUnavailable("PROVIDER_TIMEOUT", diagnostics) from None
        except ModelUnavailable as error:
            diagnostics["latency_ms"] = int((time.monotonic()-started)*1000)
            raise ModelUnavailable(str(error), diagnostics) from None

    async def _within_deadline(self, prompt, diagnostics, on_attempt):
        # One cancellable wall-clock budget covers connection, reads and repair.
        async with asyncio.timeout(self.settings.timeout):
            return await self._generate(prompt, diagnostics, on_attempt)

    async def _generate(self, prompt, diagnostics, on_attempt):
        start = time.monotonic()
        deadline = start+self.settings.timeout
        request_id = None
        for attempt in range(2):
            diagnostics.clear()
            diagnostics["attempt"] = attempt+1
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise ModelUnavailable("PROVIDER_TIMEOUT")
            try:
                # No redirects, environment proxies, raw logging or disabled TLS verification.
                async with httpx.AsyncClient(timeout=remaining, follow_redirects=False, trust_env=False, transport=self.transport) as client:
                    if on_attempt:
                        on_attempt(attempt+1)
                    async with client.stream("POST", self.settings.base_url+"/chat/completions",
                        headers={"Authorization":"Bearer "+self.settings.api_key},
                        json={"model":self.settings.model,"messages":prompt,"temperature":self.settings.temperature,
                              "max_tokens":self.settings.max_tokens,"stream":False,
                              # NVIDIA's Nemotron 3 chat template supports disabling thinking.
                              # Keep the bounded output budget available for the JSON brief.
                              **({"chat_template_kwargs":{"enable_thinking":False}}
                                 if self.settings.model.lower() in {
                                     "nvidia/nemotron-3_5-lightning",
                                     "nvidia/nemotron-3-super-120b-a12b",
                                 } else {})}) as response:
                        diagnostics["http_status"] = response.status_code
                        header_id = response.headers.get("x-request-id")
                        diagnostics.update(safe_diagnostics({"request_id":header_id}))
                        if response.status_code != 200:
                            code = "PROVIDER_AUTH_ERROR" if response.status_code in {401,403} else "PROVIDER_RATE_LIMITED" if response.status_code == 429 else "PROVIDER_HTTP_ERROR"
                            raise ModelUnavailable(code)
                        chunks, size = [], 0
                        async for chunk in response.aiter_bytes():
                            size += len(chunk)
                            if size > 100000 or time.monotonic() >= deadline:
                                raise ModelUnavailable("PROVIDER_RESPONSE_LIMIT")
                            chunks.append(chunk)
                        body = json.loads(b"".join(chunks))
                        if not isinstance(body,dict):
                            raise ModelUnavailable("PROVIDER_INVALID_RESPONSE")
                        candidate = body.get("id") or response.headers.get("x-request-id")
                        request_id = safe_diagnostics({"request_id":candidate}).get("request_id")
                        usage = body.get("usage") or {}
                        choice = body["choices"][0]
                        if not isinstance(choice,dict) or not isinstance(usage,dict):
                            raise ModelUnavailable("PROVIDER_INVALID_RESPONSE")
                        diagnostics.update(safe_diagnostics({"request_id":request_id,
                            "finish_reason":choice.get("finish_reason"),
                            "input_tokens":usage.get("prompt_tokens"),"output_tokens":usage.get("completion_tokens")}))
                        print(
                            "Nebius completion:",
                            diagnostics.get("finish_reason","unavailable"),
                            "output_tokens:", diagnostics.get("output_tokens","unavailable"),
                            flush=True,
                        )
                        if choice.get("finish_reason") != "stop":
                            raise ModelUnavailable("PROVIDER_INCOMPLETE_OUTPUT")
                        raw = choice["message"]["content"]
                if not isinstance(raw,str):
                    raise ModelUnavailable("PROVIDER_INVALID_RESPONSE")
            except httpx.TimeoutException:
                raise ModelUnavailable("PROVIDER_TIMEOUT") from None
            except (httpx.HTTPError, KeyError, IndexError, TypeError, json.JSONDecodeError):
                raise ModelUnavailable("PROVIDER_INVALID_RESPONSE") from None
            try:
                parse_draft(raw)
                return DraftResult(raw,"nebius",self.settings.model,request_id,int((time.monotonic()-start)*1000),safe_diagnostics(diagnostics))
            except ValueError:
                if attempt == 0:
                    prompt = [prompt[0], {"role":"system","content":"The previous generation was malformed. Regenerate JSON strictly matching the schema. Do not add prose or markdown."}, prompt[-1]]
                else:
                    # Let the application parser record the failed schema controls.
                    return DraftResult(raw,"nebius",self.settings.model,request_id,int((time.monotonic()-start)*1000),safe_diagnostics(diagnostics))
