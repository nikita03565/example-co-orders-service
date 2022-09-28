"""
A place for custom decorators
"""
import json
import logging

from functools import wraps

logging.basicConfig()
logger = logging.getLogger("exampleco.sqltime")
logger.setLevel(logging.DEBUG)


def handle_exception(func):
    """Catches all unexpected exceptions and returns 500 response."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Exception occurred: %s", exc)
            return {"statusCode": 500, "body": json.dumps({"error": str(exc)})}

    return inner
