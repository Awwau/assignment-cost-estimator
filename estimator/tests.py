
from decimal import Decimal

from django.test import SimpleTestCase

from .services.assignment_cost import (
    calculate_assignment_benefits,
    calculate_final_employer_cost,
    calculate_home_pay,
)
from .services.currency import chf_to_gbp
from .services.swiss_tax import (
    FEDERAL_TAX_BRACKETS_2026,
    calculate_progressive_tax,
    calculate_swiss_social_security,
)
from .services.uk_tax import (
    calculate_personal_allowance,
    calculate_tax_gross_up,
    calculate_uk_income_tax,
)


class CurrencyConversionTests(SimpleTestCase):
    def test_chf_to_gbp(self):
        result = chf_to_gbp(Decimal("150000"), Decimal("1.10"))

        self.assertAlmostEqual(
            result,
            Decimal("136363.63636363636"),
            places=8,
        )

    def test_invalid_exchange_rate(self):
        with self.assertRaises(ValueError):
            chf_to_gbp(Decimal("150000"), Decimal("0"))


class UKTaxTests(SimpleTestCase):
    def test_personal_allowance(self):
        self.assertEqual(calculate_personal_allowance(60000), Decimal("12570"))

    def test_personal_allowance_taper(self):
        self.assertEqual(calculate_personal_allowance(110000), Decimal("7570"))

    def test_basic_rate(self):
        self.assertEqual(calculate_uk_income_tax(30000), Decimal("3486"))

    def test_higher_rate(self):
        self.assertEqual(calculate_uk_income_tax(60000), Decimal("11432"))

    def test_additional_rate(self):
        self.assertEqual(calculate_uk_income_tax(150000), Decimal("53703"))

    def test_gross_up(self):
        taxable_pay = Decimal("80000")
        tax = calculate_tax_gross_up(taxable_pay)
        recalculated_tax = calculate_uk_income_tax(taxable_pay + tax)

        self.assertAlmostEqual(
            tax,
            recalculated_tax,
            delta=Decimal("0.01"),
        )

    def test_negative_income(self):
        with self.assertRaises(ValueError):
            calculate_uk_income_tax(-100)

    def test_uk_income_tax_bands(self):
        expected_results = {
            Decimal("100000"): Decimal("27432.00"),
            Decimal("110000"): Decimal("33432.00"),
            Decimal("125140"): Decimal("42516.00"),
            Decimal("150000"): Decimal("53703.00"),
        }

        for income, expected_tax in expected_results.items():
            with self.subTest(income=income):
                actual_tax = calculate_uk_income_tax(income)
                self.assertEqual(actual_tax, expected_tax)


class SwissSocialSecurityTests(SimpleTestCase):
    def test_standard_assignment_income(self):
        result = calculate_swiss_social_security(Decimal("170000"))

        self.assertEqual(
            result["ahv_iv_eo_chf"],
            Decimal("9010.000"),
        )
        self.assertEqual(
            result["alv_chf"],
            Decimal("1630.200"),
        )
        self.assertEqual(
            result["total_chf"],
            Decimal("10640.200"),
        )

    def test_income_below_alv_limit(self):
        result = calculate_swiss_social_security(Decimal("100000"))

        self.assertEqual(
            result["total_chf"],
            Decimal("6400.000"),
        )

    def test_negative_income(self):
        with self.assertRaises(ValueError):
            calculate_swiss_social_security(-100)


class SwissFederalTaxTests(SimpleTestCase):
    def test_swiss_federal_tax_brackets(self):
        result = calculate_progressive_tax(
            Decimal("146979"),
            FEDERAL_TAX_BRACKETS_2026,
        )

        self.assertEqual(result, Decimal("6743.3300"))


class AssignmentCostTests(SimpleTestCase):
    def test_annual_home_pay(self):
        result = calculate_home_pay(
            base_salary=150000,
            bonus=20000,
            exchange_rate=1.10,
        )

        self.assertEqual(
            result["total_home_pay_chf"],
            Decimal("170000"),
        )
        self.assertAlmostEqual(
            result["total_home_pay_gbp"],
            Decimal("154545.45"),
            places=2,
        )

    def test_first_year_benefits(self):
        result = calculate_assignment_benefits(
            monthly_housing=3000,
            relocation_chf=5000,
            moving_costs=6000,
            temporary_housing=4000,
            exchange_rate=1.10,
            assignment_year=1,
        )

        self.assertAlmostEqual(
            result["total"],
            Decimal("50545.45"),
            places=2,
        )

    def test_second_year_benefits(self):
        result = calculate_assignment_benefits(
            monthly_housing=3000,
            relocation_chf=5000,
            moving_costs=6000,
            temporary_housing=4000,
            exchange_rate=1.10,
            assignment_year=2,
        )

        self.assertEqual(
            result["total"],
            Decimal("36000"),
        )

    def test_negative_salary_rejected(self):
        with self.assertRaises(ValueError):
            calculate_home_pay(
                base_salary=-1000,
                bonus=20000,
                exchange_rate=1.10,
            )


class FinalEmployerCostTests(SimpleTestCase):
    def test_final_employer_cost(self):
        result = calculate_final_employer_cost(
            home_pay_gbp=Decimal("154545.45"),
            assignment_benefits_gbp=Decimal("50545.45"),
            uk_tax_gross_up_gbp=Decimal("103890.77"),
            employer_social_security_gbp=Decimal("9672.91"),
            hypothetical_swiss_income_tax_gbp=Decimal("29780.38"),
            hypothetical_swiss_social_security_gbp=Decimal("9672.91"),
        )

        self.assertEqual(
            result["total_employer_cost_gbp"],
            Decimal("279201.29"),
        )
        self.assertEqual(
            result["total_hypothetical_deductions_gbp"],
            Decimal("39453.29"),
        )
        self.assertFalse(result["is_final"])

    def test_zero_home_pay_caps_hypothetical_deductions(self):
        result = calculate_final_employer_cost(
            home_pay_gbp=Decimal("0"),
            assignment_benefits_gbp=Decimal("36000"),
            uk_tax_gross_up_gbp=Decimal("15000"),
            employer_social_security_gbp=Decimal("0"),
            hypothetical_swiss_income_tax_gbp=Decimal("21.82"),
            hypothetical_swiss_social_security_gbp=Decimal("0"),
        )

        self.assertEqual(
            result["total_hypothetical_deductions_gbp"],
            Decimal("0"),
        )
        self.assertEqual(
            result["total_employer_cost_gbp"],
            Decimal("51000"),
        )
