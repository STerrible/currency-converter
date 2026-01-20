from pathlib import Path

import pytest

from app.rates import CsvRatesLoader, InvalidRatesFileError

from app.rates import Rates, UnknownCurrencyError


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8", newline="\n")
    return p


def test_load_ok(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "rates.csv",
        "currency,rate_to_rub\nRUB,1\nUSD,92.5\nEUR,100.2\n",
    )
    rates = CsvRatesLoader(path).load()

    assert rates.get_rate_to_rub("usd") == 92.5
    assert rates.get_rate_to_rub("RUB") == 1.0


def test_load_adds_rub_if_missing(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "rates.csv",
        "currency,rate_to_rub\nUSD,92.5\n",
    )
    rates = CsvRatesLoader(path).load()
    assert rates.get_rate_to_rub("RUB") == 1.0


def test_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "nope.csv"
    with pytest.raises(InvalidRatesFileError):
        CsvRatesLoader(missing).load()


def test_no_header_row(tmp_path: Path) -> None:
    path = _write(tmp_path, "rates.csv", "")
    with pytest.raises(InvalidRatesFileError):
        CsvRatesLoader(path).load()


def test_wrong_header(tmp_path: Path) -> None:
    path = _write(tmp_path, "rates.csv", "cur,rate\nUSD,1\n")
    with pytest.raises(InvalidRatesFileError):
        CsvRatesLoader(path).load()


def test_empty_currency_code(tmp_path: Path) -> None:
    path = _write(tmp_path, "rates.csv", "currency,rate_to_rub\n,10\n")
    with pytest.raises(InvalidRatesFileError):
        CsvRatesLoader(path).load()


def test_invalid_rate_not_float(tmp_path: Path) -> None:
    path = _write(tmp_path, "rates.csv", "currency,rate_to_rub\nUSD,abc\n")
    with pytest.raises(InvalidRatesFileError):
        CsvRatesLoader(path).load()


def test_invalid_rate_non_positive(tmp_path: Path) -> None:
    path = _write(tmp_path, "rates.csv", "currency,rate_to_rub\nUSD,0\n")
    with pytest.raises(InvalidRatesFileError):
        CsvRatesLoader(path).load()


def test_unknown_currency_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "rates.csv",
        "currency,rate_to_rub\nRUB,1\nUSD,92.5\n",
    )
    rates = CsvRatesLoader(path).load()

    with pytest.raises(UnknownCurrencyError):
        rates.get_rate_to_rub("ABC")

    with pytest.raises(UnknownCurrencyError):
        rates.get_rate_to_rub("")


def test_normalize_non_string_raises() -> None:
    rates = Rates(rate_to_rub={"RUB": 1.0})
    with pytest.raises(UnknownCurrencyError):
        rates.normalize(123)  # type: ignore[arg-type]
