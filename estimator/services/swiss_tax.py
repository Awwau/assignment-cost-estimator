from decimal import Decimal


def calculate_swiss_social_security(annual_income):
    """Estimate employee AHV/IV/EO and ALV contributions; excludes BVG."""
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


def calculate_progressive_tax(taxable_income, tax_brackets):
    """Calculate marginal tax using (upper limit, rate) brackets."""
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


FEDERAL_TAX_SCHEDULE_2026 = [
    # (taxable income threshold, base tax, additional tax per CHF 100)
    (Decimal("15200"), Decimal("0.00"), Decimal("0.77")),
    (Decimal("33200"), Decimal("138.60"), Decimal("0.88")),
    (Decimal("43500"), Decimal("229.20"), Decimal("2.64")),
    (Decimal("58000"), Decimal("612.00"), Decimal("2.97")),
    (Decimal("76200"), Decimal("1152.50"), Decimal("5.94")),
    (Decimal("82100"), Decimal("1502.95"), Decimal("6.60")),
    (Decimal("108900"), Decimal("3271.75"), Decimal("8.80")),
    (Decimal("141500"), Decimal("6140.55"), Decimal("11.00")),
    (Decimal("185100"), Decimal("10936.55"), Decimal("13.20")),
    (Decimal("793900"), Decimal("91298.15"), Decimal("11.85")),
    (Decimal("794000"), Decimal("91310.00"), Decimal("11.50")),
]


def calculate_federal_income_tax(taxable_income):
    """Estimate 2026 federal tax for a single taxpayer using the tariff schedule."""
    taxable_income = Decimal(str(taxable_income))
    if taxable_income < 0:
        raise ValueError("Taxable income cannot be negative.")
    if taxable_income <= Decimal("15200"):
        return Decimal("0.00")
    for threshold, base_tax, increment_per_100 in reversed(
        FEDERAL_TAX_SCHEDULE_2026
    ):
        if taxable_income >= threshold:
            additional_income = taxable_income - threshold
            return base_tax + (
                additional_income / Decimal("100")
            ) * increment_per_100
    return Decimal("0.00")
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
# Zurich tax multipliers used in this model.
# Source: https://www.stadt-zuerich.ch/steuerberechnung
# State tax rate: 95% of basic cantonal tax
# Municipal tax rate: 119% of basic cantonal tax
# Applies to the City of Zurich.
# Church tax is excluded from this model.


ZURICH_CANTON_TAX_MULTIPLIER = Decimal("0.95")


ZURICH_CITY_TAX_MULTIPLIER = Decimal("1.19")


def calculate_zurich_income_tax(
    taxable_income,
    tax_brackets,
):
    """Estimate Zurich cantonal and municipal income tax."""
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


def calculate_swiss_income_after_social_security(
    annual_gross_income_chf,
):
    """Deduct employee AHV/IV/EO and ALV from Swiss gross income."""
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
    """Estimate taxable income after documented deductions."""
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
    """Estimate Zurich employment-expense deduction under model assumptions."""
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
    """Prepare separate federal and Zurich taxable income amounts."""
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
    """Use a provisional CHF 4,000 federal employment-expense deduction."""
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
    """Compare a Swiss tax estimate with a reference within a tolerance."""
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
    """Estimate provisional federal, Zurich and personal tax for the model."""
    gross_income = Decimal(str(annual_gross_income_chf))
    exchange_rate = Decimal(str(exchange_rate))
    if gross_income < 0:
        raise ValueError("Gross income cannot be negative.")
    if exchange_rate <= 0:
        raise ValueError("Exchange rate must be positive.")
    income_result = calculate_swiss_income_after_social_security(
        gross_income
    )
    income_after_ss = income_result[
        "income_after_social_security_chf"
    ]
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
    federal_tax = calculate_federal_income_tax(
        federal_taxable_income
    )
    zurich_taxes = calculate_zurich_income_tax(
        taxable_income=zurich_taxable_income,
        tax_brackets=ZURICH_TAX_BRACKETS_2026,
    )
    personal_tax = Decimal("24")
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
    """Estimate employer AHV/IV/EO and ALV; excludes other contributions."""
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
