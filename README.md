# Assignment Cost Estimator

A Django web application that estimates the employer cost of a two-year international assignment from Zurich, Switzerland, to London, United Kingdom, under a **tax-equalisation** arrangement.

The application presents year-by-year and combined employer-cost estimates, explains the underlying calculations and assumptions, and provides an immigration information tab with links to official guidance.

> **Scope:** This is a technical-assessment prototype and a provisional financial model, not a production payroll, tax, legal, or immigration advisory service.

## Scenario

The example assignment assumes a Swiss employee transferring to a UK subsidiary for two years, from **6 April 2026 to 5 April 2028**. The employee is single, has no children, has worked for the Swiss employer for three years, and is treated as UK tax resident during the assignment.

The default inputs are:

| Input | Default |
| --- | ---: |
| Annual salary | CHF 150,000 |
| Annual bonus | CHF 20,000 |
| Employer-paid housing | £3,000 per month |
| Year 1 cash relocation allowance | CHF 5,000 |
| Year 1 moving costs | £6,000 |
| Year 1 temporary accommodation | £4,000 |
| Exchange rate | £1 = CHF 1.10 |

The form allows the user to change relevant inputs and recalculate the estimates.

## Features

- Validated assignment input form.
- Separate **Year 1** and **Year 2** employer-cost estimates.
- Two-year total and cost multiples relative to home pay; undefined multiples are shown as **N/A** when home pay is zero.
- UK income tax calculation with iterative **tax-on-tax gross-up**.
- Estimated Swiss hypothetical federal and Zurich cantonal/municipal income taxes.
- Swiss employee and employer social security estimates for **AHV/IV/EO and ALV**.
- Classification of cash payments, accommodation benefits and potentially qualifying relocation costs.
- Calculation breakdowns and explanatory notes.
- Immigration guidance with references to official UK government information.
- Responsive web interface.
- Automated Django tests.

## Technology

- **Python 3.12**
- **Django** (see `requirements.txt` for the pinned version)
- **HTML, CSS and JavaScript**
- **SQLite** for local development
- Django's built-in testing framework

## Video Walkthrough

A short demonstration of the Assignment Cost Estimator, including the user interface, cost calculations, immigration guidance, Django backend and automated tests.

