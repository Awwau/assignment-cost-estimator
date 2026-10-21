
from django import forms


class AssignmentForm(forms.Form):
    home_country = forms.ChoiceField(
        choices=[("CH", "Switzerland")],
        initial="CH",
        label="Home country",
    )

    host_country = forms.ChoiceField(
        choices=[("GB", "United Kingdom")],
        initial="GB",
        label="Host country",
    )

    home_city = forms.ChoiceField(
        choices=[("Zurich", "Zurich")],
        initial="Zurich",
        label="Home city",
    )

    host_city = forms.ChoiceField(
        choices=[("London", "London")],
        initial="London",
        label="Host city",
    )

    start_date = forms.DateField(
        initial="2026-04-06",
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Assignment start date",
    )

    end_date = forms.DateField(
        initial="2028-04-05",
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Assignment end date",
    )

    nationality = forms.ChoiceField(
        choices=[("CH", "Swiss")],
        initial="CH",
        label="Employee nationality",
    )

    years_employed = forms.IntegerField(
        min_value=0,
        initial=3,
        label="Years with employer",
    )

    base_salary = forms.DecimalField(
        min_value=0,
        initial=150000,
        decimal_places=2,
        label="Annual base salary (CHF)",
    )

    bonus = forms.DecimalField(
        min_value=0,
        initial=20000,
        decimal_places=2,
        label="Annual bonus (CHF)",
    )

    housing = forms.DecimalField(
        min_value=0,
        initial=3000,
        decimal_places=2,
        label="Monthly housing cost in London  (GBP)",
    )

    relocation = forms.DecimalField(
        min_value=0,
        initial=5000,
        decimal_places=2,
        label="Relocation allowance (CHF)",
    )

    moving_costs = forms.DecimalField(
        min_value=0,
        initial=6000,
        decimal_places=2,
        label="Moving costs (GBP)",
    )

    temporary_housing = forms.DecimalField(
        min_value=0,
        initial=4000,
        decimal_places=2,
        label="Temporary housing (GBP)",
    )

    exchange_rate = forms.DecimalField(
        min_value=0.000001,
        initial=1.10,
        decimal_places=6,
        label="Exchange rate (GBP to CHF)",
    )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError(
                    "The assignment end date must be after the start date."
                )

        return cleaned_data
