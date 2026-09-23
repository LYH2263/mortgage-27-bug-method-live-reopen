"""历史测算只读打开的回归测试：

钉选还款方式入库的历史记录，之后无论现行默认方式被改掉还是停用，
按编号重新打开都必须返回钉选时的 method、月供与利息合计，
且只读打开不得改写库里的结果。当场新测仍可按指定方式计算。
"""
import sqlite3

import pytest

import app.db
from app.services.mortgage_service import MortgageService

SCHEMA = """
CREATE TABLE loans(id INTEGER PRIMARY KEY, name TEXT, principal REAL, annual_rate REAL, months INTEGER);
CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE calc_runs(id INTEGER PRIMARY KEY, kind TEXT, loan_id INTEGER, input_json TEXT, result_json TEXT, created_at TEXT);
"""


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    monkeypatch.setattr(app.db, "DB_PATH", db_file)
    return db_file


def _stored_result_json(db_file, rid):
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT result_json FROM calc_runs WHERE id=?", (rid,)).fetchone()
    conn.close()
    return row[0]


def _persist(method):
    with MortgageService() as s:
        return s.schedule(1_000_000, 3.5, 360, None, True, method=method)


def test_reopen_keeps_pinned_equal_principal_after_default_changes(isolated_db):
    out = _persist("equal_principal")
    with MortgageService() as s:
        s.update_settings({"method": "equal_payment"})
        item = s.history_item(out["run_id"])
    assert item["method"] == "equal_principal"
    result = item["result"]
    assert result["method"] == "equal_principal"
    assert result["first_payment"] == out["first_payment"]
    assert result["last_payment"] == out["last_payment"]
    assert result["total_interest"] == out["total_interest"]
    assert "monthly_payment" not in result


def test_reopen_keeps_pinned_equal_payment_after_default_changes(isolated_db):
    out = _persist("equal_payment")
    with MortgageService() as s:
        s.update_settings({"method": "equal_principal"})
        item = s.history_item(out["run_id"])
    assert item["method"] == "equal_payment"
    result = item["result"]
    assert result["monthly_payment"] == out["monthly_payment"]
    assert result["total_interest"] == out["total_interest"]
    assert "first_payment" not in result


def test_reopen_survives_default_method_removed(isolated_db):
    out = _persist("equal_principal")
    conn = sqlite3.connect(isolated_db)
    conn.execute("DELETE FROM settings WHERE key='method'")
    conn.commit()
    conn.close()
    with MortgageService() as s:
        item = s.history_item(out["run_id"])
    assert item["method"] == "equal_principal"
    assert item["result"]["total_interest"] == out["total_interest"]


def test_reopen_does_not_rewrite_stored_result(isolated_db):
    out = _persist("equal_principal")
    before = _stored_result_json(isolated_db, out["run_id"])
    with MortgageService() as s:
        s.update_settings({"method": "equal_payment"})
        s.history_item(out["run_id"])
        s.history_item(out["run_id"])
    assert _stored_result_json(isolated_db, out["run_id"]) == before


def test_fresh_calc_follows_requested_method(isolated_db):
    _persist("equal_principal")
    with MortgageService() as s:
        s.update_settings({"method": "equal_payment"})
        fresh = s.schedule(1_000_000, 3.5, 360, None, True, method="equal_payment")
    assert fresh["method"] == "equal_payment"
    assert fresh["monthly_payment"] == 4490.45
