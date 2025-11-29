import hmac
import json
from hashlib import sha256
from typing import Any, Dict, Tuple
from urllib.parse import parse_qsl, unquote_plus

from app.config import settings


class TelegramInitDataError(Exception):
    pass


def _build_data_check_string(pairs: list[Tuple[str, str]]) -> str:
    # Exclude 'hash' and sort by key
    filtered = [(k, v) for k, v in pairs if k != "hash"]
    filtered.sort(key=lambda x: x[0])
    return "\n".join([f"{k}={v}" for k, v in filtered])


def verify_telegram_init_data(init_data: str) -> Dict[str, Any]:
    """
    Verify Telegram WebApp initData per official spec.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    Steps:
      1. Parse querystring-like 'init_data'
      2. Build data_check_string from all key=value pairs excluding 'hash', sorted by key, joined by newline
      3. Compute secret_key = sha256('WebAppData' + BOT_TOKEN)
      4. Compute HMAC_SHA256(data_check_string, secret_key) as hex lowercase
      5. Compare to provided 'hash' using hmac.compare_digest
    Returns the parsed payload including 'user' as a python dict if present.
    Raises TelegramInitDataError if invalid.
    """
    if not init_data:
        raise TelegramInitDataError("Empty init_data")

    pairs = parse_qsl(init_data, keep_blank_values=True)
    provided_hash = None
    for k, v in pairs:
        if k == "hash":
            provided_hash = v
            break

    if not provided_hash:
        raise TelegramInitDataError("Missing hash in init_data")

    data_check_string = _build_data_check_string(pairs)
    secret_key = sha256(("WebAppData" + settings.BOT_TOKEN).encode("utf-8")).digest()
    computed = hmac.new(secret_key, data_check_string.encode("utf-8"), sha256).hexdigest()

    if not hmac.compare_digest(computed, provided_hash):
        raise TelegramInitDataError("Invalid signature")

    # Parse payload into dict and decode 'user' JSON if present
    payload: Dict[str, Any] = {}
    for k, v in pairs:
        payload[k] = v

    # Telegram sends 'user' as a JSON string
    user_raw = payload.get("user")
    if isinstance(user_raw, str):
        try:
            # value may be urlencoded
            payload["user"] = json.loads(unquote_plus(user_raw))
        except Exception:
            # If cannot parse, keep raw
            pass

    return payload
