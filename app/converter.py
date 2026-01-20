from __future__ import annotations

from dataclasses import dataclass

from app.rates import Rates, UnknownCurrencyError


class ConversionError(Exception):
    """Base exception for conversion issues."""


class InvalidAmountError(ConversionError):
    pass


@dataclass(frozen=True)
class ConversionResult:
    from_currency: str
    to_currency: str
    amount: float
    rate: float
    result: float


class CurrencyConverter:
    def __init__(self, rates: Rates) -> None:
        self._rates = rates

    def convert(self, amount: float, from_currency: str, to_currency: str) -> ConversionResult:
        if not isinstance(amount, (int, float)):
            raise InvalidAmountError("Amount must be a number")

        amount = float(amount)
        if amount <= 0:
            raise InvalidAmountError("Amount must be > 0")

        f = self._rates.normalize(from_currency)
        t = self._rates.normalize(to_currency)

        # 1 FROM -> RUB -> TO
        rate_from = self._rates.get_rate_to_rub(f)  # raises UnknownCurrencyError
        rate_to = self._rates.get_rate_to_rub(t)    # raises UnknownCurrencyError

        # rate of (1 FROM) in TO:
        rate = rate_from / rate_to
        result = amount * rate

        # округлим до 2 знаков (как для денег)
        result_rounded = round(result, 2)
        rate_rounded = round(rate, 6)

        return ConversionResult(
            from_currency=f,
            to_currency=t,
            amount=amount,
            rate=rate_rounded,
            result=result_rounded,
        )
