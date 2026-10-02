"""Logging setup. On Cloud Run, emit one JSON object per line so Cloud Logging
parses severity and fields. Log IDs and event names only, never user content (PRIVACY.md)."""

import json
import logging
import sys

_STANDARD_ATTRS = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class CloudLoggingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {"severity": record.levelname, "message": record.getMessage(), "logger": record.name}
        entry.update({k: v for k, v in vars(record).items() if k not in _STANDARD_ATTRS})
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def configure_logging(json_output: bool) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        CloudLoggingFormatter() if json_output else logging.Formatter("%(levelname)s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.INFO)
