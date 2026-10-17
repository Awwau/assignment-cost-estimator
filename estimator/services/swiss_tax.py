
from decimal import Decimal


# ============================================================
# SWISS SOCIAL SECURITY
# ============================================================

def calculate_swiss_social_security(annual_income):
    """
    Calculate employee Swiss social security contributions.

    Includes:
    - AHV / IV / EO: 5.3% of gross employment income
    - ALV: 1.1% of income up to CHF 148,200

    Excludes:
    - BVG occupational pension contributions
    """

    annual_income = Decimal(str(annual_income))

    if annual_income < 0:
        raise ValueError("Annual income cannot be negative.")

    ahv_iv_eo_rate = Decimal("0.053")
    alv_rate = Decimal("0.011")
    alv_income_cap = Decimal("148200")

    ahv_iv_eo = annual_income * ahv_iv_eo_rate

    alv_income = min(annual_income, alv_income_cap)
    alv = alv_income * alv_rate

    total = ahv_iv_eo + alv

    return {
        "ahv_iv_eo_chf": ahv_iv_eo,
        "alv_chf": alv,
        "total_chf": total,
    }


# ============================================================
# PROGRESSIVE SWISS TAX CALCULATION
# ============================================================

def calculate_progressive_tax(taxable_income, tax_brackets):
    """
    Calculate progressive income tax using marginal brackets.

    Each bracket must be a tuple:
        (upper_income_limit, marginal_tax_rate)

    The final bracket can use None as its upper limit.

    Note:
    Tax brackets must be independently verified for the
    relevant tax year and jurisdiction.
    """

    taxable_income = Decimal(str(taxable_income))

    if taxable_income < 0:
        raise ValueError("Taxable income cannot be negative.")

    total_tax = Decimal("0")
    previous_limit = Decimal("0")

    for upper_limit, rate in tax_brackets:
        rate = Decimal(str(rate))

        if upper_limit is None:
            upper_limit = taxable_income
        else:
            upper_limit = Decimal(str(upper_limit))

        taxable_in_bracket = min(
            taxable_income,
            upper_limit,
        ) - previous_limit

        if taxable_in_bracket > 0:
            total_tax += taxable_in_bracket * rate

        if taxable_income <= upper_limit:
            break

        previous_limit = upper_limit

    return total_tax


# ============================================================
# SWISS FEDERAL INCOME TAX
# ============================================================

# Provisional modelling brackets.
# These are not a verified implementation of the complete
# 2026 Swiss federal tax tariff for a single taxpayer.
# Do not use them to report a final tax liability.



# OFFICIAL 2026 TAX REFERENCES
#
# Federal tax tariff:
# https://www.estv.admin.ch/de/steuertarife-zur-direkten-bundessteuer
#
# Federal deductions:
# https://www.estv.admin.ch/de/abzuege-ansaetze-tarife-direkte-bundessteuer
#
# Zurich 2026 tax rules:
# https://www.zh.ch/de/steuern-finanzen/steuern/treuhaender/steuerbuch/steuerbuch-definition/zstb-34-1.html
#
# IMPORTANT:
# The existing federal brackets and Zurich multipliers
# are provisional and must not be used as final 2026 rates.



# 2026 Swiss direct federal income tax brackets
# Single taxpayer, no children.
#
# Sources:
# https://www.estv.admin.ch/en/tax-rates-for-direct-federal-tax
# https://taxsummaries.pwc.com/switzerland/individual/taxes-on-personal-income
#
# Rates are marginal rates expressed as decimals.
# The high-income 11.5% overall cap is not handled
# by this generic progressive tax function.

FEDERAL_TAX_BRACKETS_2026 = [
    (Decimal("15200"), Decimal("0")),
    (Decimal("33200"), Decimal("0.0077")),
    (Decimal("43500"), Decimal("0.0088")),
    (Decimal("58000"), Decimal("0.0264")),
    (Decimal("76200"), Decimal("0.0297")),
    (Decimal("82100"), Decimal("0.0594")),
    (Decimal("108900"), Decimal("0.0660")),
    (Decimal("141500"), Decimal("0.0880")),
    (Decimal("185100"), Decimal("0.1100")),
    (Decimal("793900"), Decimal("0.1320")),
    (None, Decimal("0.1150")),
]


