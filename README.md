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
All requests/responses use JSON. Request header for body: `Content-Type: application/json`.

| Название действия | Локейшн (URL) | Тип запроса | Описание запроса и ответа |
|---|---|---|---|
| Проверка доступности | `/health` | GET | **200**: `{"status":"ok"}` |
| Создать операцию конвертации | `/operations` | POST | **Запрос**: `{"from":"USD","to":"RUB","amount":10}`. Сервер выполняет конвертацию по курсам из CSV и сохраняет операцию. **200**: `{"operation":{...},"rate":92.5,"result":925.0}`. **400**: невалидный JSON/нет полей/amount<=0. **404**: неизвестная валюта |
| Получить историю операций | `/operations` | GET | Query params (опц.): `limit` (int), `offset` (int). **200**: `{"count":N,"items":[{...}]}`. **400**: некорректные query-параметры |
| Получить операцию по id | `/operations/{id}` | GET | **200**: `{...}`. **404**: операция не найдена |
| Очистить историю операций | `/operations` | DELETE | Удаляет все операции из истории. **200**: `{"deleted":N}` (сколько удалено). |

### Query params for GET /operations
- `limit` (optional): max number of items to return. If omitted → return all.
- `offset` (optional): start position from 0. If omitted → 0.
- If `limit < 0` → return empty list.
- If `offset < 0` → treated as 0.

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

