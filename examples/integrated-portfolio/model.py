"""Reproduce the public-data portfolio case without a data feed or an AI model.

The portfolio amounts are explicitly illustrative. Missing issuer data remains
unassessed; no synthetic issuer denominator is introduced to complete coverage.
"""
from __future__ import annotations

import argparse
import copy
from datetime import date
import hashlib
from itertools import permutations
import json
import math
from pathlib import Path
import sys

# Keep reproduction free of bytecode-cache writes in the repository as well.
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
from sf_agent.analytics import carbon_inventory, portfolio_emissions_attribution

SCOPES = ("scope12_tco2e", "scope3_tco2e")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def finite(value, name, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if value < 0 or (positive and value == 0):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return value


def construct_evic(components):
    """PCAF 2025 p42 fn45: use disclosed total liabilities, without cash netting.

    Class B equity is valued at the convertible Class A price. Rounded reported
    shares and inferred absence of preferred/minority equity remain explicit.
    """
    if components is None:
        return None
    fields = ("class_a_shares_m", "class_b_shares_m", "close_price_usd",
              "total_liabilities_usd_m", "preferred_equity_usd_m",
              "minority_interests_usd_m")
    if any(components.get(k) is None for k in fields):
        return None
    for k in fields:
        finite(components[k], k)
    if components.get("cash_deduction_usd_m", 0) != 0:
        raise ValueError("EVIC must not deduct cash")
    equity_m = ((components["class_a_shares_m"] + components["class_b_shares_m"])
                * finite(components["close_price_usd"], "price", positive=True))
    return (equity_m + components["total_liabilities_usd_m"]
            + components["preferred_equity_usd_m"]
            + components["minority_interests_usd_m"]) * 1_000_000


def holdings(snapshot):
    nav = finite(snapshot["illustrative_nav_usd"], "NAV", positive=True)
    holding_date = date.fromisoformat(snapshot["holdings_date"])
    rows = []
    seen = set()
    for item in snapshot["issuers"]:
        if item["issuer_id"] in seen:
            raise ValueError("duplicate issuer")
        seen.add(item["issuer_id"])
        weight = finite(item["illustrative_weight"], "weight")
        if item["currency"] != "USD":
            raise ValueError("explicit FX conversion is required for a non-USD record")
        if item["revenue_year"] != item["emissions_year"]:
            raise ValueError("revenue/emissions years must match")
        if item["revenue_period_end"] != item["emissions_period_end"]:
            raise ValueError("revenue/emissions fiscal year-ends must match")
        period_end = date.fromisoformat(item["revenue_period_end"])
        if period_end.year != item["revenue_year"] or period_end > holding_date:
            raise ValueError("fiscal year-end must match the year and precede the holding date")
        if item["evic_components"] is not None:
            if item["evic_components"]["date"] != snapshot["holdings_date"]:
                raise ValueError("EVIC and portfolio holding dates differ")
        revenue = finite(item["revenue_usd_m"], "revenue", positive=True) * 1_000_000
        for scope in SCOPES:
            if item[scope] is not None:
                finite(item[scope], scope)
        rows.append({
            "id": item["issuer_id"], "issuer_id": item["issuer_id"],
            "asset_type": "listed-equity", "issuer_is_listed": True,
            "amount_basis": "market_value", "currency": "USD",
            "financed_amount": nav * weight, "market_value": nav * weight,
            "financial_year": item["revenue_year"],
            "emissions_year": item["emissions_year"],
            "boundary_id": item["scope_boundaries"]["scope12_tco2e"],
            "revenue": revenue, "evic": construct_evic(item["evic_components"]),
            "scope12_tco2e": item["scope12_tco2e"], "scope3_tco2e": item["scope3_tco2e"],
            "quality_scope12": None, "quality_scope3": None,
            "scope_boundaries": item["scope_boundaries"],
            "issuer_estimation_status": item["issuer_estimation_status"],
        })
    if not math.isclose(sum(r["market_value"] for r in rows), nav, abs_tol=1e-6):
        raise ValueError("illustrative weights must sum to one")
    return rows


def shapley_waci(weight0, emissions0, revenue0, weight1, emissions1, revenue1):
    start = [weight0, emissions0, revenue0]
    end = [weight1, emissions1, revenue1]
    for values in (start, end):
        for i, value in enumerate(values):
            finite(value, f"factor {i}", positive=i == 2)
    def value(v):
        return v[0] * v[1] / (v[2] / 1_000_000)
    effects = [0.0, 0.0, 0.0]
    for order in permutations(range(3)):
        current = list(start)
        for i in order:
            before = value(current)
            current[i] = end[i]
            effects[i] += (value(current) - before) / 6
    delta = value(end) - value(start)
    return {"start": value(start), "end": value(end), "delta": delta,
            "holdings_weight_effect": effects[0], "reported_emissions_effect": effects[1],
            "revenue_denominator_effect": effects[2],
            "reconciliation_residual": delta - sum(effects)}


def waci_attribution(old, new, nav0, nav1, scope):
    a = {r["issuer_id"]: r for r in old}
    b = {r["issuer_id"]: r for r in new}
    names = ("holdings_weight_effect", "reported_emissions_effect",
             "revenue_denominator_effect", "coverage_changes", "boundary_changes",
             "entries", "exits")
    totals = dict.fromkeys(names, 0.0)
    details = []
    def contribution(row, nav):
        if row is None or row[scope] is None:
            return None
        return row["market_value"] / nav * row[scope] / (row["revenue"] / 1_000_000)
    for issuer in sorted(a.keys() | b.keys()):
        o, n = a.get(issuer), b.get(issuer)
        before, after = contribution(o, nav0), contribution(n, nav1)
        # Zero here is only the missing contribution to the OBSERVED statistic.
        # It is never a fabricated zero for issuer emissions or the portfolio.
        delta = (after or 0) - (before or 0)
        if o is None:
            bucket = "entries"
        elif n is None:
            bucket = "exits"
        elif before is None and after is None:
            bucket = "unassessed_both_periods"
        elif before is None or after is None:
            bucket = "coverage_changes"
        elif o["scope_boundaries"][scope] != n["scope_boundaries"][scope]:
            bucket = "boundary_changes"
        else:
            bridge = shapley_waci(o["market_value"] / nav0, o[scope], o["revenue"],
                                 n["market_value"] / nav1, n[scope], n["revenue"])
            for k in names[:3]:
                totals[k] += bridge[k]
            details.append({"issuer_id": issuer, "bucket": "comparable_reported_boundary",
                            "bridge": bridge})
            continue
        if bucket in totals:
            totals[bucket] += delta
        details.append({"issuer_id": issuer, "bucket": bucket, "observed_delta": delta})
    start = sum(contribution(r, nav0) or 0 for r in old)
    end = sum(contribution(r, nav1) or 0 for r in new)
    return {"scope": scope, "start_observed_full_denominator_contribution": start,
            "end_observed_full_denominator_contribution": end, "delta": end - start,
            "effects": totals, "reconciliation_residual": end - start - sum(totals.values()),
            "issuer_details": details, "physical_decarbonisation_proven": False,
            "fx_of_global_revenues_not_separately_identified": True}


def validate_sources(inputs, sources):
    ids = {s["id"] for s in sources["sources"]}
    if len(ids) != len(sources["sources"]):
        raise ValueError("duplicate source ID")
    for s in sources["sources"]:
        if (not s["url"].startswith("https://") or any(c.isspace() for c in s["url"])
                or not s["locator"]):
            raise ValueError("source needs an HTTPS URL and locator")
    for snapshot in inputs["snapshots"]:
        for issuer in snapshot["issuers"]:
            required = ("revenue_usd_m", "scope12_tco2e")
            if issuer["scope3_tco2e"] is not None:
                required += ("scope3_tco2e",)
            for field in required:
                ref = issuer["source_refs"][field]
                if ref["id"] not in ids or not ref["locator"]:
                    raise ValueError("numerical fact has no registered source locator")
            if issuer["evic_components"] is not None:
                for ref in issuer["evic_components"]["source_refs"]:
                    if ref["id"] not in ids or not ref["locator"]:
                        raise ValueError("EVIC component has no registered source locator")


def calculate(inputs, sources):
    validate_sources(inputs, sources)
    if inputs["classification"] != "ILLUSTRATIVE_HOLDINGS_WITH_REPORTED_ISSUER_DATA":
        raise ValueError("portfolio classification is required")
    if len(inputs["snapshots"]) != 2:
        raise ValueError("exactly two dated snapshots are required")
    previous, current = inputs["snapshots"]
    old, new = holdings(previous), holdings(current)
    if previous["holdings_date"] >= current["holdings_date"]:
        raise ValueError("snapshot dates must increase")
    inventories = [{"holdings_date": s["holdings_date"],
                    "inventory": carbon_inventory(h, s["illustrative_nav_usd"]),
                    "constructed_evic_usd": {r["issuer_id"]: r["evic"] for r in h}}
                   for s, h in ((previous, old), (current, new))]
    financed = {}
    waci = {}
    for scope in SCOPES:
        x, y = copy.deepcopy(old), copy.deepcopy(new)
        for row in x + y:
            row["boundary_id"] = row["scope_boundaries"][scope]
        financed[scope] = portfolio_emissions_attribution(x, y, scope)
        waci[scope] = waci_attribution(old, new, previous["illustrative_nav_usd"],
                                       current["illustrative_nav_usd"], scope)
    return {"schema_version": "1.0.0", "information_cutoff": inputs["information_cutoff"],
            "input_sha256": digest(inputs), "source_ledger_sha256": digest(sources),
            "classification": inputs["classification"], "status": "NEEDS_DATA",
            "human_review": "NOT_RECORDED", "research_approval": "NOT_GRANTED",
            "trade_or_communication_authority": False,
            "backtest_or_actual_holdings": False, "inventories": inventories,
            "financed_emissions_attribution": financed, "waci_attribution": waci,
            "open_material_issues": inputs["open_material_issues"]}


def provenance(inputs, sources, results, handoffs):
    files = ("model.py", "inputs.json", "sources.json", "results.json", "handoffs.json")
    return {"hash_method": "SHA256 exact bytes; canonical JSON digests also recorded in results",
            "files": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in files},
            "canonical_input_sha256": digest(inputs), "canonical_results_sha256": digest(results),
            "canonical_source_ledger_sha256": digest(sources),
            "canonical_handoffs_sha256": digest(handoffs),
            "human_approval": "NOT_GRANTED", "recordkeeping_certification": "NOT_CLAIMED"}


