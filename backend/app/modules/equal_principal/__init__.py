"""等额本金模块：每期本金固定为本金除以期数，利息按当期期初余额乘月利率，
月供为本金加利息并逐期递减，末期把余额收干净。"""
from app.engines.amortization import equal_principal_schedule

METHOD = "equal_principal"
LABEL = "等额本金"


def schedule(principal: float, annual_rate: float, months: int) -> dict:
    """测算等额本金还款表，返回首期月供、末期月供、利息合计、还款合计与逐期明细。"""
    return equal_principal_schedule(principal, annual_rate, months)
