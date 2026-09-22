import pytest
from app.engines.amortization import equal_payment_schedule, equal_principal_schedule

def test_monthly_payment():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["monthly_payment"] == 4490.45

def test_first_period_interest():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][0]["period"] == 1

def test_zero_rate():
    s = equal_payment_schedule(120000, 0, 12)
    assert s["monthly_payment"] == 10000.0

def test_bad_months():
    with pytest.raises(ValueError):
        equal_payment_schedule(100, 3, 0)

def test_ep_first_and_last_payment():
    s = equal_principal_schedule(1_000_000, 3.5, 360)
    assert s["first_payment"] == 5694.44
    assert s["last_payment"] == 2785.88

def test_ep_total_interest_and_payment():
    s = equal_principal_schedule(1_000_000, 3.5, 360)
    assert s["total_interest"] == 526458.33
    assert s["total_payment"] == round(1_000_000 + 526458.33, 2)

def test_ep_fixed_principal_and_declining_payment():
    s = equal_principal_schedule(1_000_000, 3.5, 360)
    rows = s["rows"]
    assert len(rows) == 360
    for row in rows[:-1]:
        assert row["principal"] == 2777.78
    for a, b in zip(rows, rows[1:-1]):
        assert a["payment"] > b["payment"]
    assert rows[-1]["balance"] == 0.0

def test_ep_interest_on_opening_balance():
    s = equal_principal_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][1]["interest"] == 2908.56

def test_ep_zero_rate():
    s = equal_principal_schedule(120000, 0, 12)
    assert s["first_payment"] == 10000.0
    assert s["last_payment"] == 10000.0
    assert s["total_interest"] == 0.0
    assert s["total_payment"] == 120000.0

def test_ep_bad_months():
    with pytest.raises(ValueError):
        equal_principal_schedule(100, 3, 0)
