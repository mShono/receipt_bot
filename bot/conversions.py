import logging

from decimal import Decimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def float_to_int(price):
    decim_price = Decimal(f"{price}")
    return int(decim_price*100)


def int_to_float_str(price):
    str_int_price = str(price)
    try:
        entier_part, fractional_part = str_int_price.split(".", 1)
    except Exception as e:
        logger.info(f"The incoming price {price} was in cents - {e}")
        str_float_price = str_int_price[:-2] + "." + str_int_price[-2:]
        # logger.info(f"Returning price {str_float_price}")
        return float(str_float_price)
    logger.info(f"The incoming price {price} was in euros")
    return price