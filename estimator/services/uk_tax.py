from decimal import Decimal

PERSONAL_ALLOWANCE = Decimal("12570")
ALLOWANCE_TAPER_START = Decimal("100000")

BASIC_RATE_LIMIT = Decimal("37700")
ADDITIONAL_RATE_THRESHOLD = Decimal("125140")

BASIC_RATE = Decimal("0.20")
HIGHER_RATE = Decimal("0.40")
ADDITIONAL_RATE = Decimal("0.45")


def calculate_personal_allowance(income):
    income = Decimal(str(income))
    if income < 0:
        raise ValueError("Income cannot be negative.")

    excess = max(income - ALLOWANCE_TAPER_START, Decimal("0"))
    reduction = excess / Decimal("2")

    return max(PERSONAL_ALLOWANCE - reduction, Decimal("0"))


def calculate_uk_income_tax(income):
    income = Decimal(str(income))
    if income < 0:
        raise ValueError("Income cannot be negative.")

    allowance = calculate_personal_allowance(income)
    taxable_income = max(income - allowance, Decimal("0"))

    basic_amount = min(taxable_income,BASIC_RATE_LIMIT)

    higher_amount = min(max(taxable_income - BASIC_RATE_LIMIT, Decimal("0")), ADDITIONAL_RATE_THRESHOLD - BASIC_RATE_LIMIT)

    additional_amount = max(taxable_income - ADDITIONAL_RATE_THRESHOLD, Decimal("0"))

    tax = (basic_amount * BASIC_RATE + higher_amount * HIGHER_RATE + additional_amount * ADDITIONAL_RATE)

    return tax


def calculate_tax_gross_up(taxable_pay, tolerance=Decimal("0.01"), max_iterations=100):
    taxable_pay = Decimal(str(taxable_pay))
    tolerance = Decimal(str(tolerance))

    if taxable_pay < 0:
        raise ValueError(
            "Taxable pay cannot be negative."
        )

    if tolerance <= 0:
        raise ValueError(
            "Tolerance must be greater than zero."
        )

    tax_estimate = Decimal("0")

    for iteration in range(max_iterations):
        new_tax = calculate_uk_income_tax(taxable_pay + tax_estimate)

        difference = abs(new_tax - tax_estimate)

        if difference < tolerance:
            return new_tax

        tax_estimate = new_tax

    raise RuntimeError(
        "Tax gross-up calculation did not converge."
    )

"""
THIS IS NOT NECESSARY AND SHOULD BE REMOVED

"""

def calculate_tax_equalisation_adjustment(
    taxable_income_before_adjustment,
    hypothetical_deductions_gbp,
    tolerance=Decimal("0.01"),
    max_iterations=100,
):
    """
    Calculate the additional taxable employer payment
    needed to cover UK income tax after accounting for
    hypothetical deductions retained from the employee.

    Model assumption:
    - UK tax is paid from employee cash compensation.
    - Hypothetical deductions are withheld internally.
    - Employer adds taxable compensation so the employee
      retains their protected net home pay.
    """

    taxable_income = Decimal(
        str(taxable_income_before_adjustment)
    )
    hypothetical_deductions = Decimal(
        str(hypothetical_deductions_gbp)
    )
    tolerance = Decimal(str(tolerance))

    if taxable_income < 0 or hypothetical_deductions < 0:
        raise ValueError("Amounts cannot be negative.")

    if tolerance <= 0:
        raise ValueError("Tolerance must be greater than zero.")

    adjustment = Decimal("0")

    for _ in range(max_iterations):
        uk_tax = calculate_uk_income_tax(
            taxable_income + adjustment
        )

        new_adjustment = uk_tax - hypothetical_deductions

        if new_adjustment < 0:
            new_adjustment = Decimal("0")

        if abs(new_adjustment - adjustment) < tolerance:
            return new_adjustment

        adjustment = new_adjustment

    raise RuntimeError(
        "Tax equalisation adjustment did not converge."
    )

