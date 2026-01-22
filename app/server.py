from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from app.converter import CurrencyConverter, InvalidAmountError
from app.operations import OperationLog
from app.rates import CsvRatesLoader, InvalidRatesFileError, UnknownCurrencyError


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: object) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _error(handler: BaseHTTPRequestHandler, status: int, error: str, message: str) -> None:
    _json_response(handler, status, {"error": error, "message": message})


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length_str = handler.headers.get("Content-Length", "0")
    try:
        length = int(length_str)
    except ValueError:
        raise ValueError("Invalid Content-Length")

    raw = handler.rfile.read(length) if length > 0 else b""
    try:
        obj = json.loads(raw.decode("utf-8")) if raw else None
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON") from e

    if not isinstance(obj, dict):
        raise ValueError("JSON body must be an object")

    return obj


class AppState:
    def __init__(self, rates_path: str) -> None:
        rates = CsvRatesLoader(rates_path).load()
        self.converter = CurrencyConverter(rates)
        self.log = OperationLog()


class Handler(BaseHTTPRequestHandler):
    state: AppState

    # чтобы не шумел стандартный логгер на каждый запрос
    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            _json_response(self, 200, {"status": "ok"})
            return

        if path == "/operations":
            qs = parse_qs(parsed.query)

            limit = None
            offset = 0

            if "limit" in qs:
                try:
                    limit = int(qs["limit"][0])
                except (ValueError, IndexError):
                    _error(self, 400, "bad_request", "limit must be integer")
                    return

            if "offset" in qs:
                try:
                    offset = int(qs["offset"][0])
                except (ValueError, IndexError):
                    _error(self, 400, "bad_request", "offset must be integer")
                    return

            items = [op.to_dict() for op in self.state.log.list(limit=limit, offset=offset)]
            _json_response(self, 200, {"count": self.state.log.count(), "items": items})
            return

        if path.startswith("/operations/"):
            op_id = path.removeprefix("/operations/").strip()
            if not op_id:
                _error(self, 404, "not_found", "operation id is required")
                return

            for op in self.state.log.list():
                if op.id == op_id:
                    _json_response(self, 200, op.to_dict())
                    return

            _error(self, 404, "not_found", "operation not found")
            return

        _error(self, 404, "not_found", "endpoint not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path != "/operations":
            _error(self, 404, "not_found", "endpoint not found")
            return

        try:
            body = _read_json(self)
        except ValueError as e:
            _error(self, 400, "bad_request", str(e))
            return

        try:
            from_cur = body["from"]
            to_cur = body["to"]
            amount = body["amount"]
        except KeyError as e:
            _error(self, 400, "bad_request", f"missing field: {e.args[0]}")
            return

        try:
            result = self.state.converter.convert(amount, from_cur, to_cur)
        except InvalidAmountError as e:
            _error(self, 400, "bad_request", str(e))
            return
        except UnknownCurrencyError as e:
            _error(self, 404, "not_found", str(e))
            return

        op = self.state.log.add(
            result.from_currency,
            result.to_currency,
            result.amount,
            result.rate,
            result.result,
        )

        payload = {
            "rate": result.rate,
            "result": result.result,
            "operation": {
                "id": op.id,
                "ts": op.ts,
                "from": op.from_currency,
                "to": op.to_currency,
                "amount": op.amount,
                "rate": op.rate,
                "result": op.result,
            },
        }
        _json_response(self, 200, payload)

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path != "/operations":
            _error(self, 404, "not_found", "endpoint not found")
            return

        deleted = self.state.log.count()
        self.state.log.clear()
        _json_response(self, 200, {"deleted": deleted})


def run_server(host: str = "0.0.0.0", port: int = 8008, rates_path: str = "data/rates.csv") -> None:
    # Создаём state один раз
    state = AppState(rates_path)

    # прокидываем state в handler через атрибут класса
    def handler_factory(*args, **kwargs):
        h = Handler(*args, **kwargs)
        return h

    # не используем factory в HTTPServer напрямую, поэтому присваиваем state классу
    Handler.state = state  # type: ignore[assignment]

    server = HTTPServer((host, port), Handler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    try:
        run_server()
    except InvalidRatesFileError as e:
        print(f"Failed to start server: {e}")
        raise