def calculate_federal_income_tax(
    taxable_income,
    tax_brackets=FEDERAL_TAX_BRACKETS_2026,
):
    """
    Calculate a provisional federal income tax estimate.

    Requires verified tax brackets before production use.
    """

    return calculate_progressive_tax(
        taxable_income,
        tax_brackets,
    )


# ============================================================
# ZURICH CANTONAL AND MUNICIPAL TAX
# ============================================================


# Zurich 2026 basic income tax tariff (Grundtarif).
# Applies to a single taxpayer without children.
#
# Official source:
# https://www.zh.ch/content/dam/zhweb/bilder-dokumente/themen/steuern-finanzen/steuern/vertreter/steuerbuch/zstb-nr-48-1/zstb-nr-48-1.pdf

ZURICH_TAX_BRACKETS_2026 = [
    (Decimal("7000"), Decimal("0.00")),
    (Decimal("12000"), Decimal("0.02")),
    (Decimal("16800"), Decimal("0.03")),
    (Decimal("24800"), Decimal("0.04")),
    (Decimal("34500"), Decimal("0.05")),
    (Decimal("45700"), Decimal("0.06")),
    (Decimal("58800"), Decimal("0.07")),
    (Decimal("76400"), Decimal("0.08")),
    (Decimal("110400"), Decimal("0.09")),
    (Decimal("144100"), Decimal("0.10")),
    (Decimal("197400"), Decimal("0.11")),
    (Decimal("266700"), Decimal("0.12")),
    (None, Decimal("0.13")),
]


# Verified 2026 Zurich tax rates.
# Source: https://www.stadt-zuerich.ch/steuerberechnung

# State tax rate: 95% of basic cantonal tax
# Municioal tax rate: 119% of basic cantonal tax

# Applies to the City of Zurich.
# Church tax is excluded from this model.

ZURICH_CANTON_TAX_MULTIPLIER = Decimal("0.95")
ZURICH_CITY_TAX_MULTIPLIER = Decimal("1.19")


def calculate_zurich_income_tax(
    taxable_income,
    tax_brackets,
):
    """
    Calculate Zurich cantonal and municipal income tax.

    The tax_brackets argument must contain the applicable
    Zurich basic cantonal tax schedule.

    Multipliers are provisional and require verification
    for the relevant year and municipality.
    """

    basic_cantonal_tax = calculate_progressive_tax(
        taxable_income,
        tax_brackets,
    )

    cantonal_tax = (
        basic_cantonal_tax * ZURICH_CANTON_TAX_MULTIPLIER
    )

    municipal_tax = (
        basic_cantonal_tax * ZURICH_CITY_TAX_MULTIPLIER
    )

    return {
        "basic_cantonal_tax_chf": basic_cantonal_tax,
        "cantonal_tax_chf": cantonal_tax,
        "municipal_tax_chf": municipal_tax,
        "total_chf": cantonal_tax + municipal_tax,
    }


# ============================================================
# INCOME AFTER SWISS SOCIAL SECURITY
# ============================================================

def calculate_swiss_income_after_social_security(
    annual_gross_income_chf,
):
    """
    Calculate gross Swiss employment income after employee
    AHV / IV / EO and ALV contributions.

    This is not final Swiss taxable income because
    additional deductions may apply.
    """

    gross_income = Decimal(str(annual_gross_income_chf))

    if gross_income < 0:
        raise ValueError("Gross income cannot be negative.")

    social_security = calculate_swiss_social_security(
        gross_income
    )

    income_after_social_security = (
        gross_income - social_security["total_chf"]
    )

    return {
        "gross_income_chf": gross_income,
        "social_security_chf": social_security["total_chf"],
        "income_after_social_security_chf": income_after_social_security,
        "is_final_taxable_income": False,
    }


