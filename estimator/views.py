from django.shortcuts import render

from .forms import AssignmentForm

from .services.assignment_cost import (
    calculate_home_pay,
    calculate_assignment_benefits,
    calculate_hypothetical_social_security,
    calculate_pay_after_social_security,
    calculate_annual_cost_summary,
    calculate_relocation_relief,
    calculate_uk_taxable_benefits,
    assess_employer_accommodation,
    calculate_total_taxable_benefits,
    prepare_uk_taxable_income,
    calculate_protected_net_home_pay,
    calculate_final_employer_cost,
)

from .services.swiss_tax import (
    calculate_total_hypothetical_swiss_tax,
    calculate_swiss_employer_social_security,
)

from .services.uk_tax import calculate_tax_gross_up


def home(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment_data = form.cleaned_data
            home_pay = calculate_home_pay(
                base_salary=assignment_data["base_salary"],
                bonus=assignment_data["bonus"],
                exchange_rate=assignment_data["exchange_rate"],
            )
            year_1_benefits = calculate_assignment_benefits(
                monthly_housing=assignment_data["housing"],
                relocation_chf=assignment_data["relocation"],
                moving_costs=assignment_data["moving_costs"],
                temporary_housing=assignment_data["temporary_housing"],
                exchange_rate=assignment_data["exchange_rate"],
                assignment_year=1,
            )
            year_2_benefits = calculate_assignment_benefits(
                monthly_housing=assignment_data["housing"],
                relocation_chf=assignment_data["relocation"],
                moving_costs=assignment_data["moving_costs"],
                temporary_housing=assignment_data["temporary_housing"],
                exchange_rate=assignment_data["exchange_rate"],
                assignment_year=2,
            )
            hypothetical_social_security = calculate_hypothetical_social_security(
                annual_home_pay_chf=home_pay["total_home_pay_chf"],
                exchange_rate=assignment_data["exchange_rate"],
            )
            pay_after_social_security = calculate_pay_after_social_security(
                home_pay=home_pay,
                hypothetical_social_security=hypothetical_social_security,
                )
            year_1_summary = calculate_annual_cost_summary(
                home_pay=home_pay,
                benefits=year_1_benefits,
                hypothetical_social_security=hypothetical_social_security,
                assignment_year=1,
            )
            year_2_summary = calculate_annual_cost_summary(
                home_pay=home_pay,
                benefits=year_2_benefits,
                hypothetical_social_security=hypothetical_social_security,
                assignment_year=2,
            )
            two_year_total = (
                year_1_summary["known_employer_outlay_gbp"] + year_2_summary["known_employer_outlay_gbp"]
            )
            year_1_relocation_relief = calculate_relocation_relief(
                  moving_costs=year_1_benefits["moving_costs"],
                  temporary_housing=year_1_benefits["temporary_housing"],
            )
            year_2_relocation_relief = calculate_relocation_relief(
                moving_costs=year_2_benefits["moving_costs"],
                temporary_housing=year_2_benefits["temporary_housing"],
            )
            year_1_taxable_benefits = calculate_uk_taxable_benefits(
                benefits=year_1_benefits,
                relocation_relief=year_1_relocation_relief,
            )
            year_2_taxable_benefits = calculate_uk_taxable_benefits(
                benefits=year_2_benefits,
                relocation_relief=year_2_relocation_relief,
            )
            year_1_accommodation = assess_employer_accommodation(
                annual_housing_cost=year_1_benefits["housing"],
                assumed_taxable_value=year_1_benefits["housing"],
            )
            year_2_accommodation = assess_employer_accommodation(
                annual_housing_cost=year_2_benefits["housing"],
                assumed_taxable_value=year_2_benefits["housing"],
            )
            year_1_total_taxable_benefits = calculate_total_taxable_benefits(
                taxable_benefits=year_1_taxable_benefits,
                accommodation=year_1_accommodation,
            )
            year_2_total_taxable_benefits = calculate_total_taxable_benefits(
                taxable_benefits=year_2_taxable_benefits,
                accommodation=year_2_accommodation,
            )
            annual_gross_income_chf = (
                form.cleaned_data["base_salary"]
                + form.cleaned_data["bonus"]
            )
            exchange_rate = form.cleaned_data["exchange_rate"]
            hypothetical_swiss_tax = calculate_total_hypothetical_swiss_tax(
                annual_gross_income_chf=annual_gross_income_chf,
                exchange_rate=exchange_rate,
            )
            swiss_employer_social_security = calculate_swiss_employer_social_security(
                annual_gross_income_chf
            )
            swiss_employer_social_security_gbp = (
                swiss_employer_social_security["total_chf"]
                / exchange_rate
            )
            protected_net_home_pay = calculate_protected_net_home_pay(
                home_pay=home_pay,
                hypothetical_social_security=hypothetical_social_security,
                hypothetical_swiss_tax=hypothetical_swiss_tax,
            )
            year_1_uk_tax_inputs = prepare_uk_taxable_income(
                pay_after_social_security=pay_after_social_security,
                total_taxable_benefits=year_1_total_taxable_benefits,
                hypothetical_swiss_income_tax_gbp=hypothetical_swiss_tax["total_tax_gbp"],
            )
            year_2_uk_tax_inputs = prepare_uk_taxable_income(
                pay_after_social_security=pay_after_social_security,
                total_taxable_benefits=year_2_total_taxable_benefits,
                hypothetical_swiss_income_tax_gbp=hypothetical_swiss_tax["total_tax_gbp"],
            )
            year_1_uk_tax_gross_up = calculate_tax_gross_up(
                year_1_uk_tax_inputs["taxable_income_before_gross_up"]
            )
            year_2_uk_tax_gross_up = calculate_tax_gross_up(
                year_2_uk_tax_inputs["taxable_income_before_gross_up"]
            )
            year_1_final_cost = calculate_final_employer_cost(
                home_pay_gbp=home_pay["total_home_pay_gbp"],
                assignment_benefits_gbp=year_1_benefits["total"],
                uk_tax_gross_up_gbp=year_1_uk_tax_gross_up,
                employer_social_security_gbp=swiss_employer_social_security_gbp,
                hypothetical_swiss_income_tax_gbp=hypothetical_swiss_tax["total_tax_gbp"],
                hypothetical_swiss_social_security_gbp=hypothetical_social_security["total_gbp"],
            )
            year_2_final_cost = calculate_final_employer_cost(
                home_pay_gbp=home_pay["total_home_pay_gbp"],
                assignment_benefits_gbp=year_2_benefits["total"],
                uk_tax_gross_up_gbp=year_2_uk_tax_gross_up,
                employer_social_security_gbp=swiss_employer_social_security_gbp,
                hypothetical_swiss_income_tax_gbp=hypothetical_swiss_tax["total_tax_gbp"],
                hypothetical_swiss_social_security_gbp=hypothetical_social_security["total_gbp"],
            )
            final_two_year_total = (
                year_1_final_cost["total_employer_cost_gbp"]
                + year_2_final_cost["total_employer_cost_gbp"]
            )
            two_year_home_pay = home_pay["total_home_pay_gbp"] * 2
            final_two_year_multiple = (
                final_two_year_total / two_year_home_pay
                if two_year_home_pay > 0
                else None
            )
            results = {
                "home_pay": home_pay,
                "year_1_benefits": year_1_benefits,
                "year_2_benefits": year_2_benefits,
                "hypothetical_social_security": hypothetical_social_security,
                "pay_after_social_security": pay_after_social_security,
                "year_1_summary": year_1_summary,
                "year_2_summary": year_2_summary,
                "two_year_total": two_year_total,
                "year_1_relocation_relief": year_1_relocation_relief,
                "year_2_relocation_relief": year_2_relocation_relief,
                "year_1_taxable_benefits": year_1_taxable_benefits,
                "year_2_taxable_benefits": year_2_taxable_benefits,
                "year_1_accommodation": year_1_accommodation,
                "year_2_accommodation": year_2_accommodation,
                "year_1_total_taxable_benefits": year_1_total_taxable_benefits,
                "year_2_total_taxable_benefits": year_2_total_taxable_benefits,
                "hypothetical_swiss_tax": hypothetical_swiss_tax,
                "swiss_employer_social_security": swiss_employer_social_security,
                "swiss_employer_social_security_gbp": swiss_employer_social_security_gbp,
                "year_1_uk_tax_inputs": year_1_uk_tax_inputs,
                "year_2_uk_tax_inputs": year_2_uk_tax_inputs,
                "protected_net_home_pay": protected_net_home_pay,
                "year_1_uk_tax_gross_up": year_1_uk_tax_gross_up,
                "year_2_uk_tax_gross_up": year_2_uk_tax_gross_up,
                "year_1_final_cost": year_1_final_cost,
                "year_2_final_cost": year_2_final_cost,
                "final_two_year_total": final_two_year_total,
                "final_two_year_multiple": final_two_year_multiple,
            }
            return render(
                request,
                "estimator/home.html",
                {
                    "form": form,
                    "assignment_data": assignment_data,
                    "results": results,
                }
            )
    else:
        form = AssignmentForm()
    return render(
        request,
        "estimator/home.html",
        {"form": form}
    )
