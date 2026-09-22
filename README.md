# 15-mortgage（房贷月供）

Mortgage — 等额本息 / 等额本金月供与逐期本金利息拆分

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4400 |
| API | http://localhost:9400 |

## 主链

贷额期限利率 → 等额本息/等额本金还款表（method 可选，缺省等额本息）→ 利息合计

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