def calculate_swiss_taxable_income(
    income_after_social_security_chf,
    additional_deductions_chf=None,
):
    """
    Prepare estimated Swiss taxable income.

    Additional deductions must be supported by
    documented assumptions or official tax rules.
    """

    income = Decimal(str(income_after_social_security_chf))

    if income < 0:
        raise ValueError("Income cannot be negative.")

    if additional_deductions_chf is None:
        return {
            "income_after_social_security_chf": income,
            "additional_deductions_chf": None,
            "taxable_income_chf": None,
            "is_complete": False,
        }

    deductions = Decimal(str(additional_deductions_chf))

    if deductions < 0:
        raise ValueError("Deductions cannot be negative.")

    taxable_income = max(
        Decimal("0"),
        income - deductions,
    )

    return {
        "income_after_social_security_chf": income,
        "additional_deductions_chf": deductions,
        "taxable_income_chf": taxable_income,
        "is_complete": True,
    }


def calculate_zurich_employment_expense_deduction(
    qualifying_net_salary_chf,
):
    """
    Calculate the 2026 Zurich standard deduction
    for other employment expenses.

    Assumes the employee is eligible and the
    expenses are not reimbursed by the employer.
    """

    salary = Decimal(str(qualifying_net_salary_chf))

    if salary < 0:
        raise ValueError("Salary cannot be negative.")

    calculated_deduction = salary * Decimal("0.03")

    deduction = min(
        Decimal("4000"),
        max(Decimal("2000"), calculated_deduction),
    )

    return deduction


def prepare_swiss_taxable_incomes(
    income_after_social_security_chf,
    federal_deductions_chf=None,
    zurich_deductions_chf=None,
):
    """
    Prepare separate taxable incomes for
    Swiss federal and Zurich cantonal tax.

    Deduction amounts must be established separately.
    """

    income = Decimal(str(income_after_social_security_chf))

    if income < 0:
        raise ValueError("Income cannot be negative.")

    federal_income = None
    zurich_income = None

    if federal_deductions_chf is not None:
        federal_deductions = Decimal(
            str(federal_deductions_chf)
        )

        if federal_deductions < 0:
            raise ValueError(
                "Federal deductions cannot be negative."
            )

        federal_income = max(
            Decimal("0"),
            income - federal_deductions,
        )

    if zurich_deductions_chf is not None:
        zurich_deductions = Decimal(
            str(zurich_deductions_chf)
        )

        if zurich_deductions < 0:
            raise ValueError(
                "Zurich deductions cannot be negative."
            )

        zurich_income = max(
            Decimal("0"),
            income - zurich_deductions,
        )

    return {
        "federal_taxable_income_chf": federal_income,
        "zurich_taxable_income_chf": zurich_income,
        "is_complete": (
            federal_income is not None
            and zurich_income is not None
        ),
    }



def calculate_federal_employment_expense_deduction(
    qualifying_net_salary_chf,
    assumed_deduction_chf=Decimal("4000"),
):
    """
    Record an assumed Swiss federal employment-expense
    deduction for the tax-equalisation scenario.

    The default CHF 4,000 is provisional and must
    be checked against the 2026 federal rules.
    """

    salary = Decimal(str(qualifying_net_salary_chf))
    deduction = Decimal(str(assumed_deduction_chf))

    if salary < 0:
        raise ValueError("Salary cannot be negative.")

    if deduction < 0:
        raise ValueError("Deduction cannot be negative.")

    return {
        "deduction_chf": deduction,
        "is_verified": False,
    }


def validate_swiss_tax_estimate(
    calculated_tax_chf,
    official_reference_chf,
    tolerance_chf=Decimal("25"),
):
    """
    Compare our Swiss tax calculation with an
    official tax calculator reference.

    A passing comparison means the results are
    within tolerance, not that all tax assumptions
    have been verified.
    """

    calculated = Decimal(str(calculated_tax_chf))
    official = Decimal(str(official_reference_chf))
    tolerance = Decimal(str(tolerance_chf))

    if calculated < 0 or official < 0 or tolerance < 0:
        raise ValueError(
            "Tax amounts and tolerance cannot be negative."
        )

    difference = calculated - official
    absolute_difference = abs(difference)

    within_tolerance = absolute_difference <= tolerance

    return {
        "calculated_tax_chf": calculated,
        "official_reference_chf": official,
        "difference_chf": difference,
        "absolute_difference_chf": absolute_difference,
        "tolerance_chf": tolerance,
        "within_tolerance": within_tolerance,
    }


