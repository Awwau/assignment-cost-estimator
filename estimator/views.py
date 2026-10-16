
from django.shortcuts import render
from .forms import AssignmentForm

from .services.assignment_cost import (
    calculate_home_pay,
    calculate_assignment_benefits,
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

            # Store the results for the HTML template
            results = {
                "home_pay": home_pay,
                "year_1_benefits": year_1_benefits,
                "year_2_benefits": year_2_benefits,
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
