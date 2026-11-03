from decimal import ROUND_HALF_UP, Decimal, localcontext

CENT = Decimal("0.01")
ROUNDING_MODE = ROUND_HALF_UP


def round_money(amount: Decimal) -> Decimal:
    if not amount.is_finite():
        raise ValueError("Money values must be finite.")

    with localcontext() as context:
        context.prec = max(
            context.prec,
            len(amount.as_tuple().digits) + 2,
            amount.adjusted() + 3,
        )
        return amount.quantize(CENT, rounding=ROUNDING_MODE)
