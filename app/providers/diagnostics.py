"""Small, explicit allowlist for provider metadata; never retain response bodies."""
import re

FINISH_REASONS = {"stop", "length", "content_filter", "tool_calls", "function_call"}
ERROR_CODES = {
    "PROVIDER_NOT_CONFIGURED", "PROVIDER_AUTH_ERROR", "PROVIDER_RATE_LIMITED",
    "PROVIDER_HTTP_ERROR", "PROVIDER_TIMEOUT", "PROVIDER_RESPONSE_LIMIT",
    "PROVIDER_INVALID_RESPONSE", "PROVIDER_INCOMPLETE_OUTPUT",
}


def safe_diagnostics(values):
    result = {}
    for key, maximum in {"http_status": 599, "input_tokens": 10_000_000,
                         "output_tokens": 10_000_000, "latency_ms": 3_600_000,
                         "attempt": 2}.items():
        value = values.get(key)
        minimum = 100 if key == "http_status" else 1 if key == "attempt" else 0
        if type(value) is int and minimum <= value <= maximum:
            result[key] = value
    if isinstance(values.get("finish_reason"), str) and values["finish_reason"] in FINISH_REASONS:
        result["finish_reason"] = values["finish_reason"]
    request_id = values.get("request_id")
    if isinstance(request_id, str) and re.fullmatch(r"[\w.:/-]{1,160}", request_id, re.ASCII):
        result["request_id"] = request_id
    return result
