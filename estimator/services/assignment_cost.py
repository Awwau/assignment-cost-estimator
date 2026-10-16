
from decimal import Decimal

from .currency import chf_to_gbp
from .swiss_tax import calculate_swiss_social_security


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
        
        "tax_treatment": {
            "housing": "Taxable benefit-in-kind",
            "relocation": "Taxable cash",
            "moving_costs": "Potentially exempt relocation expense",
            "temporary_housing": "Potentially exempt relocation expense",
        },    
    }



def prepare_uk_tax_inputs(home_pay, benefits):
    """
    Prepare assignment amounts for the UK tax calculation.

    This does not calculate taxable income or UK tax yet.
    """
    return {
        "annual_home_pay_gbp": home_pay["total_home_pay_gbp"],
        "cash_relocation_gbp": benefits["relocation"],
        "housing_cost_gbp": benefits["housing"],
        "moving_costs_gbp": benefits["moving_costs"],
        "temporary_housing_gbp": benefits["temporary_housing"],
    }


def calculate_hypothetical_social_security(
    annual_home_pay_chf,
    exchange_rate,
):
    """
    Calculate hypothetical Swiss employee social security
    deductions and convert them to GBP.
    """
    swiss_contributions = calculate_swiss_social_security(
        annual_home_pay_chf
    )

    total_chf = swiss_contributions["total"]

    total_gbp = chf_to_gbp(
        total_chf,
        exchange_rate
    )

    return {
        "ahv_iv_eo_chf": swiss_contributions["ahv_iv_eo"],
        "alv_chf": swiss_contributions["alv"],
        "total_chf": total_chf,
        "total_gbp": total_gbp,
    }


def calculate_pay_after_social_security(
    home_pay,
    hypothetical_social_security,
):
    """
    Calculate annual home pay after hypothetical
    Swiss social security deductions.

    Hypothetical Swiss income tax is not yet deducted.
    """
    annual_home_pay = home_pay["total_home_pay_gbp"]
    social_security = hypothetical_social_security["total_gbp"]

    pay_after_social_security = (
        annual_home_pay - social_security
    )

    return {
        "annual_home_pay_gbp": annual_home_pay,
        "hypothetical_social_security_gbp": social_security,
        "pay_after_social_security_gbp": pay_after_social_security,
        "is_final_net_home_pay": False,
    }


def calculate_annual_cost_summary(
    home_pay,
    benefits,
    hypothetical_social_security,
    assignment_year,
):
    """
    Prepare a provisional annual assignment cost summary.

    Does not include UK income tax, tax gross-up,
    hypothetical Swiss income tax, or employer contributions.
    """
    if assignment_year not in (1, 2):
        raise ValueError("Assignment year must be 1 or 2.")

    gross_home_pay = home_pay["total_home_pay_gbp"]
    total_benefits = benefits["total"]

    known_employer_outlay = gross_home_pay + total_benefits

    return {
        "assignment_year": assignment_year,
        "gross_home_pay_gbp": gross_home_pay,
        "total_benefits_gbp": total_benefits,
        "hypothetical_social_security_gbp": (
            hypothetical_social_security["total_gbp"]
        ),
        "known_employer_outlay_gbp": known_employer_outlay,
        "is_final_employer_cost": False,
    }
