from decimal import Decimal
from .currency import chf_to_gbp
from .swiss_tax import calculate_swiss_social_security


def calculate_home_pay(base_salary, bonus, exchange_rate):
    """Convert annual Swiss salary and bonus to GBP."""
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
    """Calculate annual housing and first-year relocation benefits."""
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
    """Collect compensation and benefit components for UK tax modelling."""
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
    """Calculate hypothetical Swiss employee contributions in CHF and GBP."""
    swiss_contributions = calculate_swiss_social_security(
        annual_home_pay_chf
    )
    total_chf = swiss_contributions["total_chf"]
    total_gbp = chf_to_gbp(
        total_chf,
        exchange_rate
    )
    return {
        "ahv_iv_eo_chf": swiss_contributions["ahv_iv_eo_chf"],
        "alv_chf": swiss_contributions["alv_chf"],
        "total_chf": total_chf,
        "total_gbp": total_gbp,
    }


def calculate_pay_after_social_security(
    home_pay,
    hypothetical_social_security,
):
    """Deduct hypothetical Swiss social security before Swiss income tax."""
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
    """Summarise known costs before tax gross-up and employer contributions."""
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


def calculate_relocation_relief(
    moving_costs,
    temporary_housing,
    exemption_limit=Decimal("8000"),
):
    """Apply assumed relief to qualifying relocation expenses, subject to eligibility."""
    moving_costs = Decimal(str(moving_costs))
    temporary_housing = Decimal(str(temporary_housing))
    exemption_limit = Decimal(str(exemption_limit))
    if any(amount < 0 for amount in (
        moving_costs,
        temporary_housing,
        exemption_limit,
    )):
        raise ValueError("Amounts cannot be negative.")
    total_qualifying_costs = moving_costs + temporary_housing
    exempt_amount = min(
        total_qualifying_costs,
        exemption_limit,
    )
    potentially_taxable_amount = (
        total_qualifying_costs - exempt_amount
    )
    return {
        "total_qualifying_costs": total_qualifying_costs,
        "exempt_amount": exempt_amount,
        "potentially_taxable_amount": potentially_taxable_amount,
    }


def calculate_uk_taxable_benefits(
    benefits,
    relocation_relief,
):
    """Identify taxable relocation amounts; housing valuation is handled separately."""
    taxable_cash = benefits["relocation"]
    taxable_relocation_expenses = (
        relocation_relief["potentially_taxable_amount"]
    )
    known_taxable_amount = (
        taxable_cash + taxable_relocation_expenses
    )
    return {
        "taxable_cash": taxable_cash,
        "taxable_relocation_expenses": taxable_relocation_expenses,
        "known_taxable_amount": known_taxable_amount,
        "housing_employer_cost": benefits["housing"],
        "housing_taxable_value": None,
        "is_complete": False,
    }


def assess_employer_accommodation(
    annual_housing_cost,
    employer_rents_property=True,
    employee_contribution=0,
    assumed_taxable_value=None,
):
    """Record an assumed accommodation taxable value pending HMRC verification."""
    annual_housing_cost = Decimal(str(annual_housing_cost))
    employee_contribution = Decimal(str(employee_contribution))
    if annual_housing_cost < 0 or employee_contribution < 0:
        raise ValueError("Accommodation amounts cannot be negative.")
    if assumed_taxable_value is not None:
        assumed_taxable_value = Decimal(str(assumed_taxable_value))
        if assumed_taxable_value < 0:
            raise ValueError("Taxable value cannot be negative.")
        valuation_status = "Assumed taxable value - requires verification"
        requires_valuation = True
    else:
        valuation_status = "Pending HMRC accommodation assessment"
        requires_valuation = True
    return {
        "annual_employer_cost": annual_housing_cost,
        "employer_rents_property": employer_rents_property,
        "employee_contribution": employee_contribution,
        "taxable_benefit_value": assumed_taxable_value,
        "requires_valuation": requires_valuation,
        "valuation_status": valuation_status,
    }


def calculate_total_taxable_benefits(
    taxable_benefits,
    accommodation,
):
    """Combine taxable assignment benefits with the assumed accommodation value."""
    housing_taxable_value = accommodation["taxable_benefit_value"]
    if housing_taxable_value is None:
        raise ValueError(
            "An accommodation taxable value is required."
        )
    known_taxable_amount = taxable_benefits["known_taxable_amount"]
    total_taxable_benefits = (
        known_taxable_amount + housing_taxable_value
    )
    return {
        "known_taxable_amount": known_taxable_amount,
        "housing_taxable_value": housing_taxable_value,
        "total_taxable_benefits": total_taxable_benefits,
        "is_verified": False,
    }


