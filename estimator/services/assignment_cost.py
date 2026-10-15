
from decimal import Decimal

from .currency import chf_to_gbp


def calculate_home_pay(base_salary, bonus, exchange_rate):
    """
    Calculate annual salary and bonus in GBP.

    base_salary: annual salary in CHF
    bonus: annual bonus in CHF
    exchange_rate: CHF per 1 GBP
    """
    base_salary = Decimal(str(base_salary))
    bonus = Decimal(str(bonus))
    exchange_rate = Decimal(str(exchange_rate))

    if base_salary < 0 or bonus < 0:
        raise ValueError("Salary and bonus cannot be negative.")

    total_home_pay_chf = base_salary + bonus

    total_home_pay_gbp = chf_to_gbp(
        total_home_pay_chf,
        exchange_rate
    )

    return {
        "base_salary_chf": base_salary,
        "bonus_chf": bonus,
        "total_home_pay_chf": total_home_pay_chf,
        "total_home_pay_gbp": total_home_pay_gbp,
    }



def calculate_assignment_benefits(
    monthly_housing,
    relocation_chf,
    moving_costs,
    temporary_housing,
    exchange_rate,
    assignment_year,
):
    """
    Calculate employer-provided assignment benefits.

    Housing applies every year.
    Relocation, moving costs and temporary housing
    apply only in the first year.
    """
    monthly_housing = Decimal(str(monthly_housing))
    relocation_chf = Decimal(str(relocation_chf))
    moving_costs = Decimal(str(moving_costs))
    temporary_housing = Decimal(str(temporary_housing))
    exchange_rate = Decimal(str(exchange_rate))

    if any(
        amount < 0
        for amount in (
            monthly_housing,
            relocation_chf,
            moving_costs,
            temporary_housing,
        )
    ):
        raise ValueError("Benefit amounts cannot be negative.")

    if assignment_year not in (1, 2):
        raise ValueError("Assignment year must be 1 or 2.")

    annual_housing = monthly_housing * Decimal("12")

    if assignment_year == 1:
        relocation_gbp = chf_to_gbp(
            relocation_chf,
            exchange_rate,
        )
        moving = moving_costs
        temporary = temporary_housing
    else:
        relocation_gbp = Decimal("0")
        moving = Decimal("0")
        temporary = Decimal("0")

    total = annual_housing + relocation_gbp + moving + temporary

    return {
        "housing": annual_housing,
        "relocation": relocation_gbp,
        "moving_costs": moving,
        "temporary_housing": temporary,
        "total": total,
    }
