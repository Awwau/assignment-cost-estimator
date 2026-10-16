
from django.shortcuts import render
from .forms import AssignmentForm

from .services.assignment_cost import (
    calculate_home_pay,
    calculate_assignment_benefits,
)
from .services.assignment_cost import (
    calculate_home_pay,
    calculate_assignment_benefits,
    calculate_hypothetical_social_security,
)
from .services.assignment_cost import (
    calculate_home_pay,
    calculate_assignment_benefits,
    calculate_hypothetical_social_security,
    calculate_pay_after_social_security,
)
from .services.assignment_cost import (
    calculate_home_pay,
    calculate_assignment_benefits,
    calculate_hypothetical_social_security,
    calculate_pay_after_social_security,
    calculate_annual_cost_summary,
)


def home(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)

        if form.is_valid():
            assignment_data = form.cleaned_data

            # Calculate annual salary and bonus
            home_pay = calculate_home_pay(
                base_salary=assignment_data["base_salary"],
                bonus=assignment_data["bonus"],
                exchange_rate=assignment_data["exchange_rate"],
            )

            # Calculate first-year benefits
            year_1_benefits = calculate_assignment_benefits(
                monthly_housing=assignment_data["housing"],
                relocation_chf=assignment_data["relocation"],
                moving_costs=assignment_data["moving_costs"],
                temporary_housing=assignment_data["temporary_housing"],
                exchange_rate=assignment_data["exchange_rate"],
                assignment_year=1,
            )

            # Calculate second-year benefits
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



            # Store the results for the HTML template
            results = {
                "home_pay": home_pay,
                "year_1_benefits": year_1_benefits,
                "year_2_benefits": year_2_benefits,
                "hypothetical_social_security": hypothetical_social_security,
                "pay_after_social_security": pay_after_social_security,
                "year_1_summary": year_1_summary,
                "year_2_summary": year_2_summary,
                "two_year_total": two_year_total,
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
