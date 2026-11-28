"""Internal cooperative execution helpers; no Worker protocol changes."""

import hashlib
import logging


class Cancelled(Exception):
    """Execution stopped before its publication boundary."""


def check_cancelled(cancelled):
    if cancelled():
        raise Cancelled()


def copy_stream(source, target, cancelled):
    while True:
        check_cancelled(cancelled)
        block = source.read(1024 * 1024)
        check_cancelled(cancelled)
        if not block:
            return
        target.write(block)


def digest_file(path, cancelled):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            check_cancelled(cancelled)
            block = stream.read(1024 * 1024)
            check_cancelled(cancelled)
            if not block:
                return "sha256:" + digest.hexdigest()
            digest.update(block)


def notify(observer, fraction):
    try:
        observer(fraction)
    except Exception:
        # Fixed diagnostics do not expose callback text, paths or secrets.
        logging.getLogger(__name__).warning("Progress observer failed")
