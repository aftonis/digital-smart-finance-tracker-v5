"""
Unit tests for src/tools/calculators.py
All expected values are cross-verified against the original
Digital_Smart_Finance_Calculator.ipynb notebook outputs.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools.calculators import (
    calculate_simple_interest,
    calculate_compound_interest,
    calculate_future_value,
    calculate_present_value,
    calculate_future_value_annuity,
    calculate_present_value_annuity,
    COMPOUND_FREQUENCIES,
)


# ── Simple Interest ────────────────────────────────────────────────────────────

class TestSimpleInterest:
    def test_notebook_example(self):
        """$1,000 @ 5% for 3 years = $150 interest (notebook reference)."""
        assert calculate_simple_interest(1000, 0.05, 3) == pytest.approx(150.0)

    def test_zero_rate(self):
        assert calculate_simple_interest(5000, 0.0, 10) == 0.0

    def test_zero_time(self):
        assert calculate_simple_interest(1000, 0.08, 0) == 0.0

    def test_proportional_to_principal(self):
        i1 = calculate_simple_interest(1000, 0.05, 5)
        i2 = calculate_simple_interest(2000, 0.05, 5)
        assert i2 == pytest.approx(i1 * 2)


# ── Compound Interest ──────────────────────────────────────────────────────────

class TestCompoundInterest:
    def test_notebook_example(self):
        """$1,000 @ 5% monthly for 3 years = $1,161.47 total (notebook)."""
        result = calculate_compound_interest(1000, 0.05, 3, 12)
        assert result == pytest.approx(1161.47, abs=0.01)

    def test_annual_compounding(self):
        """$1,000 @ 10% annually for 2 years = $1,210."""
        assert calculate_compound_interest(1000, 0.10, 2, 1) == pytest.approx(1210.0, abs=0.01)

    def test_zero_rate_returns_principal(self):
        assert calculate_compound_interest(5000, 0.0, 10, 12) == pytest.approx(5000.0)

    def test_more_compounding_gives_more(self):
        annual   = calculate_compound_interest(1000, 0.05, 1, 1)
        monthly  = calculate_compound_interest(1000, 0.05, 1, 12)
        daily    = calculate_compound_interest(1000, 0.05, 1, 365)
        assert daily > monthly > annual


# ── Future Value ──────────────────────────────────────────────────────────────

class TestFutureValue:
    def test_notebook_example(self):
        """$1,000 @ 5% quarterly for 10 years = $1,643.62 (notebook)."""
        result = calculate_future_value(1000, 0.05, 10, 4)
        assert result == pytest.approx(1643.62, abs=0.01)

    def test_zero_rate(self):
        assert calculate_future_value(2500, 0.0, 5, 12) == pytest.approx(2500.0)

    def test_longer_time_means_more(self):
        fv5  = calculate_future_value(1000, 0.05, 5,  4)
        fv10 = calculate_future_value(1000, 0.05, 10, 4)
        assert fv10 > fv5


# ── Present Value ─────────────────────────────────────────────────────────────

class TestPresentValue:
    def test_notebook_example(self):
        """PV of $1,643.62 @ 5% quarterly in 10 years = $1,000 (notebook)."""
        result = calculate_present_value(1643.62, 0.05, 10, 4)
        assert result == pytest.approx(1000.0, abs=0.01)

    def test_second_notebook_example(self):
        """PV of $50,000 @ 8% monthly in 20 years = $10,148.57 (notebook)."""
        result = calculate_present_value(50000, 0.08, 20, 12)
        assert result == pytest.approx(10148.57, abs=0.01)

    def test_pv_fv_roundtrip(self):
        """FV then PV with same params must return original principal."""
        principal = 3750.0
        fv = calculate_future_value(principal, 0.06, 8, 12)
        pv = calculate_present_value(fv, 0.06, 8, 12)
        assert pv == pytest.approx(principal, abs=0.01)

    def test_higher_rate_means_lower_pv(self):
        pv5 = calculate_present_value(10000, 0.05, 10, 4)
        pv8 = calculate_present_value(10000, 0.08, 10, 4)
        assert pv5 > pv8


# ── Future Value Annuity ──────────────────────────────────────────────────────

class TestFutureValueAnnuity:
    def test_notebook_example(self):
        """$100/mo @ 5% monthly for 10 years = $15,528.23 (notebook)."""
        result = calculate_future_value_annuity(100, 0.05, 10, 12)
        assert result == pytest.approx(15528.23, abs=0.01)

    def test_zero_rate(self):
        """With 0% rate FVA = payment × total_periods."""
        result = calculate_future_value_annuity(100, 0.0, 10, 12)
        assert result == pytest.approx(100 * 12 * 10)

    def test_higher_rate_means_more(self):
        fva5  = calculate_future_value_annuity(100, 0.05, 10, 12)
        fva10 = calculate_future_value_annuity(100, 0.10, 10, 12)
        assert fva10 > fva5


# ── Present Value Annuity ────────────────────────────────────────────────────

class TestPresentValueAnnuity:
    def test_notebook_example(self):
        """$200/mo @ 7% monthly for 5 years = $10,100.40 (notebook)."""
        result = calculate_present_value_annuity(200, 0.07, 5, 12)
        assert result == pytest.approx(10100.40, abs=0.01)

    def test_zero_rate(self):
        """With 0% rate PVA = payment × total_periods."""
        result = calculate_present_value_annuity(200, 0.0, 5, 12)
        assert result == pytest.approx(200 * 12 * 5)

    def test_higher_rate_means_less_pv(self):
        pva5  = calculate_present_value_annuity(200, 0.05, 5, 12)
        pva10 = calculate_present_value_annuity(200, 0.10, 5, 12)
        assert pva5 > pva10


# ── COMPOUND_FREQUENCIES lookup ───────────────────────────────────────────────

class TestCompoundFrequencies:
    def test_all_keys_present(self):
        for label in ["Annually (1/yr)", "Semi-annually (2/yr)", "Quarterly (4/yr)",
                      "Monthly (12/yr)", "Weekly (52/yr)", "Daily (365/yr)"]:
            assert label in COMPOUND_FREQUENCIES

    def test_values_correct(self):
        assert COMPOUND_FREQUENCIES["Annually (1/yr)"]     == 1
        assert COMPOUND_FREQUENCIES["Quarterly (4/yr)"]    == 4
        assert COMPOUND_FREQUENCIES["Monthly (12/yr)"]     == 12
        assert COMPOUND_FREQUENCIES["Daily (365/yr)"]      == 365
