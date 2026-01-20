from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


class RatesError(Exception):
    """Base exception for rates-related issues."""


class UnknownCurrencyError(RatesError):
    pass


class InvalidRatesFileError(RatesError):
    pass


@dataclass(frozen=True)
class Rates:
    """
    Stores currency rates to base currency (RUB).
    Example: rate_to_rub['USD'] = 92.5 means 1 USD = 92.5 RUB.
    """
    rate_to_rub: dict[str, float]

    def normalize(self, code: str) -> str:
        if not isinstance(code, str):
            raise UnknownCurrencyError("Currency code must be a string")
        code = code.strip().upper()
        if not code:
            raise UnknownCurrencyError("Currency code is empty")
        return code

    def get_rate_to_rub(self, code: str) -> float:
        code = self.normalize(code)
        try:
            return self.rate_to_rub[code]
        except KeyError as e:
            raise UnknownCurrencyError(f"Unknown currency: {code}") from e


class CsvRatesLoader:
    """
    Loads rates from CSV with header: currency,rate_to_rub
    """
    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)

    def load(self) -> Rates:
        if not self.csv_path.exists() or not self.csv_path.is_file():
            raise InvalidRatesFileError(f"Rates file not found: {self.csv_path}")

        rate_to_rub: dict[str, float] = {}

        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise InvalidRatesFileError("CSV has no header row")

            required = {"currency", "rate_to_rub"}
            if set(name.strip() for name in reader.fieldnames) != required:
                # строгая проверка: ровно 2 колонки
                raise InvalidRatesFileError(
                    f"CSV header must be exactly: {sorted(required)}"
                )

            for idx, row in enumerate(reader, start=2):  # start=2 because header is line 1
                raw_code = (row.get("currency") or "").strip().upper()
                raw_rate = (row.get("rate_to_rub") or "").strip()

                if not raw_code:
                    raise InvalidRatesFileError(f"Empty currency code at line {idx}")

                try:
                    rate = float(raw_rate)
                except ValueError as e:
                    raise InvalidRatesFileError(
                        f"Invalid rate at line {idx}: {raw_rate!r}"
                    ) from e

                if rate <= 0:
                    raise InvalidRatesFileError(f"Rate must be > 0 at line {idx}")

                rate_to_rub[raw_code] = rate

        # гарантируем, что базовая валюта есть
        if "RUB" not in rate_to_rub:
            rate_to_rub["RUB"] = 1.0

        return Rates(rate_to_rub=rate_to_rub)