def calculate_total_hypothetical_swiss_tax(
    annual_gross_income_chf,
    exchange_rate,
):
    """
    Calculate a provisional annual hypothetical Swiss
    income tax estimate for a single employee living
    in the City of Zurich.

    Uses the current model's deduction assumptions.
    Not a verified final Swiss tax assessment.
    """

    gross_income = Decimal(str(annual_gross_income_chf))
    exchange_rate = Decimal(str(exchange_rate))

    if gross_income < 0:
        raise ValueError("Gross income cannot be negative.")

    if exchange_rate <= 0:
        raise ValueError("Exchange rate must be positive.")

    # 1. Calculate income after Swiss social security
    income_result = calculate_swiss_income_after_social_security(
        gross_income
    )

    income_after_ss = income_result[
        "income_after_social_security_chf"
    ]

    # 2. Calculate employment-expense deductions
    zurich_deduction = (
        calculate_zurich_employment_expense_deduction(
            income_after_ss
        )
    )

    federal_deduction_result = (
        calculate_federal_employment_expense_deduction(
            income_after_ss
        )
    )

    federal_deduction = federal_deduction_result[
        "deduction_chf"
    ]

    # 3. Calculate separate taxable incomes
    taxable_incomes = prepare_swiss_taxable_incomes(
        income_after_social_security_chf=income_after_ss,
        federal_deductions_chf=federal_deduction,
        zurich_deductions_chf=zurich_deduction,
    )

    federal_taxable_income = taxable_incomes[
        "federal_taxable_income_chf"
    ]

    zurich_taxable_income = taxable_incomes[
        "zurich_taxable_income_chf"
    ]

    # 4. Calculate federal income tax
    federal_tax = calculate_federal_income_tax(
        federal_taxable_income
    )

    # 5. Calculate Zurich cantonal and municipal tax
    zurich_taxes = calculate_zurich_income_tax(
        taxable_income=zurich_taxable_income,
        tax_brackets=ZURICH_TAX_BRACKETS_2026,
    )

    # 6. Include provisional Zurich personal tax
    personal_tax = Decimal("24")

    # 7. Calculate total hypothetical Swiss income tax
    total_tax_chf = (
        federal_tax
        + zurich_taxes["cantonal_tax_chf"]
        + zurich_taxes["municipal_tax_chf"]
        + personal_tax
    )

    total_tax_gbp = total_tax_chf / exchange_rate

    return {
        "gross_income_chf": gross_income,
        "income_after_social_security_chf": income_after_ss,
        "federal_deduction_chf": federal_deduction,
        "zurich_deduction_chf": zurich_deduction,
        "federal_taxable_income_chf": federal_taxable_income,
        "zurich_taxable_income_chf": zurich_taxable_income,
        "federal_tax_chf": federal_tax,
        "cantonal_tax_chf": zurich_taxes["cantonal_tax_chf"],
        "municipal_tax_chf": zurich_taxes["municipal_tax_chf"],
        "personal_tax_chf": personal_tax,
        "total_tax_chf": total_tax_chf,
        "total_tax_gbp": total_tax_gbp,
        "is_verified": False,
    }


def calculate_swiss_employer_social_security(annual_gross_income_chf):
    """
    Estimate Swiss employer AHV/IV/EO and ALV contributions.

    Excludes BVG occupational pension, accident insurance,
    family allowance contributions and administration fees.

    Assumes Swiss coverage continues during the assignment.
    """
    annual_income = Decimal(str(annual_gross_income_chf))

    if annual_income < 0:
        raise ValueError("Annual gross income cannot be negative.")

    ahv_iv_eo = annual_income * Decimal("0.053")

    alv_ceiling = Decimal("148200")
    alv = min(annual_income, alv_ceiling) * Decimal("0.011")

    total = ahv_iv_eo + alv

    return {
        "ahv_iv_eo_chf": ahv_iv_eo,
        "alv_chf": alv,
        "total_chf": total,
        "is_complete": False,
    }

