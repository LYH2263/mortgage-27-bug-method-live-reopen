import json
import os
import tempfile

# 在导入任何会读取 app.config 的模块之前，把数据目录指到临时目录，保证测试隔离。
os.environ["DATA_DIR"] = tempfile.mkdtemp()

import pytest

from app.db import connect
from app.seed import init_db
from app.services.mortgage_service import MortgageService
from app.repositories import runs as runs_repo
from app.engines.amortization import equal_payment_schedule, equal_principal_schedule


@pytest.fixture()
def svc():
    init_db()
    with MortgageService() as s:
        yield s


def _raw_result(rid):
    conn = connect()
    try:
        return conn.execute("SELECT result_json FROM calc_runs WHERE id=?", (rid,)).fetchone()[0]
    finally:
        conn.close()


def test_open_principal_run_keeps_pinned_method_when_default_is_payment(svc):
    created = svc.schedule(1_000_000, 3.5, 360, None, True, method="equal_principal")
    rid = created["run_id"]
    expected = equal_principal_schedule(1_000_000, 3.5, 360)

    # 现行默认还款方式改成等额本息（旧记录的方式相当于已被换掉）。
    svc.update_settings({"method": "equal_payment"})

    raw_before = _raw_result(rid)
    item = svc.history_item(rid)
    raw_after = _raw_result(rid)

    assert item["method"] == "equal_principal"
    assert item["result"]["method"] == "equal_principal"
    assert item["result"]["first_payment"] == expected["first_payment"]
    assert item["result"]["last_payment"] == expected["last_payment"]
    assert item["result"]["total_interest"] == expected["total_interest"]
    assert "monthly_payment" not in item["result"]
    # 只读打开不得改写库里的结果。
    assert raw_after == raw_before


def test_open_payment_run_keeps_payment_when_default_is_principal(svc):
    created = svc.schedule(1_000_000, 3.5, 360, None, True, method="equal_payment")
    rid = created["run_id"]
    expected = equal_payment_schedule(1_000_000, 3.5, 360)

    svc.update_settings({"method": "equal_principal"})

    raw_before = _raw_result(rid)
    item = svc.history_item(rid)
    raw_after = _raw_result(rid)

    assert item["method"] == "equal_payment"
    assert item["result"]["method"] == "equal_payment"
    assert item["result"]["monthly_payment"] == expected["monthly_payment"]
    assert item["result"]["total_interest"] == expected["total_interest"]
    assert "first_payment" not in item["result"]
    assert raw_after == raw_before


def test_history_list_and_detail_share_pinned_method_and_totals(svc):
    created = svc.schedule(800_000, 4.0, 240, None, True, method="equal_principal")
    rid = created["run_id"]
    svc.update_settings({"method": "equal_payment"})

    rows = {h["id"]: h for h in svc.history(100)}
    item = svc.history_item(rid)

    assert rows[rid]["method"] == "equal_principal"
    assert item["method"] == "equal_principal"
    assert rows[rid]["total_interest"] == item["result"]["total_interest"]


def test_open_does_not_mutate_result_even_with_repeated_views(svc):
    created = svc.schedule(500_000, 3.0, 120, None, True, method="equal_principal")
    rid = created["run_id"]
    svc.update_settings({"method": "equal_payment"})

    raw_before = _raw_result(rid)
    first = svc.history_item(rid)
    second = svc.history_item(rid)

    assert first["result"] == second["result"] == json.loads(raw_before)
    assert _raw_result(rid) == raw_before


def test_fresh_calculation_follows_current_method(svc):
    # 当场新测仍按传入（现行）方式计算，历史只读路径的修复不影响新测。
    svc.update_settings({"method": "equal_principal"})
    out = svc.schedule(1_000_000, 3.5, 360, None, False, method="equal_principal")
    assert out["method"] == "equal_principal"
    assert out["first_payment"] == equal_principal_schedule(1_000_000, 3.5, 360)["first_payment"]
