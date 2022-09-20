import json
import logging

from functools import wraps

logging.basicConfig()
logger = logging.getLogger("exampleco.sqltime")
logger.setLevel(logging.DEBUG)


def handle_exception(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("Exception occurred: %s", e)
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    return inner
