import json
from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.modules import equal_principal
from app.repositories import loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def update_settings(self, values):
        for k, v in values.items(): settings.set_value(self._c, k, v)
        return settings.get_map(self._c)
    def history(self, limit=50):
        return [self._run_summary(r) for r in runs.list_recent(self._c, limit)]
    def history_item(self, rid):
        row = runs.get(self._c, rid)
        if not row: return None
        item = self._run_summary(row)
        item["input"] = _loads(row.get("input_json"))
        # 只读打开：原样返回落库时钉选的方式与结果，不按现行默认方式重算，也不回写数据库。
        item["result"] = _loads(row.get("result_json"))
        return item
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, method="equal_payment"):
        if method == equal_principal.METHOD:
            full = equal_principal.schedule(principal, annual_rate, months)
            out = {k: full[k] for k in ("first_payment", "last_payment", "total_interest", "total_payment")}
        else:
            full = equal_payment_schedule(principal, annual_rate, months)
            out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["method"] = method
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", {"principal": principal, "annual_rate": annual_rate, "months": months, "method": method}, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
    @staticmethod
    def _run_summary(row):
        item = dict(row)
        result = _loads(item.get("result_json"))
        payload = _loads(item.get("input_json"))
        item["method"] = payload.get("method") or result.get("method") or "equal_payment"
        item["total_interest"] = result.get("total_interest")
        return item

def _loads(text):
    try: return json.loads(text or "{}")
    except (TypeError, ValueError): return {}
