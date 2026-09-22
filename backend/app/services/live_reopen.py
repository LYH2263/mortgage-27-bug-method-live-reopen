import json
from app.engines.amortization import equal_payment_schedule
from app.modules import equal_principal
from app.repositories import settings


def current_default_method(conn) -> str:
    m = settings.get_map(conn).get("method") or "equal_payment"
    return m if m in ("equal_payment", "equal_principal") else "equal_payment"


def recompute_schedule_payload(conn, payload: dict) -> dict:
    principal = float(payload["principal"])
    annual_rate = float(payload["annual_rate"])
    months = int(payload["months"])
    method = current_default_method(conn)
    if method == equal_principal.METHOD:
        full = equal_principal.schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("first_payment", "last_payment", "total_interest", "total_payment")}
    else:
        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
    out["method"] = method
    preview_n = min(12, len(full.get("rows") or []))
    out["preview"] = full["rows"][:preview_n]
    out["row_count"] = len(full["rows"])
    return out


def refresh_run_on_open(conn, row: dict) -> dict:
    payload = json.loads(row.get("input_json") or "{}")
    fresh = recompute_schedule_payload(conn, payload)
    from app.repositories import runs

    runs.replace_result(conn, int(row["id"]), fresh)
    return fresh
