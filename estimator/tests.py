from django.test import TestCase

from decimal import Decimal
from django.test import SimpleTestCase

from .services.currency import chf_to_gbp

from .services.uk_tax import (
    calculate_uk_income_tax,
    calculate_personal_allowance,
    calculate_tax_gross_up,
)


class CurrencyConversionTests(SimpleTestCase):
    def test_chf_to_gbp(self):
        result = chf_to_gbp(Decimal("150000"), Decimal("1.10"))

        self.assertAlmostEqual(
            result,
            Decimal("136363.63636363636"),
            places=8
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

        self.assertAlmostEqual(tax, recalculated_tax, delta=Decimal("0.01"))

    def test_negative_income(self):
        with self.assertRaises(ValueError):
            calculate_uk_income_tax(-100)