**[Watch the Loom walkthrough](https://www.loom.com/share/1280fc04593b4783a00db6f5409f7313)**

## Quick Start (Windows PowerShell)

### Prerequisites

- Python 3.12 installed and available as `python`.
- Git, if cloning the repository.

### 1. Get the project

```powershell
git clone https://github.com/Awwau/assignment-cost-estimator.git
cd assignment-cost-estimator
```


### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can temporarily allow scripts for the **current terminal session only**:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Only use this workaround if you trust the local activation script. The prompt should now show `(.venv)`.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Set development environment variables

```powershell
$env:DJANGO_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(64))"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_USE_HTTPS = "False"
```

These values are for **local development only** and last for the current PowerShell session. Set them again in a new terminal. Never commit real secret keys or credentials.

### 5. Apply migrations

```powershell
python manage.py migrate
```

### 6. Start the application

```powershell
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser. Stop the server with **Ctrl+C**.

### 7. Run tests

```powershell
python manage.py test estimator
```

At the time of this README update, **20 automated tests pass**. The tests exercise the application's calculations and behaviour, including a zero-home-pay regression case. The number may change as the project develops.

## Calculation Methodology

The estimator uses a simplified tax-equalisation approach intended to illustrate the components of assignment cost.

**1. Convert compensation to GBP.** Annual Swiss salary and bonus are combined and converted using the input exchange rate.

**2. Estimate hypothetical Swiss deductions.** The model estimates Swiss employee AHV/IV/EO and ALV contributions and hypothetical Swiss income tax using its implemented federal and Zurich assumptions.

**3. Calculate protected net home pay.** Hypothetical Swiss employee social security and income tax are deducted from gross home pay. As an explicit edge-case convention, deductions *applied against home pay* are capped at available gross home pay, so protected net home pay cannot be negative. The underlying hypothetical tax estimate is still retained for transparency.

**4. Classify assignment benefits.** Employer-paid housing is treated as a taxable benefit at an assumed value equal to its cost. Cash relocation is treated as taxable; qualifying moving and temporary accommodation expenses are considered under the model's relocation-relief assumptions. The first year includes the one-off relocation amounts; the second year does not.

**5. Calculate UK income tax gross-up.** The model uses its England 2026/27 income tax rules, including personal allowance tapering, and iteratively calculates the additional employer-paid tax required when the employer's tax payment is itself taxable.

**6. Estimate employer cost.** For each year:

```text
Employer cost
  = Gross home pay
  + Assignment benefits
  + Employer-paid UK income tax (including gross-up)
  + Estimated Swiss employer social security
  - Hypothetical Swiss deductions applied
```

The two-year total is the sum of both years. Cost multiples divide estimated employer cost by the corresponding home-pay amount and are displayed as **N/A** when the denominator is zero.

All calculations are **illustrative**, not certified tax computations. Small differences of a penny may arise from decimal precision and display rounding.

## Key Assumptions and Limitations

| Area | Assumption or limitation |
| --- | --- |
| Exchange rate | User-supplied fixed CHF/GBP rate; no exchange-rate forecast or currency fluctuations. |
| UK income tax | England **2026/27** rules are applied to both years for modelling purposes; Year 2 legislation may differ. |
| Tax equalisation | Simplified protected-net-pay and gross-up method; not a full shadow-payroll or tax-return calculation. |
| Swiss income tax | Provisional federal and Zurich estimates based on implemented brackets, multipliers and employment-expense deductions; not a full individual Swiss assessment. |
| Swiss social security | Models **AHV/IV/EO and ALV only**. Occupational pension, accident insurance, family allowance contributions and other possible employer charges are outside the estimate. |
| Posting coverage | Continued Swiss social security coverage is assumed for modelling; actual cross-border coverage and documentation must be confirmed. |
| Housing | The model assumes the accommodation's taxable value equals employer-paid rent. Actual UK benefit valuation and any exemptions require verification. |
| Relocation relief | Qualifying expense treatment and any applicable relief limits depend on the facts and current HMRC rules; the model does not establish eligibility. |
| UK payroll and tax | Actual PAYE, National Insurance, treaty, payroll reporting and benefit treatment may require additional analysis and could change the result. |
| Zero income | Applied hypothetical deductions are capped at available home pay; this is a **modelling convention**, not a rule cancelling Swiss tax liability. |
| Other costs | Visa fees, immigration health surcharge, advisory fees, employer administration and other assignment costs are not necessarily included in the financial estimate. |

## Immigration Guidance

The **Immigration** tab discusses the potential **Global Business Mobility – Senior or Specialist Worker** route, relevant sponsorship and eligibility considerations, restrictions on visitor status, and supporting documentation and costs.

This section is informational. Visa suitability, sponsorship rules, fees and processing times must be checked against current official UK government guidance before any application.

Official starting points:

- [Senior or Specialist Worker visa — GOV.UK](https://www.gov.uk/senior-specialist-worker-visa)
- [UK visa and immigration information — GOV.UK](https://www.gov.uk/browse/visas-immigration)
- [Income Tax rates and allowances — GOV.UK](https://www.gov.uk/income-tax-rates)
- [Tax on relocation expenses — GOV.UK](https://www.gov.uk/expenses-and-benefits-relocation)

Additional source explanations are available in the application's calculation details.

## Security and Production Deployment

The project reads its Django secret key and development settings from environment variables rather than hardcoding a key in source code. **Do not publish `.env` files, secrets, local databases or virtual environments.**

The Quick Start instructions run Django's **development server**. They do **not** constitute a production deployment. Before hosting the application publicly, at minimum:

1. Set a stable, private `DJANGO_SECRET_KEY` in the hosting environment and set `DJANGO_DEBUG=False`.
2. Configure appropriate allowed hosts, trusted origins and HTTPS settings for the actual domain.
3. Run `python manage.py check --deploy` and address applicable warnings.
4. Use a production-capable application server and configure static-file serving.
5. Review dependency versions, logging, database persistence, backup strategy and access controls.
6. Confirm that the application's security-related settings match the hosting platform before enabling HTTPS redirects or secure cookies.

The current project is intended to be evaluated **locally** unless a separate deployment configuration is provided. No public production deployment is claimed.

## AI Tools Used

**ChatGPT (OpenAI)** was used as a development assistant to support project planning, explain Django and Python concepts, review code, troubleshoot errors, improve documentation, and suggest testing approaches.

AI-generated suggestions were reviewed and adapted during development. The application's calculations, assumptions and functionality were checked through manual testing, automated tests and reference to relevant official sources.


## Project Status

Technical-assessment prototype. Estimates, especially Swiss taxation, accommodation treatment and immigration information, remain provisional and subject to independent verification.

## Disclaimer

This application is for educational and technical-assessment purposes. It does not provide financial, payroll, tax, legal or immigration advice. Users should consult appropriately qualified professionals and current official guidance before making employment, assignment or immigration decisions.
