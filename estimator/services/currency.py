from decimal import Decimal


def chf_to_gbp(amount_chf, exchange_rate):
    """
    Convert Swiss francs to British pounds.

    exchange_rate: £1 = CHF 1.10
    """

    amount_chf = Decimal(str(amount_chf))
    exchange_rate = Decimal(str(exchange_rate))

    if exchange_rate <= 0:
        raise ValueError(
            "Exchange rate must be greater than zero."
        )

    return amount_chf / exchange_rate