def prepare_uk_taxable_income(
    pay_after_social_security,
    total_taxable_benefits,
    hypothetical_swiss_income_tax_gbp=None,
):
    """Prepare the UK gross-up base, flooring protected net pay at zero."""
    pay_after_ss = Decimal(
        str(pay_after_social_security["pay_after_social_security_gbp"])
    )
    taxable_benefits = Decimal(
        str(total_taxable_benefits["total_taxable_benefits"])
    )
    if hypothetical_swiss_income_tax_gbp is None:
        return {
            "taxable_income_before_gross_up": None,
            "is_complete": False,
        }
    hypothetical_tax = Decimal(
        str(hypothetical_swiss_income_tax_gbp)
    )
    if hypothetical_tax < 0:
        raise ValueError(
            "Hypothetical Swiss income tax cannot be negative."
        )
    protected_net_home_pay = max(
        pay_after_ss - hypothetical_tax,
        Decimal("0")
    )
    taxable_income = (
        protected_net_home_pay
        + taxable_benefits
    )
    return {
        "pay_after_social_security": pay_after_ss,
        "taxable_benefits": taxable_benefits,
        "hypothetical_swiss_income_tax": hypothetical_tax,
        "taxable_income_before_gross_up": taxable_income,
        "protected_net_home_pay": protected_net_home_pay,
        "is_complete": True,
    }


def calculate_hypothetical_swiss_income_tax(
    federal_tax_chf,
    cantonal_tax_chf,
    municipal_tax_chf,
    exchange_rate,
):
    """Combine Swiss federal, cantonal and municipal income tax estimates."""
    federal_tax_chf = Decimal(str(federal_tax_chf))
    cantonal_tax_chf = Decimal(str(cantonal_tax_chf))
    municipal_tax_chf = Decimal(str(municipal_tax_chf))
    exchange_rate = Decimal(str(exchange_rate))
    if any(amount < 0 for amount in (
        federal_tax_chf,
        cantonal_tax_chf,
        municipal_tax_chf,
    )):
        raise ValueError("Tax amounts cannot be negative.")
    total_tax_chf = (
        federal_tax_chf
        + cantonal_tax_chf
        + municipal_tax_chf
    )
    return {
        "federal_tax_chf": federal_tax_chf,
        "cantonal_tax_chf": cantonal_tax_chf,
        "municipal_tax_chf": municipal_tax_chf,
        "total_tax_chf": total_tax_chf,
        "total_tax_gbp": chf_to_gbp(
            total_tax_chf,
            exchange_rate,
        ),
    }


def calculate_protected_net_home_pay(
    home_pay,
    hypothetical_social_security,
    hypothetical_swiss_tax,
):
    """Estimate protected net home pay, capped at zero for this model."""
    gross_home_pay_gbp = Decimal(
        str(home_pay["total_home_pay_gbp"])
    )
    social_security_gbp = Decimal(
        str(hypothetical_social_security["total_gbp"])
    )
    swiss_income_tax_gbp = Decimal(
        str(hypothetical_swiss_tax["total_tax_gbp"])
    )
    protected_net_home_pay_gbp = max(
        gross_home_pay_gbp
        - social_security_gbp
        - swiss_income_tax_gbp,
        Decimal("0")
    )
    return {
        "gross_home_pay_gbp": gross_home_pay_gbp,
        "hypothetical_social_security_gbp": social_security_gbp,
        "hypothetical_swiss_income_tax_gbp": swiss_income_tax_gbp,
        "protected_net_home_pay_gbp": protected_net_home_pay_gbp,
        "is_final": False,
    }


def calculate_final_employer_cost(
    home_pay_gbp,
    assignment_benefits_gbp,
    uk_tax_gross_up_gbp,
    employer_social_security_gbp,
    hypothetical_swiss_income_tax_gbp,
    hypothetical_swiss_social_security_gbp,
):
    """Combine employer costs less hypothetical deductions, capped at gross home pay."""
    home_pay = Decimal(str(home_pay_gbp))
    benefits = Decimal(str(assignment_benefits_gbp))
    uk_tax = Decimal(str(uk_tax_gross_up_gbp))
    employer_ss = Decimal(str(employer_social_security_gbp))
    hypothetical_tax = Decimal(str(hypothetical_swiss_income_tax_gbp))
    hypothetical_ss = Decimal(str(hypothetical_swiss_social_security_gbp))
    amounts = [
        home_pay,
        benefits,
        uk_tax,
        employer_ss,
        hypothetical_tax,
        hypothetical_ss,
    ]
    if any(amount < 0 for amount in amounts):
        raise ValueError("Employer cost components cannot be negative.")
    total_hypothetical_deductions = min(
        hypothetical_tax + hypothetical_ss, home_pay
    )
    applied_hypothetical_ss = min(
        hypothetical_ss,
        total_hypothetical_deductions
    )
    applied_hypothetical_tax = (
        total_hypothetical_deductions
        - applied_hypothetical_ss
    )
    total_employer_cost = (
        home_pay
        + benefits
        + uk_tax
        + employer_ss
        - total_hypothetical_deductions
    )
    cost_multiple = (
        total_employer_cost / home_pay
        if home_pay > 0
        else None
    )
    return {
        "home_pay_gbp": home_pay,
        "assignment_benefits_gbp": benefits,
        "uk_tax_gross_up_gbp": uk_tax,
        "employer_social_security_gbp": employer_ss,
        "hypothetical_swiss_income_tax_gbp": hypothetical_tax,
        "hypothetical_swiss_social_security_gbp": hypothetical_ss,
        "total_hypothetical_deductions_gbp": total_hypothetical_deductions,
        "total_employer_cost_gbp": total_employer_cost,
        "cost_multiple": cost_multiple,
        "is_final": False,
        "applied_hypothetical_swiss_income_tax_gbp": applied_hypothetical_tax,
        "applied_hypothetical_swiss_social_security_gbp": applied_hypothetical_ss,
    }
