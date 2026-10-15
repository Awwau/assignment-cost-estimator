from django.shortcuts import render
from .forms import AssignmentForm


def home(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)

        if form.is_valid():
            assignment_data = form.cleaned_data

            return render(
                request,
                "estimator/home.html",
                {
                    "form": form,
                    "assignment_data": assignment_data
                }
            )
    else:
        form = AssignmentForm()

    return render(
        request,
        "estimator/home.html",
        {"form": form}
    )
