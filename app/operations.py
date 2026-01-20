from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Operation:
    id: str
    ts: str
    from_currency: str
    to_currency: str
    amount: float
    rate: float
    result: float

    def to_dict(self) -> dict:
        return asdict(self)


class OperationLog:
    def __init__(self) -> None:
        self._items: list[Operation] = []

    def add(self, from_currency: str, to_currency: str, amount: float, rate: float, result: float) -> Operation:
        op = Operation(
            id=str(uuid4()),
            ts=datetime.now(timezone.utc).isoformat(),
            from_currency=from_currency,
            to_currency=to_currency,
            amount=float(amount),
            rate=float(rate),
            result=float(result),
        )
        self._items.append(op)
        return op

    def list(self, limit: int | None = None, offset: int = 0) -> list[Operation]:
        if offset < 0:
            offset = 0
        items = self._items[offset:]
        if limit is None:
            return list(items)
        if limit < 0:
            return []
        return list(items[:limit])

    def count(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
