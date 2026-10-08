"""Controls for the dated public-data case, including its incomplete inventory."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import sf_agent.analytics as analytics


REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "examples" / "integrated-portfolio"
spec = importlib.util.spec_from_file_location("integrated_portfolio", CASE / "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class IntegratedPortfolioTests(unittest.TestCase):
    def setUp(self):
        self.inputs = json.loads((CASE / "inputs.json").read_text())
        self.sources = json.loads((CASE / "sources.json").read_text())
        self.handoffs = json.loads((CASE / "handoffs.json").read_text())

    def test_missing_scope_and_capital_are_unassessed_not_zero(self):
        results = model.calculate(self.inputs, self.sources)
        for snapshot, expected_coverage in zip(results["inventories"], (0.20, 0.25)):
            for scope in model.SCOPES:
                metric = snapshot["inventory"]["scopes"][scope]
                self.assertEqual(metric["fe_coverage_fraction"], expected_coverage)
                self.assertIsNone(metric["complete_in_scope_financed_tco2e"])
                self.assertIsNone(metric["quality_exposure_weighted"])
            self.assertIsNone(snapshot["constructed_evic_usd"]["MSFT"])
        self.assertIsNone(self.inputs["snapshots"][0]["issuers"][-1]["scope3_tco2e"])
        # A reported zero is covered data; an unavailable value is not.
        changed = copy.deepcopy(self.inputs)
        ibm = changed["snapshots"][0]["issuers"][-1]
        ibm["scope3_tco2e"] = 0
        ibm["source_refs"]["scope3_tco2e"] = copy.deepcopy(ibm["source_refs"]["scope12_tco2e"])
        actual = model.calculate(changed, self.sources)["inventories"][0]["inventory"]
        self.assertEqual(actual["scopes"]["scope3_tco2e"]["waci_market_coverage_of_in_scope"], 1)
        self.assertEqual(actual["scopes"]["scope3_tco2e"]["waci_observed_contribution_full_portfolio_denominator"],
                         results["inventories"][0]["inventory"]["scopes"]["scope3_tco2e"]["waci_observed_contribution_full_portfolio_denominator"])

    def test_evic_includes_both_share_classes_and_liabilities_once(self):
        old, new = self.inputs["snapshots"]
        components = old["issuers"][2]["evic_components"]
        self.assertAlmostEqual(model.construct_evic(components),
                               ((2211 + 350) * 353.96 + 76455) * 1_000_000)
        self.assertAlmostEqual(model.construct_evic(new["issuers"][2]["evic_components"]),
                               ((2190 + 344) * 585.51 + 93417) * 1_000_000)
        incomplete = copy.deepcopy(components)
        incomplete["class_b_shares_m"] = None
        self.assertIsNone(model.construct_evic(incomplete))
        components["cash_deduction_usd_m"] = 1
        with self.assertRaisesRegex(ValueError, "deduct cash"):
            model.construct_evic(components)

    def test_incompatible_dates_currency_or_denominator_are_rejected(self):
        for field, value, error in (("revenue_year", 2022, "years must match"),
                                    ("revenue_period_end", "2023-12-31", "year-ends"),
                                    ("currency", "EUR", "FX conversion"),
                                    ("revenue_usd_m", 0, "positive")):
            changed = copy.deepcopy(self.inputs["snapshots"][0])
            changed["issuers"][0][field] = value
            with self.assertRaisesRegex(ValueError, error):
                model.holdings(changed)
        changed = copy.deepcopy(self.inputs["snapshots"][0])
        changed["issuers"][2]["evic_components"]["date"] = "2024-12-31"
        with self.assertRaisesRegex(ValueError, "holding dates"):
            model.holdings(changed)
        changed["issuers"][2]["evic_components"]["date"] = "2023-12-31"
        changed["issuers"][0]["emissions_period_end"] = "2024-06-30"
        changed["issuers"][0]["revenue_period_end"] = "2024-06-30"
        with self.assertRaisesRegex(ValueError, "precede the holding date"):
            model.holdings(changed)

    def test_negative_nan_and_invalid_weights_do_not_enter_accounting(self):
        for value in (-1, float("nan"), float("inf"), True):
            changed = copy.deepcopy(self.inputs["snapshots"][0])
            changed["issuers"][0]["scope12_tco2e"] = value
            with self.assertRaises(ValueError):
                model.holdings(changed)
        changed = copy.deepcopy(self.inputs["snapshots"][0])
        changed["issuers"][0]["illustrative_weight"] = 0.31
        with self.assertRaisesRegex(ValueError, "sum to one"):
            model.holdings(changed)

    def test_shapley_attributes_single_factor_and_reconciles_public_case(self):
        bridge = model.shapley_waci(.1, 100, 1_000_000, .2, 100, 1_000_000)
        self.assertAlmostEqual(bridge["holdings_weight_effect"], 10)
        self.assertEqual(bridge["reported_emissions_effect"], 0)
        self.assertEqual(bridge["revenue_denominator_effect"], 0)
        result = model.calculate(self.inputs, self.sources)
        for method in ("waci_attribution", "financed_emissions_attribution"):
            for scope in model.SCOPES:
                bridge = result[method][scope]
                self.assertAlmostEqual(sum(bridge["effects"].values()), bridge["delta"], places=10)
                self.assertAlmostEqual(bridge["reconciliation_residual"], 0, places=10)
        self.assertAlmostEqual(result["waci_attribution"]["scope12_tco2e"]["delta"],
                               6.909310896469366 - 9.129864092486727)

    def test_report_is_identical_under_old_and_new_float_sum(self):
        def legacy_sum(values, start=0):
            # Python <=3.11 sums floats left to right; 3.12 compensates error.
            total = start
            for value in values:
                total += value
            return total
        normal = model.calculate(self.inputs, self.sources)
        with patch.object(model, "sum", legacy_sum, create=True), \
                patch.object(analytics, "sum", legacy_sum, create=True):
            legacy = model.calculate(self.inputs, self.sources)
        self.assertEqual(normal, legacy)
        self.assertEqual(model.digest(normal), model.digest(legacy))
        self.assertEqual(normal["input_sha256"], model.digest(self.inputs))
        self.assertEqual(normal["source_ledger_sha256"], model.digest(self.sources))

    def test_report_rounding_preserves_inputs_and_rejects_actual_bridge_errors(self):
        number = 1.2345678901234567
        report = model.canonical_report({"calculated": number, "integer": 17,
                                         "flag": False, "missing": None,
                                         "reconciliation_residual": 1.4e-14})
        self.assertEqual(report["calculated"], 1.23456789012)
        self.assertEqual(type(report["integer"]), int)
        self.assertIs(report["flag"], False)
        self.assertIsNone(report["missing"])
        self.assertEqual(report["reconciliation_residual"], 0)
        self.assertEqual(number, 1.2345678901234567)
        with self.assertRaisesRegex(ValueError, "raw attribution"):
            model.canonical_report({"reconciliation_residual": 1e-7})
        with self.assertRaisesRegex(ValueError, "finite numbers"):
            model.canonical_report({"calculated": float("nan")})

    def test_changed_meta_scope3_basis_is_not_an_emissions_effect(self):
        result = model.calculate(self.inputs, self.sources)
        bridge = result["financed_emissions_attribution"]["scope3_tco2e"]
        self.assertEqual(bridge["effects"]["reported_emissions_effect"], 0)
        self.assertEqual(bridge["effects"]["boundary_changes"], bridge["delta"])
        detail = result["waci_attribution"]["scope3_tco2e"]["issuer_details"]
        self.assertEqual(next(r for r in detail if r["issuer_id"] == "META")["bucket"], "boundary_changes")
        self.assertEqual(next(r for r in detail if r["issuer_id"] == "IBM")["bucket"], "unassessed_both_periods")

    def test_facts_require_registered_locators_and_valid_primary_urls(self):
        changed = copy.deepcopy(self.inputs)
        changed["snapshots"][0]["issuers"][0]["source_refs"]["revenue_usd_m"]["id"] = "MISSING"
        with self.assertRaisesRegex(ValueError, "registered source"):
            model.calculate(changed, self.sources)
        sources = copy.deepcopy(self.sources)
        sources["sources"][0]["url"] = "https://example.org/broken url"
        with self.assertRaisesRegex(ValueError, "HTTPS URL"):
            model.validate_sources(self.inputs, sources)

    def test_site_evidence_and_proposed_handoffs_do_not_grant_authority(self):
        model.validate_handoffs(self.handoffs, self.inputs, self.sources)
        site = self.handoffs["nature_handoff"]
        self.assertEqual(site["location"]["site_label"], "Mesa, Arizona, United States")
        self.assertEqual(site["fact"]["value"], 57)
        self.assertEqual(site["fact"]["unit"], "megalitres")
        self.assertIsNone(site["location"]["precise_coordinates"])
        self.assertEqual(site["financial_mechanism"]["valuation_status"], "BLOCKED")
        for field, value in (("communication_sent", True), ("research_approval", "APPROVED"),
                             ("trade_or_voting_authority", True)):
            changed = copy.deepcopy(self.handoffs)
            changed[field] = value
            with self.assertRaisesRegex(ValueError, "proposed research"):
                model.validate_handoffs(changed, self.inputs, self.sources)
        result = model.calculate(self.inputs, self.sources)
        self.assertEqual(result["status"], "NEEDS_DATA")
        self.assertEqual(result["human_review"], "NOT_RECORDED")
        self.assertFalse(result["trade_or_communication_authority"])

    def test_committed_results_hashes_and_check_are_read_only(self):
        def hashes():
            return {str(p.relative_to(CASE)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in CASE.rglob("*") if p.is_file()}
        before = hashes()
        run = subprocess.run([sys.executable, str(CASE / "model.py"), "--check"],
                             cwd=REPO, capture_output=True, text=True, check=True)
        self.assertIn("two scopes reconcile", run.stdout)
        self.assertEqual(hashes(), before)
        result = json.loads((CASE / "results.json").read_text())
        self.assertEqual(result["input_sha256"], model.digest(self.inputs))
        self.assertEqual(result, model.calculate(self.inputs, self.sources))


if __name__ == "__main__":
    unittest.main()
