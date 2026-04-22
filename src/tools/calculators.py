"""
Finance calculators — ported from the Digital Smart Finance Calculator notebook.

All rates are passed as decimals (e.g. 0.05 for 5%).
`n_compounds` is the compounding frequency per year:
    1 = annual, 2 = semi-annual, 4 = quarterly, 12 = monthly,
    52 = weekly, 365 = daily.
"""
from __future__ import annotations


def calculate_simple_interest(principal: float, rate: float, time: float) -> float:
    """Simple interest: I = P * r * t."""
    return principal * rate * time


def calculate_compound_interest(
    principal: float, rate: float, time: float, n_compounds: int = 1
) -> float:
    """
    Total amount after compound interest:
        A = P * (1 + r/n)^(n*t)
    Returns the full amount (principal + interest).
    """
    return principal * (1 + (rate / n_compounds)) ** (n_compounds * time)


def calculate_future_value(
    principal: float, rate: float, time: float, n_compounds: int = 1
) -> float:
    """
    Future Value of a lump sum:
        FV = PV * (1 + r/n)^(n*t)
    """
    return principal * (1 + (rate / n_compounds)) ** (n_compounds * time)


def calculate_present_value(
    future_value: float, rate: float, time: float, n_compounds: int = 1
) -> float:
    """
    Present Value of a future lump sum:
        PV = FV / (1 + r/n)^(n*t)
    """
    return future_value / ((1 + (rate / n_compounds)) ** (n_compounds * time))


def calculate_future_value_annuity(
    payment: float, rate: float, time: float, n_compounds: int = 1
) -> float:
    """
    Future Value of an Ordinary Annuity (payments at end of period):
        FVA = P * [((1 + r/n)^(n*t) - 1) / (r/n)]
    """
    periodic_rate = rate / n_compounds
    total_payments = n_compounds * time
    if periodic_rate == 0:
        return payment * total_payments
    return payment * (((1 + periodic_rate) ** total_payments - 1) / periodic_rate)


def calculate_present_value_annuity(
    payment: float, rate: float, time: float, n_compounds: int = 1
) -> float:
    """
    Present Value of an Ordinary Annuity:
        PVA = P * [(1 - (1 + r/n)^(-n*t)) / (r/n)]
    """
    periodic_rate = rate / n_compounds
    total_periods = n_compounds * time
    if periodic_rate == 0:
        return payment * total_periods
    return payment * ((1 - (1 + periodic_rate) ** (-total_periods)) / periodic_rate)


# Frequency lookup used by the Streamlit UI
COMPOUND_FREQUENCIES = {
    "Annually (1/yr)":    1,
    "Semi-annually (2/yr)": 2,
    "Quarterly (4/yr)":   4,
    "Monthly (12/yr)":    12,
    "Weekly (52/yr)":     52,
    "Daily (365/yr)":     365,
}
