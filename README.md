# Currency Converter (Case 2)

HTTP currency converter. Rates are loaded from a CSV file.

## Project structure
- `app/` core logic (rates, converter, operations)
- `tests/` unit tests
- `data/rates.csv` rates file

## Rates file format
CSV: `data/rates.csv`

Header: `currency,rate_to_rub`

Example:
```csv
currency,rate_to_rub
RUB,1
USD,78.05
EUR,91.56

```
## Run demo
`python main.py`

## run tests + coverage
```
pip install pytest coverage
pytest
coverage run -m pytest
coverage report
```

## API (draft)

Base URL: `http://localhost:8008`

| Название действия | Локейшн (URL) | Тип запроса | Описание запроса и ответа |
|---|---|---|---|
| Проверка доступности сервиса | `/health` | GET | Возвращает статус сервиса. **Ответ 200**: `{"status":"ok"}` |
| Конвертация валюты | `/convert` | POST | Принимает JSON: `{"from":"USD","to":"RUB","amount":10}`. Возвращает результат конвертации и записывает операцию в историю. **Ответ 200**: `{"from":"USD","to":"RUB","amount":10,"rate":92.5,"result":925.0,"operation":{...}}`. Ошибки: **400** (невалидный JSON/нет полей/amount <= 0), **404** (валюта не найдена) |
| Получить историю операций | `/operations` | GET | Возвращает список операций. Query params (опц.): `limit` (int), `offset` (int). **Ответ 200**: `{"count": N, "items":[{...},{...}]}` |
| Получить операцию по id | `/operations/{id}` | GET | Возвращает одну операцию по `id`. **Ответ 200**: `{...}`. Ошибка: **404** если операция не найдена |

### Operation object
```json
{
  "id": "uuid",
  "ts": "2026-01-20T07:45:22.586611+00:00",
  "from": "USD",
  "to": "RUB",
  "amount": 10.0,
  "rate": 78.65,
  "result": 786.5
}
```
