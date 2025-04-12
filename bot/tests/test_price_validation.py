import logging

from ..bot_utils import price_validation

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REQUESTS_AND_RESPONDS = {
    "-1": False,
    "-1,2": False,
    "-1.2": False,
    "-1,-2": False,
    "-1.-2": False,
    "1,-2": False,
    "1.-2": False,
    "-1,23": False,
    "-1.23": False,
    "1.234": False,
    "1,234": False,
    "1&2": False,
    "ddd": False,
    "dd,dd": False,
    "dd.dd": False,
    "0": False,
    "-0": False,
    # "-0.2": False,

    "0.2": True,
    "1": True,
    "1,0": True,
    "1.0": True,
    "1,2": True,
    "1.2": True,
    "1.23": True,
    "1,23": True,
}

def test_price_validation():
    for request in REQUESTS_AND_RESPONDS:
        respond, _ = price_validation(request)
        assert respond == REQUESTS_AND_RESPONDS[request], f"Error for request {request}: {respond}"