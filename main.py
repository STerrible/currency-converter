from pathlib import Path

from app.rates import CsvRatesLoader
from app.converter import CurrencyConverter
from app.operations import OperationLog


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    rates_path = base_dir / "data" / "rates.csv"

    rates = CsvRatesLoader(rates_path).load()
    converter = CurrencyConverter(rates)
    log = OperationLog()

    r1 = converter.convert(10, "USD", "RUB")
    op1 = log.add(r1.from_currency, r1.to_currency, r1.amount, r1.rate, r1.result)

    r2 = converter.convert(1500, "RUB", "USD")
    op2 = log.add(r2.from_currency, r2.to_currency, r2.amount, r2.rate, r2.result)

    print("Conversion 1:", r1)
    print("Operation 1:", op1.to_dict())
    print("Conversion 2:", r2)
    print("Operation 2:", op2.to_dict())

    print("\nAll operations:")
    for op in log.list():
        print(op.to_dict())


if __name__ == "__main__":
    main()
