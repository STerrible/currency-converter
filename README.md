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
USD,92.50
EUR,100.20

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