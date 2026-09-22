"""可选还款方式模块。equal_principal 已接入测算；其余仍为 0-1 桩。"""
from app.modules import equal_principal

MODULES = {equal_principal.METHOD: equal_principal}
