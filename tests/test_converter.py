import pytest

from app.converter import CurrencyConverter, InvalidAmountError
from app.rates import Rates, UnknownCurrencyError


def test_convert_ok_rounding() -> None:
    rates = Rates(rate_to_rub={"RUB": 1.0, "USD": 92.5})
    conv = CurrencyConverter(rates)

    res = conv.convert(1500, "RUB", "USD")
    assert res.from_currency == "RUB"
    assert res.to_currency == "USD"
    assert res.amount == 1500.0
    assert res.result == 16.22  # round(1500/92.5, 2)
    assert res.rate == round(1.0 / 92.5, 6)


def test_amount_must_be_number() -> None:
    rates = Rates(rate_to_rub={"RUB": 1.0, "USD": 92.5})
    conv = CurrencyConverter(rates)

    with pytest.raises(InvalidAmountError):
        conv.convert("10", "USD", "RUB")  # type: ignore[arg-type]


def test_amount_must_be_positive() -> None:
    rates = Rates(rate_to_rub={"RUB": 1.0, "USD": 92.5})
    conv = CurrencyConverter(rates)

    with pytest.raises(InvalidAmountError):
        conv.convert(0, "USD", "RUB")

    with pytest.raises(InvalidAmountError):
        conv.convert(-1, "USD", "RUB")


def test_unknown_currency_propagates() -> None:
    rates = Rates(rate_to_rub={"RUB": 1.0})
    conv = CurrencyConverter(rates)

    with pytest.raises(UnknownCurrencyError):
        conv.convert(10, "USD", "RUB")