def validate_handoffs(handoffs, inputs, sources):
    if (handoffs["research_approval"] != "NOT_GRANTED" or handoffs["communication_sent"]
            or handoffs["trade_or_voting_authority"] or handoffs["status"] != "NEEDS_DATA"):
        raise ValueError("handoff must remain a proposed research packet")
    if handoffs["information_cutoff"] != inputs["information_cutoff"]:
        raise ValueError("handoff and portfolio information cutoffs differ")
    source_ids = {s["id"] for s in sources["sources"]}
    fact = handoffs["nature_handoff"]["fact"]
    if fact["source_id"] not in source_ids or not fact["locator"]:
        raise ValueError("nature evidence needs a registered source locator")
    previous = date.fromisoformat(inputs["information_cutoff"])
    for milestone in handoffs["stewardship_handoff"]["milestones"]:
        due = date.fromisoformat(milestone["due_date"])
        if due <= previous or milestone["status"] != "PROPOSED":
            raise ValueError("milestones must be ordered future proposals")
        previous = due


def check():
    inputs = json.loads((HERE / "inputs.json").read_text())
    sources = json.loads((HERE / "sources.json").read_text())
    expected = json.loads((HERE / "results.json").read_text())
    handoffs = json.loads((HERE / "handoffs.json").read_text())
    actual = calculate(inputs, sources)
    if actual != expected:
        raise SystemExit("results.json differs from read-only recomputation")
    recorded = json.loads((HERE / "provenance.json").read_text())
    if provenance(inputs, sources, expected, handoffs) != recorded:
        raise SystemExit("provenance.json has stale file or canonical hashes")
    for metric in ("financed_emissions_attribution", "waci_attribution"):
        for scope in SCOPES:
            if not math.isclose(actual[metric][scope]["reconciliation_residual"], 0, abs_tol=1e-9):
                raise SystemExit("attribution does not reconcile")
    validate_handoffs(handoffs, inputs, sources)
    print("Integrated portfolio: inputs, source ledger, results and handoffs verified; two scopes reconcile.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed results without writing")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        inputs = json.loads((HERE / "inputs.json").read_text())
        sources = json.loads((HERE / "sources.json").read_text())
        print(json.dumps(calculate(inputs, sources), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
