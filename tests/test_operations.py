from app.operations import OperationLog


def test_log_add_list_count_clear() -> None:
    log = OperationLog()

    assert log.count() == 0
    assert log.list() == []

    op = log.add("USD", "RUB", 10, 92.5, 925)
    assert op.id
    assert op.ts
    assert log.count() == 1

    items = log.list()
    assert len(items) == 1
    assert items[0].id == op.id

    log.clear()
    assert log.count() == 0
    assert log.list() == []


def test_list_offset_limit() -> None:
    log = OperationLog()
    for i in range(5):
        log.add("USD", "RUB", i + 1, 1.0, i + 1)

    assert len(log.list(limit=2)) == 2
    assert len(log.list(offset=10)) == 0
    assert len(log.list(limit=2, offset=3)) == 2

    # negative cases
    assert len(log.list(limit=-1)) == 0
    assert len(log.list(offset=-100)) == 5


def test_list_limit_none_branch() -> None:
    log = OperationLog()
    log.add("USD", "RUB", 10, 1.0, 10)
    assert len(log.list(limit=None)) == 1


def test_list_covers_offset_negative_and_limit_none() -> None:
    log = OperationLog()
    log.add("USD", "RUB", 1, 1.0, 1.0)

    # offset < 0 branch + limit is None branch
    items = log.list(limit=None, offset=-1)
    assert len(items) == 1


def test_operation_log_class_is_executed() -> None:
    from app.operations import OperationLog  # локальный импорт для coverage

    log = OperationLog()
    assert log.count() == 0
